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
    "protocolName": "Burden_12_22_23",
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
final_positions = {'D6': ['B2', 'GFP10', 'RBS0.125', 24.802324968961695, 169.1976750310383], 'C10': ['B2', 'GFP10', 'RBS0.125', 24.802324968961695, 169.1976750310383], 'G8': ['C2', 'GFP25', 'RBS0.125', 22.47302474917753, 171.52697525082246], 'D9': ['C2', 'GFP25', 'RBS0.125', 22.47302474917753, 171.52697525082246], 'D4': ['D2', 'GFP50', 'RBS0.125', 27.45972099677744, 166.54027900322257], 'D5': ['D2', 'GFP50', 'RBS0.125', 27.45972099677744, 166.54027900322257], 'G9': ['E2', 'GFP75', 'RBS0.125', 30.475110891091468, 163.52488910890852], 'D2': ['E2', 'GFP75', 'RBS0.125', 30.475110891091468, 163.52488910890852], 'B3': ['B3', 'GFP10', 'RBS0.25', 20.6522235401309, 173.3477764598691], 'E2': ['B3', 'GFP10', 'RBS0.25', 20.6522235401309, 173.3477764598691], 'F5': ['C3', 'GFP25', 'RBS0.25', 21.031927614483102, 172.9680723855169], 'C8': ['C3', 'GFP25', 'RBS0.25', 21.031927614483102, 172.9680723855169], 'B4': ['D3', 'GFP50', 'RBS0.25', 25.37943915759807, 168.62056084240191], 'D7': ['D3', 'GFP50', 'RBS0.25', 25.37943915759807, 168.62056084240191], 'C3': ['E3', 'GFP75', 'RBS0.25', 30.278372877739713, 163.7216271222603], 'F10': ['E3', 'GFP75', 'RBS0.25', 30.278372877739713, 163.7216271222603], 'F9': ['B4', 'GFP10', 'RBS0.5', 23.42717186429252, 170.57282813570748], 'B11': ['B4', 'GFP10', 'RBS0.5', 23.42717186429252, 170.57282813570748], 'G11': ['C4', 'GFP25', 'RBS0.5', 20.60685456366883, 173.39314543633117], 'B9': ['C4', 'GFP25', 'RBS0.5', 20.60685456366883, 173.39314543633117], 'G6': ['D4', 'GFP50', 'RBS0.5', 25.50364527776358, 168.49635472223642], 'C9': ['D4', 'GFP50', 'RBS0.5', 25.50364527776358, 168.49635472223642], 'G4': ['E4', 'GFP75', 'RBS0.5', 19.822992513823134, 174.17700748617688], 'F11': ['E4', 'GFP75', 'RBS0.5', 19.822992513823134, 174.17700748617688], 'C2': ['B5', 'GFP10', 'RBS1', 24.828585152567776, 169.17141484743223], 'C6': ['B5', 'GFP10', 'RBS1', 24.828585152567776, 169.17141484743223], 'B7': ['C5', 'GFP25', 'RBS1', 18.249495140075457, 175.75050485992455], 'E9': ['C5', 'GFP25', 'RBS1', 18.249495140075457, 175.75050485992455], 'G5': ['D5', 'GFP50', 'RBS1', 24.504283161964345, 169.49571683803566], 'F6': ['D5', 'GFP50', 'RBS1', 24.504283161964345, 169.49571683803566], 'F2': ['E5', 'GFP75', 'RBS1', 21.753803269454018, 172.246196730546], 'F3': ['E5', 'GFP75', 'RBS1', 21.753803269454018, 172.246196730546], 'G7': ['B6', 'GFP10', 'RBS2', 29.590661957039284, 164.4093380429607], 'C4': ['B6', 'GFP10', 'RBS2', 29.590661957039284, 164.4093380429607], 'C5': ['C6', 'GFP25', 'RBS2', 19.308851308806805, 174.6911486911932], 'B2': ['C6', 'GFP25', 'RBS2', 19.308851308806805, 174.6911486911932], 'E8': ['D6', 'GFP50', 'RBS2', 26.603062057401182, 167.3969379425988], 'E5': ['D6', 'GFP50', 'RBS2', 26.603062057401182, 167.3969379425988], 'C7': ['E6', 'GFP75', 'RBS2', 21.328422109151145, 172.67157789084885], 'D10': ['E6', 'GFP75', 'RBS2', 21.328422109151145, 172.67157789084885], 'E11': ['B7', 'GFP10', 'RBS4', 23.415477366991134, 170.58452263300887], 'D8': ['B7', 'GFP10', 'RBS4', 23.415477366991134, 170.58452263300887], 'B6': ['C7', 'GFP25', 'RBS4', 19.277105846322616, 174.72289415367737], 'E3': ['C7', 'GFP25', 'RBS4', 19.277105846322616, 174.72289415367737], 'G10': ['D7', 'GFP50', 'RBS4', 21.78411412397232, 172.21588587602767], 'G3': ['D7', 'GFP50', 'RBS4', 21.78411412397232, 172.21588587602767], 'F8': ['E7', 'GFP75', 'RBS4', 20.49877750300502, 173.50122249699498], 'D3': ['E7', 'GFP75', 'RBS4', 20.49877750300502, 173.50122249699498], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B8': ['blank', 'blank', 'blank', 0, 194], 'B10': ['blank', 'blank', 'blank', 0, 194], 'C11': ['blank', 'blank', 'blank', 0, 194], 'D11': ['blank', 'blank', 'blank', 0, 194], 'E4': ['blank', 'blank', 'blank', 0, 194], 'E6': ['blank', 'blank', 'blank', 0, 194], 'E7': ['blank', 'blank', 'blank', 0, 194], 'E10': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'F7': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194]}
iptg_volume = 6
