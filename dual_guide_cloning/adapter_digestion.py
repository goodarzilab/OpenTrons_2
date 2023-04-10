AMOUNTS_TO_ADD = {
    'fd_buffer': 2,
    'bpu1102_enzyme': 1,
    'bstXI_enzyme': 1,
    'insert': 16,
}

TOTAL_RxN_VOL = 20

AMOUNTS_TO_ADD['water'] = TOTAL_RxN_VOL - sum(AMOUNTS_TO_ADD.values())

# Wells used for cloning
WELLS_USED_FOR_CLONING = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']



from opentrons import protocol_api
import math

metadata = {
    'protocolName': 'Adapters',
    'author': 'Ashir Borah <ashir.borah@ucsf.edu>',
    'description': 'Adapter digestion of inserts',
    'apiLevel': '2.13'
}

def run(protocol: protocol_api.ProtocolContext):

    protocol.comment('These are the stock solutions. Please ensure that they are at the correct slots before continuing.')
    protocol.comment(AMOUNTS_TO_ADD)

    if AMOUNTS_TO_ADD['water'] > 0:
        protocol.comment("Water is required. Please add water to the thermoblock at position C4 if you haven't already.")


    # Labware
    temp_mod = protocol.load_module('temperature module gen2', '4')
    thermoblock = temp_mod.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        label="Temperature-Controlled Stocks",
    )
    plate_96_well_with_inserts = protocol.load_labware('nest_96_wellplate_200ul_flat', 1, '96 Well Insert Plate')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 5, '20µL Tip Rack')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6, '20µL Tip Rack')

    thermocycler = protocol.load_module('thermocycler')
    tc_plate = thermocycler.load_labware('nest_96_wellplate_200ul_flat')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])


    # Reagents
    fd_buffer = thermoblock.wells_by_name()['C1']
    bpu1102_enzyme = thermoblock.wells_by_name()['C2']
    bstXI_enzyme = thermoblock.wells_by_name()['C3']
    if AMOUNTS_TO_ADD['water'] > 0:
        water = thermoblock.wells_by_name()['C4']

    # Thermoblock temperature
    temp_mod.set_temperature(4)
    temp_mod.status  # 'holding at target'

    # assert that there are no duplicate wells
    assert len(WELLS_USED_FOR_CLONING) == len(set(WELLS_USED_FOR_CLONING)), 'Duplicate wells found in wells_used_for_cloning'

    ## Transfer materials to wells
    if thermocycler.lid_position != 'open':
        thermocycler.open_lid()
        
    # We digest in steps
    # Transfer first enzyme to thermocycler plate
    for well_name in WELLS_USED_FOR_CLONING:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.transfer(AMOUNTS_TO_ADD['fd_buffer'], fd_buffer, well, new_tip='always')
        if AMOUNTS_TO_ADD['water'] > 0:
            p20.transfer(AMOUNTS_TO_ADD['water'], water, well)
        p20.transfer(AMOUNTS_TO_ADD['bpu1102_enzyme'], bpu1102_enzyme, well, new_tip='always')
        p20.pick_up_tip()
        p20.aspirate(AMOUNTS_TO_ADD['insert'], well)
        p20.dispense(AMOUNTS_TO_ADD['insert'], tc_plate.wells_by_name()[well_name])
        p20.mix(10, 10, tc_plate.wells_by_name()[well_name])
        p20.touch_tip()
        p20.blow_out()
        p20.drop_tip()

    # Thermocycling settings
    incubate = [{'temperature': 37, 'hold_time_minutes': 60},
                {'temperature': 80, 'hold_time_minutes': 5}]
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
        
    for well_name in WELLS_USED_FOR_CLONING:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.pick_up_tip()
        p20.aspirate(AMOUNTS_TO_ADD['bstXI_enzyme'], bstXI_enzyme)
        p20.dispense(AMOUNTS_TO_ADD['bstXI_enzyme'], tc_plate.wells_by_name()[well_name])
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