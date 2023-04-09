from opentrons import protocol_api
import math

metadata = {
    'protocolName': 'PCR Amplification of Adapters',
    'author': 'Ashir Borah <ashir.borah@ucsf.edu>',
    'description': 'Polymerase and adapters thermocycling using a 96 well plate and thermocycler with a mastermix.',
    'apiLevel': '2.13'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    temp_mod = protocol.load_module('temperature module gen2', '4')
    thermoblock = temp_mod.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        label="Temperature_Controlled_Stocks",
    )
    plate_96_well_with_inserts = protocol.load_labware('nest_96_wellplate_200ul_flat', 1, '96_Well_Insert_Plate')
    tiprack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 2, '200µL_Tip_Rack')
    tiprack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 3, '200µL_Tip_Rack')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 5, '20µL_Tip_Rack')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6, '20µL_Tip_Rack')

    thermocycler = protocol.load_module('thermocycler')
    tc_plate = thermocycler.load_labware('nest_96_wellplate_200ul_flat', 'Thermocycler_Plate')

    # Pipettes
    p200 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_200ul_1, tiprack_200ul_2])
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])


    # Reagents
    polymerase = thermoblock.wells_by_name()['A1']
    adapter_forward = thermoblock.wells_by_name()['A2']
    adapter_reverse = thermoblock.wells_by_name()['A3']
    water = thermoblock.wells_by_name()['A4']
    mastermix = thermoblock.wells_by_name()['B1']

    # Thermoblock temperature
    temp_mod.set_temperature(4)
    temp_mod.status  # 'holding at target'

    # Wells used for cloning
    wells_used_for_cloning = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']

    # assert that there are no duplicate wells
    assert len(wells_used_for_cloning) == len(set(wells_used_for_cloning)), 'Duplicate wells found in wells_used_for_cloning'

    # Prepare mastermix
    ## Add an additional 15% to the mastermix volume to account for pipette error
    total_wells = math.ceil(len(wells_used_for_cloning) * 1.15)
    p200.transfer(total_wells*10, polymerase, mastermix, new_tip='always')
    p200.transfer(total_wells*2, adapter_forward, mastermix, new_tip='always')
    p200.transfer(total_wells*2, adapter_reverse, mastermix, new_tip='always')
    p200.transfer(total_wells*5, water, mastermix)
    p200.pick_up_tip()
    p200.mix(10, total_wells*5, mastermix)
    p200.touch_tip(mastermix)
    p200.blow_out()
    p200.drop_tip()

    ## Transfer mastermix to wells
    if thermocycler.lid_position != 'open':
        thermocycler.open_lid()

    ## Maybe use just wells() instead of wells_by_name()?
    p200.distribute(19, mastermix, [tc_plate.wells() for wells in wells_used_for_cloning])

    # Transfer mastermix and insert
    for well_name in wells_used_for_cloning:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.pick_up_tip()
        p20.aspirate(1, well)
        p20.dispense(1, tc_plate.wells_by_name()[well_name])
        p20.blow_out()
        p20.drop_tip()

    # Thermocycling settings
    initial_denaturation = [{'temperature': 98, 'hold_time_seconds': 30}]
    cycling_steps = [
        {'temperature': 98, 'hold_time_seconds': 15},
        {'temperature': 57, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 15},
    ]
    final_elongation = [{'temperature': 72, 'hold_time_seconds': 60}]
    final_hold = [{'temperature': 4, 'hold_time_seconds': None}]

    # Run thermocycling program
    protocol.comment('Starting thermocycling...')
    if thermocycler.lid_position != 'closed':
        thermocycler.close_lid()
    thermocycler.set_lid_temperature(105)
    thermocycler.execute_profile(steps=initial_denaturation, repetitions=1, block_max_volume=20)
    thermocycler.execute_profile(steps=cycling_steps, repetitions=10, block_max_volume=20)
    thermocycler.execute_profile(steps=final_elongation, repetitions=1, block_max_volume=20)
    thermocycler.deactivate_lid()
    thermocycler.set_block_temperature(4)
    protocol.comment('Thermocycling complete.')