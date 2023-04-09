from opentrons import protocol_api

metadata = {
    'apiLevel': '2.11',
    'protocolName': 'Transfer Liquid from PCR Strips to 96-Well PCR Plate with p300 8-Channel Pipette'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    pcr_strips = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '1')
    pcr_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2')
    tiprack_300ul = protocol.load_labware('opentrons_96_tiprack_300ul', '3')

    # Pipettes
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tiprack_300ul])

    # Calculate total volume to aspirate
    total_volume = sum(range(1, 13))

    # Transfer liquid from PCR strips to 96-well PCR plate
    source_wells = pcr_strips.rows_by_name()['A']
    dest_wells = pcr_plate.rows_by_name()

    for source_well, dest_well_row in zip(source_wells, dest_wells.values()):
        p300_multi.pick_up_tip()
        p300_multi.aspirate(total_volume, source_well)
        for idx, dest_well in enumerate(dest_well_row[:12]):
            transfer_volume = 12 - idx
            p300_multi.dispense(transfer_volume, dest_well)
        p300_multi.drop_tip()