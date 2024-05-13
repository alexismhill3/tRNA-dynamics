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
    "protocolName": "Burden_12_20_23",
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


    p300.pick_up_tip(1)
    for lb_volume, destination in lb_instructions:  # Add LB to all relevant wells
        p300.transfer(lb_volume, lb_location, plate_2[destination], touch_tip=True, reverse=True)
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
        start_point = plate_2[str(letters[row-1]) + str(column)]
        p20.transfer(iptg_volume, iptg_location, start_point, touch_tip=True, reverse=True)
        p20.drop_tip()


    protocol.home()

final_positions = {}
iptg_volume = 0
# ---------- Appended Data
final_positions = {'D7': ['B2', 'GFP10', 'RBS0.125', 16.484034820387237, 177.51596517961275], 'E9': ['B2', 'GFP10', 'RBS0.125', 16.484034820387237, 177.51596517961275], 'D6': ['C2', 'GFP25', 'RBS0.125', 15.157534678396281, 178.84246532160373], 'B6': ['C2', 'GFP25', 'RBS0.125', 15.157534678396281, 178.84246532160373], 'E5': ['D2', 'GFP50', 'RBS0.125', 17.42729169118082, 176.5727083088192], 'B10': ['D2', 'GFP50', 'RBS0.125', 17.42729169118082, 176.5727083088192], 'D11': ['E2', 'GFP75', 'RBS0.125', 16.647865131322867, 177.35213486867713], 'B5': ['E2', 'GFP75', 'RBS0.125', 16.647865131322867, 177.35213486867713], 'B11': ['B3', 'GFP10', 'RBS0.25', 14.888088515698387, 179.1119114843016], 'F3': ['B3', 'GFP10', 'RBS0.25', 14.888088515698387, 179.1119114843016], 'C3': ['C3', 'GFP25', 'RBS0.25', 15.162434228225004, 178.837565771775], 'B7': ['C3', 'GFP25', 'RBS0.25', 15.162434228225004, 178.837565771775], 'C6': ['D3', 'GFP50', 'RBS0.25', 14.780178584485679, 179.21982141551433], 'C8': ['D3', 'GFP50', 'RBS0.25', 14.780178584485679, 179.21982141551433], 'C5': ['E3', 'GFP75', 'RBS0.25', 16.177011208889542, 177.82298879111045], 'G2': ['E3', 'GFP75', 'RBS0.25', 16.177011208889542, 177.82298879111045], 'B8': ['B4', 'GFP10', 'RBS0.5', 14.368139322107062, 179.63186067789294], 'E4': ['B4', 'GFP10', 'RBS0.5', 14.368139322107062, 179.63186067789294], 'F8': ['C4', 'GFP25', 'RBS0.5', 14.177042519250039, 179.82295748074995], 'D8': ['C4', 'GFP25', 'RBS0.5', 14.177042519250039, 179.82295748074995], 'E11': ['D4', 'GFP50', 'RBS0.5', 14.04122495885724, 179.95877504114276], 'G8': ['D4', 'GFP50', 'RBS0.5', 14.04122495885724, 179.95877504114276], 'B9': ['E4', 'GFP75', 'RBS0.5', 12.91243699667013, 181.08756300332988], 'D5': ['E4', 'GFP75', 'RBS0.5', 12.91243699667013, 181.08756300332988], 'F6': ['B5', 'GFP10', 'RBS1', 17.260539687949443, 176.73946031205057], 'D4': ['B5', 'GFP10', 'RBS1', 17.260539687949443, 176.73946031205057], 'C4': ['C5', 'GFP25', 'RBS1', 13.621200957373574, 180.37879904262644], 'C7': ['C5', 'GFP25', 'RBS1', 13.621200957373574, 180.37879904262644], 'E8': ['D5', 'GFP50', 'RBS1', 15.559824038689973, 178.44017596131002], 'C9': ['D5', 'GFP50', 'RBS1', 15.559824038689973, 178.44017596131002], 'E3': ['E5', 'GFP75', 'RBS1', 15.361074565601413, 178.63892543439857], 'E2': ['E5', 'GFP75', 'RBS1', 15.361074565601413, 178.63892543439857], 'F7': ['B6', 'GFP10', 'RBS2', 15.167336946557155, 178.83266305344284], 'D2': ['B6', 'GFP10', 'RBS2', 15.167336946557155, 178.83266305344284], 'G11': ['C6', 'GFP25', 'RBS2', 14.385767887360423, 179.61423211263957], 'B4': ['C6', 'GFP25', 'RBS2', 14.385767887360423, 179.61423211263957], 'F5': ['D6', 'GFP50', 'RBS2', 14.211407804175272, 179.78859219582472], 'G9': ['D6', 'GFP50', 'RBS2', 14.211407804175272, 179.78859219582472], 'D9': ['E6', 'GFP75', 'RBS2', 14.198501476331673, 179.80149852366833], 'G3': ['E6', 'GFP75', 'RBS2', 14.198501476331673, 179.80149852366833], 'F11': ['B7', 'GFP10', 'RBS4', 13.781297676024332, 180.21870232397566], 'E6': ['B7', 'GFP10', 'RBS4', 13.781297676024332, 180.21870232397566], 'D3': ['C7', 'GFP25', 'RBS4', 13.023589111341503, 180.9764108886585], 'C2': ['C7', 'GFP25', 'RBS4', 13.023589111341503, 180.9764108886585], 'B2': ['D7', 'GFP50', 'RBS4', 14.164197231724573, 179.8358027682754], 'C11': ['D7', 'GFP50', 'RBS4', 14.164197231724573, 179.8358027682754], 'B3': ['E7', 'GFP75', 'RBS4', 14.733746703467382, 179.26625329653262], 'E10': ['E7', 'GFP75', 'RBS4', 14.733746703467382, 179.26625329653262], 'C10': ['blank', 'blank', 'blank', 0, 194], 'D10': ['blank', 'blank', 'blank', 0, 194], 'E7': ['blank', 'blank', 'blank', 0, 194], 'F2': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'F9': ['blank', 'blank', 'blank', 0, 194], 'F10': ['blank', 'blank', 'blank', 0, 194], 'G4': ['blank', 'blank', 'blank', 0, 194], 'G5': ['blank', 'blank', 'blank', 0, 194], 'G6': ['blank', 'blank', 'blank', 0, 194], 'G7': ['blank', 'blank', 'blank', 0, 194], 'G10': ['blank', 'blank', 'blank', 0, 194]}
iptg_volume = 6
