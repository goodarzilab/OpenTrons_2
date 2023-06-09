def get_values(*names):
    import json
    _all_values = json.loads("""{"mag_mod":"magnetic module gen2","pipette_type":"p300_single_gen2","pipette_mount":"left","sample_number":24,"sample_volume":20,"bead_ratio":1.8,"elution_buffer_volume":200,"incubation_time":1,"settling_time":1,"drying_time":5}""")
    return [_all_values[n] for n in names]


SAMPLE_NUMBER = 24
SAMPLE_VOLUME = 20
BEAD_RATIO = 1.8
ELUTION_BUFFER_VOLUME = 200
INCUBATION_TIME = 1
SETTLING_TIME = 1
DRYING_TIME = 5

import math

metadata = {
    'protocolName': 'PCR Cleanup with Magnetic Beads',
    'author': 'Ashir Borah <ashir.borah@ucsf.edu>, Opentrons <protocols@opentrons.com>',
    'apiLevel': '2.13'
    }


def run(protocol_context):
    
    mag_deck = protocol_context.load_module(mag_mod, '1')
    mag_plate = mag_deck.load_labware(
        'biorad_96_wellplate_200ul_pcr')
    output_plate = protocol_context.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2', 'output plate')

    total_tips = sample_number*8
    tiprack_num = math.ceil(total_tips/96)
    slots = ['3', '5', '6', '7', '8', '9', '10', '11'][:tiprack_num]

    pip_range = pipette_type.split('_')[0]
    if pip_range == 'p1000':
        tip_name = 'opentrons_96_tiprack_1000ul'
    elif pip_range == 'p300' or pip_range == 'p50':
        tip_name = 'opentrons_96_tiprack_300ul'
    elif pip_range == 'p20':
        tip_name = 'opentrons_96_tiprack_20ul'
    else:
        tip_name = 'opentrons_96_tiprack_10ul'
    tipracks = [
        protocol_context.load_labware(tip_name, slot)
        for slot in slots
    ]

    pipette = protocol_context.load_instrument(
        pipette_type, pipette_mount, tip_racks=tipracks)

    mode = pipette_type.split('_')[1]

    if mode == 'single':
        if sample_number <= 5:
            reagent_container = protocol_context.load_labware(
                'opentrons_24_tuberack_nest_2ml_snapcap', '4')
            liquid_waste = protocol_context.load_labware(
                'usascientific_12_reservoir_22ml', '5').wells()[-1]
        else:
            reagent_container = protocol_context.load_labware(
                'usascientific_12_reservoir_22ml', '4')
            liquid_waste = reagent_container.wells()[-1]
        samples = [well for well in mag_plate.wells()[:sample_number]]
        output = [well for well in output_plate.wells()[:sample_number]]
    else:
        reagent_container = protocol_context.load_labware(
            'usascientific_12_reservoir_22ml', '4')
        liquid_waste = reagent_container.wells()[-1]
        col_num = math.ceil(sample_number/8)
        samples = [col for col in mag_plate.rows()[0][:col_num]]
        output = [col for col in output_plate.rows()[0][:col_num]]

    # Define reagents and liquid waste
    beads = reagent_container.wells()[0]
    ethanol = reagent_container.wells()[1]
    elution_buffer = reagent_container.wells()[2]

    # Define bead and mix volume
    bead_volume = sample_volume*bead_ratio
    if bead_volume/2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = bead_volume/2
    total_vol = bead_volume + sample_volume + 5

    # Mix beads and PCR samples
    for target in samples:
        pipette.pick_up_tip()
        pipette.mix(5, mix_vol, beads)
        pipette.transfer(bead_volume, beads, target, new_tip='never')
        pipette.mix(10, mix_vol, target)
        pipette.blow_out()
        pipette.drop_tip()

    # Incubate beads and PCR product at RT for 5 minutes
    protocol_context.delay(minutes=incubation_time)

    # Engagae MagDeck and incubate
    mag_deck.engage()
    protocol_context.delay(minutes=settling_time)

    # Remove supernatant from magnetic beads
    pipette.flow_rate.aspirate = 25
    pipette.flow_rate.dispense = 150
    for target in samples:
        pipette.transfer(total_vol, target, liquid_waste, blow_out=True)

    # Wash beads twice with 70% ethanol
    air_vol = pipette.max_volume * 0.1
    for cycle in range(2):
        for target in samples:
            pipette.transfer(200, ethanol, target, air_gap=air_vol,
                             new_tip='once')
        protocol_context.delay(minutes=1)
        for target in samples:
            pipette.transfer(200, target, liquid_waste, air_gap=air_vol)

    # Dry at RT
    protocol_context.delay(minutes=drying_time)

    # Disengage MagDeck
    mag_deck.disengage()

    # Mix beads with elution buffer
    if elution_buffer_volume/2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = elution_buffer_volume/2
    for target in samples:
        pipette.pick_up_tip()
        pipette.transfer(
            elution_buffer_volume, elution_buffer, target, new_tip='never')
        pipette.mix(20, mix_vol, target)
        pipette.drop_tip()

    # Incubate at RT
    protocol_context.delay(minutes=5)

    # Engage MagDeck and remain engaged for DNA elution
    mag_deck.engage()
    protocol_context.delay(minutes=settling_time)

    # Transfer clean PCR product to a new well
    for target, dest in zip(samples, output):
        pipette.transfer(elution_buffer_volume, target, dest, blow_out=True)
