'''
Second Ligation of dual-guide Plasmid (Library)
Mix together the following. INCLUDE A NEGATIVE CONTROL OF WATER! Always add Ligase last.
Mix								    1X				Thermocycling
10x T4 ligase buffer				2 μl			Run 20x cycles of:
first-lig_product (≈ 10-14 ng/µl)	15 µl			{42 °C 5 min digestion		
pJR89 (use 150 ng total)			1 μl			16 °C 5 min ligation}
T4 DNA Ligase					    1 μl			Run 1x step of final:
BsmBI v2						    1 μl			60 °C 5 min denaturation
H2O		-> total 20 µl		        0 μl			best proceed immediately
Transform 2 µl of ligate directly into 20 µl NEB Stable E. coli. Spread 50 µl on Amp plate, grow o/n.

'''

AMOUNTS_TO_ADD = {
    'T4_ligase_buffer': 2,
    'first_lig_product': 15,
    'pJR89': 1,
    'T4_dna_ligase': 1,
    'BsmBI_v2': 1
}

TOTAL_RxN_VOL = 20
MASTERMIX_VOL = 5

assert TOTAL_RxN_VOL - sum(AMOUNTS_TO_ADD.values()) >= 0, 'Total volume of reagents is greater than total reaction volume'

AMOUNTS_TO_ADD['water'] = TOTAL_RxN_VOL - sum(AMOUNTS_TO_ADD.values())

from opentrons import protocol_api
import math

metadata = {
    'protocolName': 'Golden gate assembly',
    'author': 'Ashir Borah <ashir.borah@ucsf.edu>',
    'description': 'First ligation of the Golden Gate reaction',
    'apiLevel': '2.13'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    temp_mod = protocol.load_module('temperature module gen2', '4')
    thermoblock = temp_mod.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        label="Temperature-Controlled Stocks",
    )
    plate_96_well_with_first_ligation = protocol.load_labware('nest_96_wellplate_200ul_flat', 1, '96 Well Insert Plate')
    tiprack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 2, '200µL Tip Rack')
    tiprack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 3, '200µL Tip Rack')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 5, '20µL Tip Rack')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6, '20µL Tip Rack')
   
    thermocycler = protocol.load_module('thermocycler')
    plate_96_well_GG_assembled = thermocycler.load_labware('nest_96_wellplate_200ul_flat', label='Golden Gate Assembly plate')

    # Pipettes
    p200 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_200ul_1, tiprack_200ul_2])
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])

    ## Prompt to remind user that pJR85 needs to be digested
    protocol.comment('Make sure that the pJR85 is digested!!')

    # Reagents
    T4_ligase_buffer = thermoblock.wells_by_name()['A1']
    T4_dna_ligase = thermoblock.wells_by_name()['A2']
    pJR89 = thermoblock.wells_by_name()['A3']
    water = thermoblock.wells_by_name()['A4']
    BsmBI_v2_enzyme = thermoblock.wells_by_name()['A5']
    mastermix = thermoblock.wells_by_name()['B1']
    
    
    # Thermoblock temperature
    temp_mod.set_temperature(4)
    temp_mod.status  # 'holding at target'

    # Wells used for cloning
    wells_used_for_cloning = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
    
    # Prepare mastermix
    ## Add an additional 15% to the mastermix volume to account for pipette error
    total_wells = math.ceil(len(wells_used_for_cloning) * 1.15)
    p200.transfer(total_wells*AMOUNTS_TO_ADD['T4_ligase_buffer'], T4_ligase_buffer, mastermix, new_tip='always')
    p200.transfer(total_wells*AMOUNTS_TO_ADD['T4_dna_ligase'], T4_dna_ligase, mastermix, new_tip='always')
    p200.transfer(total_wells*AMOUNTS_TO_ADD['pJR89'], pJR89, mastermix, new_tip='always')
    p200.transfer(total_wells*AMOUNTS_TO_ADD['BsmBI_v2'], BsmBI_v2_enzyme, mastermix, new_tip='always')
    if AMOUNTS_TO_ADD['water'] > 0:
        p200.transfer(total_wells*AMOUNTS_TO_ADD['water'], water, mastermix)
    p200.pick_up_tip()
    p200.mix(10, total_wells*5, mastermix)
    p200.touch_tip(mastermix)
    p200.blow_out()
    p200.drop_tip()
    
     ## Transfer mastermix to wells
    if thermocycler.lid_position != 'open':
        thermocycler.open_lid()

    p200.distribute(MASTERMIX_VOL, mastermix, [plate_96_well_GG_assembled.wells() for wells in wells_used_for_cloning])

    # Transfer mastermix and insert
    for well_name in wells_used_for_cloning:
        well = plate_96_well_with_first_ligation.wells_by_name()[well_name]

        # Transfer insert
        p20.pick_up_tip()
        p20.aspirate(AMOUNTS_TO_ADD['first_lig_product'], well)
        p20.dispense(AMOUNTS_TO_ADD['first_lig_product'], plate_96_well_GG_assembled.wells_by_name()[well_name])
        p20.mix(5, AMOUNTS_TO_ADD['first_lig_product']/2, plate_96_well_GG_assembled.wells_by_name()[well_name])
        p20.touch_tip(plate_96_well_GG_assembled.wells_by_name()[well_name])
        p20.blow_out()
        p20.drop_tip()
        
    # Thermocycling settings
    cycling_steps = [
        {'temperature': 42, 'hold_time_minutes': 5},
        {'temperature': 16, 'hold_time_minutes': 5},
    ]
    final_elongation = [{'temperature': 60, 'hold_time_seconds': 300}]
    final_hold = [{'temperature': 4, 'hold_time_seconds': None}]

    # Run thermocycling program
    protocol.comment('Starting thermocycling...')
    if thermocycler.lid_position != 'closed':
        thermocycler.close_lid()
    thermocycler.set_lid_temperature(105)
    thermocycler.execute_profile(steps=cycling_steps, repetitions=30, block_max_volume=20)
    thermocycler.execute_profile(steps=final_elongation, repetitions=1, block_max_volume=20)
    thermocycler.deactivate_lid()
    thermocycler.set_block_temperature(4)
    protocol.comment('Thermocycling complete.')

   ## Tell user to move the plate to a thermocycler for 16hours incubation at 16C
    protocol.comment('Please transform the plate into E. coli and incubate at 37C for 16 hours.')