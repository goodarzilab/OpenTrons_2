from opentrons import protocol_api
import math

metadata = {
    'protocolName': 'Adapters',
    'author': 'Ashir Borah <ashir.borah@ucsf.edu>',
    'description': 'Adapter digestion of inserts',
    'apiLevel': '2.13'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    temp_mod = protocol.load_module('temperature module gen2', '4')
    thermoblock = temp_mod.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        label="Temperature-Controlled Stocks",
    )
    plate_96_well_with_inserts = protocol.load_labware('nest_96_wellplate_200ul_flat', 1, '96 Well Insert Plate')
    tiprack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 2, '200µL Tip Rack')
    tiprack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 3, '200µL Tip Rack')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 5, '20µL Tip Rack')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6, '20µL Tip Rack')

    thermocycler = protocol.load_module('thermocycler')
    tc_plate = thermocycler.load_labware('nest_96_wellplate_200ul_flat')

    # Pipettes
    p200 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_200ul_1, tiprack_200ul_2])
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])


    # Reagents
    fd_buffer = thermoblock.wells_by_name()['C1']
    bpu1102_enzyme = thermoblock.wells_by_name()['C2']
    bstXI_enzyme = thermoblock.wells_by_name()['C3']

    # Thermoblock temperature
    temp_mod.set_temperature(4)
    temp_mod.status  # 'holding at target'

    # Wells used for cloning
    wells_used_for_cloning = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']

    # assert that there are no duplicate wells
    assert len(wells_used_for_cloning) == len(set(wells_used_for_cloning)), 'Duplicate wells found in wells_used_for_cloning'

    ## Transfer materials to wells
    if thermocycler.lid_position != 'open':
        thermocycler.open_lid()
        
    # We digest in steps
    # Transfer first enzyme to thermocycler plate
    for well_name in wells_used_for_cloning:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.transfer(2, fd_buffer, well, new_tip='always')
        p20.transfer(1, bpu1102_enzyme, well, new_tip='always')
        p20.pick_up_tip()
        p20.aspirate(16, well)
        p20.dispense(16, tc_plate.wells_by_name()[well_name])
        p20.mix(10, 10, tc_plate.wells_by_name()[well_name])
        p20.touch_tip()
        p20.blow_out()
        p20.drop_tip()

    # Thermocycling settings
    incubate = [{'temperature': 37, 'hold_time_seconds': 3600},
                {'temperature': 80, 'hold_time_seconds': 300}]
    # Run thermocycling program
    protocol.comment('Starting thermocycling...')
    if thermocycler.lid_position != 'closed':
        thermocycler.close_lid()
    thermocycler.set_lid_temperature(105)
    thermocycler.execute_profile(steps=incubate, repetitions=1, block_max_volume=20)
    thermocycler.deactivate_lid()
    protocol.comment('Digestion 1 thermocycling completed. Starting second digestion.')
    
    ## Second enzyme
    if thermocycler.lid_position != 'open':
        thermocycler.open_lid()
        
    for well_name in wells_used_for_cloning:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.pick_up_tip()
        p20.aspirate(1, bstXI_enzyme)
        p20.dispense(1, tc_plate.wells_by_name()[well_name])
        p20.mix(5, 10, tc_plate.wells_by_name()[well_name])
        p20.touch_tip()
        p20.blow_out()
        p20.drop_tip()
        
        
    protocol.comment('Starting second thermocycling...')
    if thermocycler.lid_position != 'closed':
        thermocycler.close_lid()
    thermocycler.set_lid_temperature(105)
    thermocycler.execute_profile(steps=incubate, repetitions=1, block_max_volume=20)
    thermocycler.deactivate_lid()
    thermocycler.set_block_temperature(4)
    protocol.comment('Thermocycling complete for PCR adapter digestion.')