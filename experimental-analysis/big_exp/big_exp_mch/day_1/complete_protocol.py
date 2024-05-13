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
    "protocolName": "Burden_12_27_2023",
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
        if cell_volume > 20:
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
        start_point = plate_2[str(letters[row-1]) + str(column)]
        p20.transfer(iptg_volume, iptg_location, start_point, touch_tip=True, reverse=True)
        p20.drop_tip()


    protocol.home()

final_positions = {}
iptg_volume = 0
# ---------- Appended Data
final_positions = {'D7': ['B2', 'MCH10', 'RBS0.125', 27.11051958204659, 166.88948041795342], 'B9': ['B2', 'MCH10', 'RBS0.125', 27.11051958204659, 166.88948041795342], 'C9': ['C2', 'MCH25', 'RBS0.125', 27.54034006747656, 166.45965993252344], 'E3': ['C2', 'MCH25', 'RBS0.125', 27.54034006747656, 166.45965993252344], 'D6': ['D2', 'MCH50', 'RBS0.125', 29.18556504149148, 164.8144349585085], 'C2': ['D2', 'MCH50', 'RBS0.125', 29.18556504149148, 164.8144349585085], 'F6': ['E2', 'MCH75', 'RBS0.125', 23.978118697819077, 170.02188130218093], 'B4': ['E2', 'MCH75', 'RBS0.125', 23.978118697819077, 170.02188130218093], 'G7': ['B3', 'MCH10', 'RBS0.25', 47.95623830898639, 146.0437616910136], 'F11': ['B3', 'MCH10', 'RBS0.25', 47.95623830898639, 146.0437616910136], 'B7': ['C3', 'MCH25', 'RBS0.25', 25.587127055979188, 168.41287294402082], 'E7': ['C3', 'MCH25', 'RBS0.25', 25.587127055979188, 168.41287294402082], 'E6': ['D3', 'MCH50', 'RBS0.25', 27.524180029883194, 166.47581997011682], 'G11': ['D3', 'MCH50', 'RBS0.25', 27.524180029883194, 166.47581997011682], 'D9': ['E3', 'MCH75', 'RBS0.25', 27.252294574103352, 166.74770542589664], 'E10': ['E3', 'MCH75', 'RBS0.25', 27.252294574103352, 166.74770542589664], 'E2': ['B4', 'MCH10', 'RBS0.5', 29.70310288118569, 164.29689711881431], 'C11': ['B4', 'MCH10', 'RBS0.5', 29.70310288118569, 164.29689711881431], 'F2': ['C4', 'MCH25', 'RBS0.5', 29.816403353867976, 164.18359664613203], 'C3': ['C4', 'MCH25', 'RBS0.5', 29.816403353867976, 164.18359664613203], 'F5': ['D4', 'MCH50', 'RBS0.5', 31.9490478950477, 162.0509521049523], 'G5': ['D4', 'MCH50', 'RBS0.5', 31.9490478950477, 162.0509521049523], 'D2': ['E4', 'MCH75', 'RBS0.5', 26.056221726102113, 167.9437782738979], 'G10': ['E4', 'MCH75', 'RBS0.5', 26.056221726102113, 167.9437782738979], 'D10': ['B5', 'MCH10', 'RBS1', 50.70400138857561, 143.29599861142438], 'B3': ['B5', 'MCH10', 'RBS1', 50.70400138857561, 143.29599861142438], 'F3': ['C5', 'MCH25', 'RBS1', 27.411574281776502, 166.5884257182235], 'B10': ['C5', 'MCH25', 'RBS1', 27.411574281776502, 166.5884257182235], 'E8': ['D5', 'MCH50', 'RBS1', 27.141898029248633, 166.85810197075136], 'D4': ['D5', 'MCH50', 'RBS1', 27.141898029248633, 166.85810197075136], 'G3': ['E5', 'MCH75', 'RBS1', 21.633394782203748, 172.36660521779626], 'G9': ['E5', 'MCH75', 'RBS1', 21.633394782203748, 172.36660521779626], 'B8': ['B6', 'MCH10', 'RBS2', 30.85605437999492, 163.14394562000507], 'F4': ['B6', 'MCH10', 'RBS2', 30.85605437999492, 163.14394562000507], 'B6': ['C6', 'MCH25', 'RBS2', 26.408334433225058, 167.59166556677494], 'F7': ['C6', 'MCH25', 'RBS2', 26.408334433225058, 167.59166556677494], 'E11': ['D6', 'MCH50', 'RBS2', 25.685215292817986, 168.314784707182], 'C4': ['D6', 'MCH50', 'RBS2', 25.685215292817986, 168.314784707182], 'D11': ['E6', 'MCH75', 'RBS2', 22.767573200910675, 171.23242679908932], 'C6': ['E6', 'MCH75', 'RBS2', 22.767573200910675, 171.23242679908932], 'C10': ['B7', 'MCH10', 'RBS4', 41.359085216306774, 152.64091478369323], 'G4': ['B7', 'MCH10', 'RBS4', 41.359085216306774, 152.64091478369323], 'D8': ['C7', 'MCH25', 'RBS4', 26.800684459150148, 167.19931554084985], 'C5': ['C7', 'MCH25', 'RBS4', 26.800684459150148, 167.19931554084985], 'E5': ['D7', 'MCH50', 'RBS4', 28.933500778248373, 165.06649922175163], 'D5': ['D7', 'MCH50', 'RBS4', 28.933500778248373, 165.06649922175163], 'C8': ['E7', 'MCH75', 'RBS4', 35.82979596918771, 158.1702040308123], 'G6': ['E7', 'MCH75', 'RBS4', 35.82979596918771, 158.1702040308123], 'B2': ['blank', 'blank', 'blank', 0, 194], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B11': ['blank', 'blank', 'blank', 0, 194], 'C7': ['blank', 'blank', 'blank', 0, 194], 'D3': ['blank', 'blank', 'blank', 0, 194], 'E4': ['blank', 'blank', 'blank', 0, 194], 'E9': ['blank', 'blank', 'blank', 0, 194], 'F8': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194], 'G8': ['blank', 'blank', 'blank', 0, 194]}
iptg_volume = 6
