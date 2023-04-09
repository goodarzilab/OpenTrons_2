from opentrons import protocol_api

metadata = {
    'apiLevel': '2.11',
    'protocolName': 'Transfer 200µL Tips with p300 8-Channel Pipette and 20µL using the p20 8-channel Pipette'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    full_tip_box_200 = protocol.load_labware('opentrons_96_tiprack_300ul', '2')
    empty_tip_box_200 = protocol.load_labware('opentrons_96_tiprack_300ul', '3')
    
    full_tip_box_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '5')
    empty_tip_box_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '6')

    # Pipettes
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'right')
    p20_multi = protocol.load_instrument('p20_multi_gen2', 'left')

    # Transfer 200µL tips
    for source_well, dest_well in zip(full_tip_box_200.columns(), empty_tip_box_200.columns()):
        p300_multi.pick_up_tip(source_well[0])
        p300_multi.drop_tip(dest_well[0])

    # Transfer 20µL tips
    for source_well, dest_well in zip(full_tip_box_20.columns(), empty_tip_box_20.columns()):
        p20_multi.pick_up_tip(source_well[0])
        p20_multi.drop_tip(dest_well[0])
