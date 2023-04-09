"""
Tube location file format

Type,ID,Well
primer,P1,A1
primer,P2,A2
...
sample,S1,B1
sample,S2,B2
...

"""



import pandas as pd
from opentrons import protocol_api

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Transfer Components from Separate Thermoblock Tubes to 384-Well Plate with Pandas'
}

def map_tube_to_well(dataframe, p384, temp_labware, primer_tube_positions, sample_tube_positions, p20_single):
    for index, row in dataframe.iterrows():
        for col, location in enumerate(row):
            [primer, sample] = [x.strip()  for x in location.split(',')]
            print('primer {} sample {}'.format(primer, sample))
            primer_source_well = primer_tube_positions.loc[primer, 'Well']
            sample_source_well = sample_tube_positions.loc[sample, 'Well']
            dest_well = p384.wells()[index * len(dataframe.columns) + col]
            primer_source_well = temp_labware.wells_by_name()[primer_source_well]
            sample_source_well = temp_labware.wells_by_name()[sample_source_well]

            # Transfer primer and sample to the destination well
            p20_single.transfer(2.5, primer_source_well, dest_well)
            p20_single.transfer(2.5, sample_source_well, dest_well)

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    primer_tubes = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '1')
    sample_tubes = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')
    p384 = protocol.load_labware('corning_384_wellplate_112ul_flat', '3')
    temp_mod = protocol.load_module('temperature module gen2', '4')
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '7')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '8')
    tiprack_20ul_3 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tiprack_20ul_4 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '10')
    tiprack_20ul_5 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '11')

  
    temp_labware = temp_mod.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        label="Temperature-Controlled Tubes of H20",
    )
    
    # Set temp to 4C
    temp_mod.set_temperature(celsius=4)
    temp_mod.status  # 'holding at target'
    
    protocol.pause('Thermoblock up to specific temp of 4C')

    # Pipettes
    p20_single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20ul_1, tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5])

    # Read CSV files
    transfer_data = pd.read_csv('transfer_locations.csv',header=None)  # Replace with the actual file name
    tube_positions = pd.read_csv('tube_positions.csv')  # Replace with the actual file name
    primer_tube_positions = tube_positions[tube_positions['Type'] == 'primer']
    sample_tube_positions = tube_positions[tube_positions['Type'] == 'sample']

    # Set index for primer and sample tube positions
    primer_tube_positions.set_index('ID', inplace=True)
    sample_tube_positions.set_index('ID', inplace=True)
    
    print(primer_tube_positions.head())
    print(sample_tube_positions.head())
    
    #import pdb; pdb.set_trace()

    # Transfer components
    map_tube_to_well(transfer_data, p384, temp_labware, primer_tube_positions, sample_tube_positions, p20_single)
