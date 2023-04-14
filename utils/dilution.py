'''
This script should take a csv file that has the sample names and the concentrations of samples. It should then dilute everything to the desired concentration.
The intermediate dilutions should be done in 1.5ml Eppendorf tubes. The final dilutions should on PCR strips. The originals also come from PCR strips.

The CSV should be of the format
samples, concentration(in ng/ul)
sample1, 100
...

'''

DESIRED_CONCENTRATION = 10 # Change this value to your desired concentration
WELL_MAX_VOLUME = 100  # PCR well max volume in µL
MIN_PIPETTE_VOLUME = 1  # Minimum pipetting volume in µL
FINAL_VOLUME = 100  # Change this value to the desired final volume in the destination well



source_strip_slot = 1
destination_strip_slot = 2
intermediary_strip_slot = 3

source_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
destination_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
    

INTERMEDIARY_ROWS = ['A', 'B', 'C', 'D']
INTERMEDIARY_COLS = range(1,7)
INTERMEDIARY_TUBES = [f'{row}{col}' for row in INTERMEDIARY_ROWS for col in INTERMEDIARY_COLS]


import pandas as pd
import logging
from opentrons import protocol_api
from collections import deque

metadata = {
    'apiLevel': '2.13',
}

def run(protocol: protocol_api.ProtocolContext):

    # Set up logging
    logging.basicConfig(filename='dilution_process.log', level=logging.INFO)
    
    # Load labware
    source_pcr_strips = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', source_strip_slot)
    destination_pcr_strips = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', destination_strip_slot)
    intermediary_mixing_tubes = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', intermediary_strip_slot)
    dilutent_well = protocol.load_labware('nest_12_reservoir_15ml', 6)
    tip_rack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tip_rack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)

    dilutent = dilutent_well.wells()[0]

    # Load pipette
    pipette = protocol.load_instrument('p300_single', 'right', tip_racks=[tip_rack_1, tip_rack_2])

    # Read CSV file using pandas
    samples = pd.read_csv('sample_concentrations.csv')
    
    assert len(samples.index) == len(source_wells), "Number of samples does not match number of source wells."
    assert len(source_wells) == len(destination_wells), "Number of source wells does not match number of destination wells."

    # Calculate dilution volumes and perform pipetting
      # Change this value to your desired concentration
    intermediary_queue = deque(INTERMEDIARY_TUBES)

    for i, sample in samples.iterrows():
        initial_concentration = sample.loc[sample, 'concentration'])
        dilution_factor = DESIRED_CONCENTRATION / initial_concentration

        if dilution_factor > 1:
            logging.warning(f"Sample {sample['name']} cannot be diluted to the desired concentration. Moving as is.")
            pipette.pick_up_tip()
            pipette.transfer(FINAL_VOLUME, source_pcr_strips[source_wells[i]], destination_pcr_strips[destination_wells[i]], new_tip='never')
            pipette.drop_tip()
            continue

        sample_volume = FINAL_VOLUME * dilution_factor / (1 + dilution_factor)
        diluent_volume = FINAL_VOLUME - sample_volume

        if sample_volume < MIN_PIPETTE_VOLUME or diluent_volume < MIN_PIPETTE_VOLUME:
            logging.error(f"Minimum pipetting volume not met for sample {sample['name']}.")
            continue

        current_concentration = initial_concentration
        current_well = source_wells[i]

        while current_concentration * FINAL_VOLUME / (WELL_MAX_VOLUME - FINAL_VOLUME) > DESIRED_CONCENTRATION:
            if not intermediary_queue:
                logging.error("No intermediary PCR strip tubes available.")
                break

            intermediary_row = intermediary_queue.popleft()
            intermediary_well = f"{intermediary_row}{i + 1}"

            pipette.pick_up_tip()
            pipette.transfer(1, source_pcr_strips[current_well], intermediary_mixing_tubes[intermediary_well], new_tip='never')
            pipette.drop_tip()

            pipette.pick_up_tip()
            pipette.transfer(999, dilutent, intermediary_mixing_tubes[intermediary_well], new_tip='never')
            pipette.drop_tip()

            logging.info(f"Sample {sample['name']} diluted from {current_well} to {intermediary_well} with 1:1000 dilution.")

            current_concentration /= 1000
            current_well = intermediary_well

        pipette.pick_up_tip()
        pipette.transfer(sample_volume, source_pcr_strips[current_well], destination_pcr_strips[destination_wells[i]], new_tip='never')
        pipette.drop_tip()

        pipette.pick_up_tip()
        pipette.transfer(diluent_volume, dilutent, destination_pcr_strips[destination_wells[i]], new_tip='never')
        pipette.drop_tip()

        logging.info(f"Sample {sample['name']} diluted from {current_well} to {destination_wells[i]} reaching the desired concentration.")