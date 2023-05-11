import pandas as pd
from opentrons import protocol_api

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'CSV Transfer Protocol',
    'author': 'ChatGPT',
    'description': 'Transfer liquids from a 1.5 mL Eppendorf tube to a microplate using a P20 pipette based on a CSV input',
}

def run(protocol: protocol_api.ProtocolContext):

    # Load labware
    tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', 6)
    tiprack_200 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 7)
    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 1)
    plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 2)

    # Load pipette
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20])
    p200 = protocol.load_instrument('p200_single_gen2', 'left', tip_racks=[tiprack_200])

    # Read the CSV file
    tube_source_array = ['A1', 'A2', 'A3', 'A4', 'A5']
    p20.pick_up_tip()
    p200.pick_up_tip()

    # Read the CSV file
    csv_file_path = '/var/lib/jupyter/notebooks/data/PCR_concentrations.csv'
    df = pd.read_csv(csv_file_path)

    total_volume_from_source = 0
    tube_counter = 0

    for index, row in df.iterrows():
        well_location = row['Location']
        volume = row['Amount']

        total_volume_from_source += volume

        if total_volume_from_source > 1200:
            tube_counter += 1
            total_volume_from_source = volume

        source_tube = tube_rack.wells_by_name()[tube_source_array[tube_counter]]

        if volume > 1 and volume < 30:
            p20.transfer(volume, source_tube, plate.wells_by_name()[well_location], new_tip='never')
        
        elif volume > 30 and volume < 200:
            p200.aspirate(volume, source_tube, plate.wells_by_name()[well_location], new_tip='never')
        else:
            protocol.comment('The transfer amount is outside transferable amount in location {}'.format(well_location))
            
    p20.drop_tip()
    p200.drop_tip()
