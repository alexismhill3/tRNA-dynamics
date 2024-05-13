from opentrons import protocol_api, types
from opentrons.protocol_api.labware import OutOfTipsError, Well, Labware, next_available_tip
from opentrons.protocol_api.instrument_context import InstrumentContext
from typing import Any, AnyStr, List, Dict, Optional, Union, Tuple, TYPE_CHECKING
from opentrons.commands.publisher import CommandPublisher, publish, publish_context
from opentrons.commands import commands as cmds
import logging
import logging

from contextlib import suppress

# ---------- Protocol Setup

# metadata
metadata = {
    "protocolName": "Burden_12_29_2023",
    "author": "Cameron <croots@utexas.edu>",
    "description": "Burden experiment on all strains",
    "apiLevel": "2.13"
}

# requirements
requirements = {"robotType": "OT-2"}

# ---------- Custom Systems

class CustomPipette(InstrumentContext):
    """This is a wrapper to the Opentrons pipette classes that does two things.
    First, it changes the out of tips behavior to wait for you to replace the tips.
    Secondly, it enables multichannels to pick up individual tips.
    
    :param parent_instance: The parent pipette instance
    :param parent_protocol: The protocol context spawning this pipette"""
    def __init__(self, parent_instance, parent_protocol):
        vars(self).update(vars(parent_instance))
        self.protocol = parent_protocol

        if self.mount == 'left':
            checked_mount = types.Mount.LEFT
        if self.mount == 'right':
            checked_mount = types.Mount.RIGHT

        self.protocol._instruments[checked_mount] = self
        
    def pick_up_tip(self,
                    number: Optional[int] = 1,
                    **kwargs) -> InstrumentContext:
        """Wrapper of the pick up tip function. Prompts operator to refill tips and enables less-than-max 
        tip collection by multichannel pipettes.
        
        :param number: number of tips to pick up (defaults to 1, errors >1 on single channels)
        
        See super().pick_up_tip for other paramaters"""
        
        # Bypass everything if operator tells speifically where to pick up a tip
        if kwargs.get('location'): # if location arg exists and is not none
            super().pick_up_tip(**kwargs)
            return self
        
        # Sanity checking for multichannels
        if not isinstance(number, int) or not 0 < number <= self.channels:
            raise ValueError(f"Invalid value for number of pipette channels: {number}")
        # @TODO: Check for deck conflicts when multichannels are picking up less than the max number of tips.
        
        # Check to see if there is enought tips for the pipette. If not, have the tips replaced.
        next_tip = None
        try:
            next_tip =  self.next_tip(number)
        except OutOfTipsError:
            input(f"Please replace the following tip boxes then press enter: {self.tip_racks}")
            super().reset_tipracks()
            
        if not next_tip:
            next_tip = self.next_tip(number)

        # Set the depression strength
        pipette_type = self.model
        if pipette_type == "p20_multi_gen2":
            pickup_current = 0.075
        else:
            pickup_current = 1
        pickup_current = pickup_current*number # of tips
        if self.mount == 'left':
            mountpoint = types.Mount.LEFT
        else:
            mountpoint = types.Mount.RIGHT

        # The doccumented way to actually change the pick up voltage is outdated
        # self.protocol._hw_manager.hardware._attached_instruments[mountpoint].update_config_item('pickupCurrent', pickup_current)
        
        # Overwrite the tip location (for multichannel pick ups less than max)
        kwargs['location'] = next_tip
        
        super().pick_up_tip(**kwargs)
        
        return self
    
    def next_tip(self, number_of_tips: int) -> Well:
        ''''''
        # Determine where the tips should be picked up from.
        target_well = None
        for tip_rack in self.tip_racks:
            truth_table = [[well.has_tip for well in column] for column in tip_rack.columns()]
            for i1, column in enumerate(tip_rack.columns()):
                for i2, _ in enumerate(column[::-1]):
                    well_index = 7-i2
                    if well_index+number_of_tips > 8:
                        continue
                    if all(truth_table[i1][well_index:well_index+number_of_tips]):
                        target_well = column[well_index]
                        break
                if target_well:
                    break
            if target_well:
                break
        else:
            raise OutOfTipsError
        return target_well
    
    def get_available_volume(self)-> float:
        "Returns the available space in the tip OR lower(max volume next tip, max volume pipette)"
        if self.has_tip:
            return self.max_volume - self.current_volume
        else:
            next_tip = self.next_tip(1)
            return min([next_tip.max_volume, self.max_volume])
        
    def get_current_volume(self)-> float:
        return self.current_volume
        
    def transfer(self, volume, source, destination, touch_tip=False, blow_out=False, reverse=False):
        aspiration_volume = volume
        despense_volume = volume

        if self.get_current_volume():
            self.dispense(self.get_current_volume(), source)

        if reverse and volume*1.1 <= self.get_available_volume():
            aspiration_volume = volume*1.1
        if aspiration_volume > self.get_available_volume():
            raise ValueError(f"Volume {aspiration_volume} is too large for the current tip. Available volume is {self.get_available_volume()}")

        self.aspirate(aspiration_volume, source)
        self.dispense(despense_volume, destination)
        if blow_out:
            self.blow_out(destination)
        if touch_tip:
            self.touch_tip(destination)

        return self.get_current_volume()



# ---------- Actual Protocol 

# protocol run function
def run(protocol: protocol_api.ProtocolContext):
    protocol.home()
    # labware

    plate_1 = protocol.load_labware('nest_96_wellplate_200ul_flat', 4)
    plate_2 = protocol.load_labware('nest_96_wellplate_200ul_flat', 5)

    reagent_reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 6)
    lb_location = reagent_reservoir['A1'].bottom(5)
    iptg_location = reagent_reservoir['A3'].bottom(5)


    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 9)

    p300 = protocol.load_instrument('p300_single', "left", tip_racks=[tiprack_300])
    p20 = protocol.load_instrument('p20_multi_gen2', "right", tip_racks=[tiprack_20])

    p300 = CustomPipette(p300, protocol)
    p20 = CustomPipette(p20, protocol)

    # Set up dictionaries for cell volumes and LB
    lb_instructions = [(value[4], key)
                        for key, value in final_positions.items()] # Volume, Destination
    cell_instructions = [(value[3], value[0], key)
                         for key, value in final_positions.items()]  # Volume, Source, Destination
    locations = list(final_positions.keys())

    
    # Add LB
    p300.pick_up_tip(1)
    first_time = True
    for lb_volume, destination in lb_instructions:  # Add LB to all relevant wells
        p300.transfer(lb_volume, lb_location, plate_2[destination], touch_tip=True, reverse=True)
        if first_time:
            first_time = False
            p300.drop_tip()
            p300.pick_up_tip()
    p300.drop_tip()
    
    # Add Cells
    for cell_volume, source, destination in cell_instructions:  # Add cells to all releveant wells
        if cell_volume > 10:
            pipette = p300
        else:
            pipette = p20
        pipette.pick_up_tip(1)

        if source == "blank":
            source = lb_location
        else:
            source = plate_1[source]

        pipette.transfer(cell_volume,
                         source,
                         plate_2[destination],
                         touch_tip=True,
                         reverse=True)
        pipette.drop_tip()

    # Induction
    column_occupancy = {n: [False]*12 for n in range(1, 13)} # Logic for tip quantity and where to induce first
    letters = "ABCDEFGH"
    for location in locations:
        column_occupancy[int(location[1:])][letters.index(location[0])] = True
    for column in column_occupancy.keys():
        try:
            start_row = next(i for i, x in enumerate(column_occupancy[column]) if x)
            num_tips = sum(column_occupancy[column])
        except:
            start_row = 0
            num_tips = 0
        column_occupancy[column] = (start_row, num_tips)
        
    for column, (row, num_tips) in column_occupancy.items():  # Induce all wells
        if num_tips == 0:
            continue
        p20.pick_up_tip(num_tips)
        start_point = plate_2[str(letters[row]) + str(column)]
        p20.transfer(iptg_volume, iptg_location, start_point, touch_tip=True, reverse=True)
        p20.drop_tip()


    protocol.home()

final_positions = {}
iptg_volume = 0
# ---------- Appended Data
final_positions = {'D9': ['B2', 'MCH10', 'RBS0.125', 19.998379328306406, 174.0016206716936], 'G6': ['B2', 'MCH10', 'RBS0.125', 19.998379328306406, 174.0016206716936], 'E7': ['C2', 'MCH25', 'RBS0.125', 16.6124850878012, 177.3875149121988], 'C8': ['C2', 'MCH25', 'RBS0.125', 16.6124850878012, 177.3875149121988], 'E3': ['D2', 'MCH50', 'RBS0.125', 17.14068551230489, 176.85931448769512], 'D4': ['D2', 'MCH50', 'RBS0.125', 17.14068551230489, 176.85931448769512], 'B4': ['E2', 'MCH75', 'RBS0.125', 17.33710455187554, 176.66289544812446], 'C10': ['E2', 'MCH75', 'RBS0.125', 17.33710455187554, 176.66289544812446], 'B2': ['B3', 'MCH10', 'RBS0.25', 34.70948976881548, 159.29051023118453], 'B3': ['B3', 'MCH10', 'RBS0.25', 34.70948976881548, 159.29051023118453], 'C2': ['C3', 'MCH25', 'RBS0.25', 18.412484867232777, 175.58751513276724], 'F10': ['C3', 'MCH25', 'RBS0.25', 18.412484867232777, 175.58751513276724], 'D7': ['D3', 'MCH50', 'RBS0.25', 17.75047677678299, 176.249523223217], 'B11': ['D3', 'MCH50', 'RBS0.25', 17.75047677678299, 176.249523223217], 'F5': ['E3', 'MCH75', 'RBS0.25', 15.973162697106568, 178.02683730289343], 'C7': ['E3', 'MCH75', 'RBS0.25', 15.973162697106568, 178.02683730289343], 'C6': ['B4', 'MCH10', 'RBS0.5', 18.492339975836575, 175.5076600241634], 'G11': ['B4', 'MCH10', 'RBS0.5', 18.492339975836575, 175.5076600241634], 'D8': ['C4', 'MCH25', 'RBS0.5', 16.653776480153905, 177.3462235198461], 'E11': ['C4', 'MCH25', 'RBS0.5', 16.653776480153905, 177.3462235198461], 'G8': ['D4', 'MCH50', 'RBS0.5', 20.32774951341294, 173.67225048658707], 'E10': ['D4', 'MCH50', 'RBS0.5', 20.32774951341294, 173.67225048658707], 'D3': ['E4', 'MCH75', 'RBS0.5', 17.394973377798788, 176.60502662220122], 'G9': ['E4', 'MCH75', 'RBS0.5', 17.394973377798788, 176.60502662220122], 'C5': ['B5', 'MCH10', 'RBS1', 16.3347670459662, 177.6652329540338], 'C3': ['B5', 'MCH10', 'RBS1', 16.3347670459662, 177.6652329540338], 'G3': ['C5', 'MCH25', 'RBS1', 15.870468138496438, 178.12953186150355], 'E6': ['C5', 'MCH25', 'RBS1', 15.870468138496438, 178.12953186150355], 'E4': ['D5', 'MCH50', 'RBS1', 17.32429642659391, 176.67570357340608], 'C9': ['D5', 'MCH50', 'RBS1', 17.32429642659391, 176.67570357340608], 'G7': ['E5', 'MCH75', 'RBS1', 14.752283626215007, 179.24771637378498], 'F11': ['E5', 'MCH75', 'RBS1', 14.752283626215007, 179.24771637378498], 'D5': ['B6', 'MCH10', 'RBS2', 15.177154005077304, 178.8228459949227], 'F9': ['B6', 'MCH10', 'RBS2', 15.177154005077304, 178.8228459949227], 'B10': ['C6', 'MCH25', 'RBS2', 15.157533857202207, 178.8424661427978], 'D2': ['C6', 'MCH25', 'RBS2', 15.157533857202207, 178.8424661427978], 'C4': ['D6', 'MCH50', 'RBS2', 17.466231303269346, 176.53376869673065], 'B9': ['D6', 'MCH50', 'RBS2', 17.466231303269346, 176.53376869673065], 'F6': ['E6', 'MCH75', 'RBS2', 16.00587000867707, 177.99412999132292], 'D10': ['E6', 'MCH75', 'RBS2', 16.00587000867707, 177.99412999132292], 'E9': ['B7', 'MCH10', 'RBS4', 14.683008707811135, 179.31699129218887], 'F8': ['B7', 'MCH10', 'RBS4', 14.683008707811135, 179.31699129218887], 'C11': ['C7', 'MCH25', 'RBS4', 14.237291542083108, 179.7627084579169], 'G10': ['C7', 'MCH25', 'RBS4', 14.237291542083108, 179.7627084579169], 'D11': ['D7', 'MCH50', 'RBS4', 15.891977063102958, 178.10802293689704], 'F7': ['D7', 'MCH50', 'RBS4', 15.891977063102958, 178.10802293689704], 'B5': ['E7', 'MCH75', 'RBS4', 22.654848357917466, 171.34515164208253], 'G5': ['E7', 'MCH75', 'RBS4', 22.654848357917466, 171.34515164208253], 'B6': ['blank', 'blank', 'blank', 0, 194], 'B7': ['blank', 'blank', 'blank', 0, 194], 'B8': ['blank', 'blank', 'blank', 0, 194], 'D6': ['blank', 'blank', 'blank', 0, 194], 'E2': ['blank', 'blank', 'blank', 0, 194], 'E5': ['blank', 'blank', 'blank', 0, 194], 'E8': ['blank', 'blank', 'blank', 0, 194], 'F2': ['blank', 'blank', 'blank', 0, 194], 'F3': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194], 'G4': ['blank', 'blank', 'blank', 0, 194]}
iptg_volume = 6
