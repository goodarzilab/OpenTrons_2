from opentrons import protocol_api

metadata = {
    'apiLevel': '2.11',
    'protocolName': 'Transfer Liquid individually from PCR Strips to 96-Well PCR Plate with 8-Channel Pipette'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    # pcr_strips = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '4')
    pcr_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '6')
    tiprack_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', '5')
    temp_mod = protocol.load_module('temperature module gen2', '4')
    
    temp_labware = temp_mod.load_labware(
        "opentrons_96_aluminumblock_generic_pcr_strip_200ul",
        label="Temperature-Controlled Tubes of H20",
    )
     
    # Set temp to 4C
    temp_mod.set_temperature(celsius=4)
    temp_mod.status  # 'holding at target'

    # Pipettes
    p20_multi = protocol.load_instrument('p20_multi_gen2', 'left', tip_racks=[tiprack_20ul])

    # Transfer liquid from PCR strips to 96-well PCR plate
    source_well = temp_labware.wells_by_name()['A1']
    dest_columns = pcr_plate.columns()
    
    p20_multi.pick_up_tip()

    for idx, dest_column in enumerate(dest_columns):
        transfer_volume = 12 - idx
        p20_multi.transfer(transfer_volume, source_well, dest_column[0], new_tip='never')
        
    temp_mod.deactivate()
    temp_mod.status  # 'idle'
