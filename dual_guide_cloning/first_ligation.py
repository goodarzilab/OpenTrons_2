'''

Mix together the following. INCLUDE A NEGATIVE CONTROL OF WATER! Always add Ligase last.
    Mix								1X				
* pJR85_digested (95.2 ng/µl)		4 μl				
* insert_dig (diluted to 4 ng/µl)	2 μl				
* 10x T4 Ligase buffer				1 μl				
* T4 DNA Ligase					    1 μl				
* H2O 		-> total 10 µl			2 μl			
Ligate at 16 °C for 16 hours (overnight). 
Purify the ligation reaction using MagBeads at 0.50 ratio. Fill up volume first to 50 µl for accuracy.

'''

TOTAL_RxN_VOL = 10

AMOUNTS_TO_ADD = {
    'pJR85_digested': 4,
    'insert_dig': 2,
    'T4_ligase_buffer': 1,
    'T4_dna_ligase': 1
}

AMOUNTS_TO_ADD['water'] = TOTAL_RxN_VOL - sum(AMOUNTS_TO_ADD.values())


MASTERMIX_VOL = 5

from opentrons import protocol_api
import math

metadata = {
    'protocolName': '1st Ligation',
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
    plate_96_well_with_inserts = protocol.load_labware('nest_96_wellplate_200ul_flat', 1, '96 Well Insert Plate')
    tiprack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 2, '200µL Tip Rack')
    tiprack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 3, '200µL Tip Rack')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 5, '20µL Tip Rack')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6, '20µL Tip Rack')
    plate_96_well_being_assembled = protocol.load_labware('nest_96_wellplate_200ul_flat', 9, '96 Well Assembled Plate for ligation')
   
    

    # Pipettes
    p200 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_200ul_1, tiprack_200ul_2])
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])

    ## Prompt to remind user that pJR85 needs to be digested
    protocol.comment('This protocol requires that pJR85 has been digested with BsmBI_v2. Please ensure that this has been done before continuing.')

    # Reagents
    T4_ligase_buffer = thermoblock.wells_by_name()['A1']
    T4_dna_ligase = thermoblock.wells_by_name()['A2']
    pJR85_digested = thermoblock.wells_by_name()['A3']
    water = thermoblock.wells_by_name()['A4']
    mastermix = thermoblock.wells_by_name()['B1']
    
    
    # Thermoblock temperature
    temp_mod.set_temperature(4)
    temp_mod.status  # 'holding at target'

    # Wells used for cloning
    wells_used_for_cloning = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
    
    # Prepare mastermix
    ## Add an additional 15% to the mastermix volume to account for pipette error
    total_wells = math.ceil(len(wells_used_for_cloning) * 1.15)
    p200.transfer(total_wells*AMOUNTS_TO_ADD['T4_ligase_buffer'], T4_ligase_buffer, mastermix,)
    p200.transfer(total_wells*AMOUNTS_TO_ADD['pJR85_digested'], pJR85_digested, mastermix)
    p200.transfer(total_wells*AMOUNTS_TO_ADD['water'], water, mastermix)
    p200.transfer(total_wells*AMOUNTS_TO_ADD['T4_dna_ligase'], T4_dna_ligase, mastermix)
    
    p200.pick_up_tip()
    p200.mix(10, TOTAL_RxN_VOL/2, mastermix)
    p200.touch_tip(mastermix)
    p200.blow_out()
    p200.drop_tip()

    ## Create the mastermix liquid definition
    mastermix_liquid = protocol.define_liquid(
        'mastermix',
        density=1.05,
        viscosity=1.0,
        container=mastermix,
        volume=MASTERMIX_VOL*total_wells
    )



    # Distribute mastermix


    ## Maybe use just wells() instead of wells_by_name()?
    p200.distribute(8, mastermix, [plate_96_well_being_assembled.wells()[wells] for wells in wells_used_for_cloning])

    # Transfer mastermix and insert
    for well_name in wells_used_for_cloning:
        well = plate_96_well_with_inserts.wells_by_name()[well_name]

        # Transfer insert
        p20.transfer(AMOUNTS_TO_ADD['insert_amount'], well, plate_96_well_being_assembled.wells_by_name()[well_name], new_tip='always', blow_out=True, mix_after=(3, 10))

   ## Tell user to move the plate to a thermocycler for 16hours incubation at 16C
    protocol.comment('Please move the plate to a thermocycler for 16 hours incubation at 16C.')