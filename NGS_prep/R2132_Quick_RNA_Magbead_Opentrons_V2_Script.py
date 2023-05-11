from opentrons import protocol_api, types
import math

sample_number = 4
sample_volume = 200
magnet_height_from_base = 21.5 # With Gen 1 Adapter
sample_transfer_step = True
dnase_treatment = True

#scaling_factor = round(sample_volume/200, 1)
odd_coordinates=[[1.8, 0, 2], [1.8, 0, 2], [-1.8, 0, 2], [-1.8, 0, 2], [0, 0, 0], [0, 0, 2], [0, 0, 2], [0, 0, 20]]
even_coordinates=[[-1.8, 0, 2], [-1.8, 0, 2], [1.8, 0, 2], [1.8, 0, 2], [0, 0, 0], [0, 0, 2], [0, 0, 2], [0, 0, 20]]
general_coordinates = [[0, 0, 1], [0, 0, 5], [0, 0, 1], [0, 0, 5]]

# metadata
metadata = {
    'protocolName': 'R2132 Quick RNA Magbead',
    'author': 'jlam@zymoresearch.com',
    'description': 'Opentron Script for R2132 Quick RNA Magbead Updated: 04/07/23',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):
    #User Entry
    #Deck Layout
    user_pipette = {
        'left_pipette' : 'p300_multi_gen2',
        'right_pipette' : 'p1000_single_gen2'
    }

    user_module = {
        'magnetic_module' :{
            'module_api_name' : 'magnetic module gen2',
            'module_deck_slot' : 6
        }
    }

    user_labware = {
        'elution_plate': {
            'labware_api_name': 'biorad_96_wellplate_200ul_pcr',
            'labware_deck_slot' : 1
        },
        'reagent_reservoir': {
            'labware_api_name': 'nest_12_reservoir_15ml',
            'labware_deck_slot' : 2
        },
        'sample_rack': {
            'labware_api_name': 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',
            'labware_deck_slot' : 3
        },
        'magnet_plate': {
            'labware_api_name': 'nest_96_wellplate_2ml_deep',
            'labware_deck_slot' : 'magnetic_module'
        },
        'waste_plate': {
            'labware_api_name': 'nest_1_reservoir_195ml',
            'labware_deck_slot' : 9
        }
    }

    user_pipette_tip_box = {
        'pipette_200_tip_box_4':{
            'pipette_tip_api_name': 'opentrons_96_filtertiprack_200ul',
            'pipette_tip_deck_slot': 4,
        },
        'pipette_200_tip_box_8': {
            'pipette_tip_api_name': 'opentrons_96_filtertiprack_200ul',
            'pipette_tip_deck_slot': 8,
        },
        'pipette_200_tip_box_7': {
            'pipette_tip_api_name': 'opentrons_96_filtertiprack_200ul',
            'pipette_tip_deck_slot': 7,
        },
        'pipette_200_tip_box_10': {
            'pipette_tip_api_name': 'opentrons_96_filtertiprack_200ul',
            'pipette_tip_deck_slot': 10,
        },
        'pipette_1000_tip_box_11': {
            'pipette_tip_api_name': 'opentrons_96_filtertiprack_1000ul',
            'pipette_tip_deck_slot': 11,
        },
    }

    #Well/Tip Assignment

    user_labware_sequence= {
        'magnetic_bead' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A1'],
            'liquid_wells_volume' : 4000,
            'well_type' : 'reservoir'
        },
        'rna_lysis_buffer' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A2'],
            'liquid_wells_volume' : 12000,
            'well_type' : 'reservoir'
        },
        'magbead_dna_rna_wash_1_buffer' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A3'],
            'liquid_wells_volume' : 16000,
            'well_type' : 'reservoir'
        },
        'magbead_dna_rna_wash_2_buffer' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A4'],
            'liquid_wells_volume' : 16000,
            'well_type' : 'reservoir'
        },
        'dnase_rna_prep_buffer' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A5'],
            'liquid_wells_volume' : 16000,
            'well_type' : 'reservoir'
        },
        'ethanol' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A6', 'A7', 'A8'],
            'liquid_wells_volume' : 18000,
            'well_type' : 'reservoir'
        },
        'dnase_ethanol' : {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A9', 'A10'],
            'liquid_wells_volume' : 18000,
            'well_type' : 'reservoir'
        },
        'dnase_reaction_mix' : {
            'liquid_labware': 'magnet_plate',
            'liquid_wells' : ['A12'],
            'liquid_wells_volume' : 600,
            'well_type' : 'individual'
        },
        'dnase_rnase_free_water': {
            'liquid_labware': 'reagent_reservoir',
            'liquid_wells' : ['A12'],
            'liquid_wells_volume' : 7000,
            'well_type' : 'reservoir'
        },
        'magnetic_sample_well': {
            'liquid_labware': 'magnet_plate',
            'liquid_wells' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',],
            'liquid_wells_volume' : 0,
            'well_type' : 'individual'
        },
        'waste_reagent_well': {
            'liquid_labware': 'waste_plate',
            'liquid_wells' : ['A1'],
            'liquid_wells_volume' : 0,
            'well_type' : 'reservoir'
        },
        'elution_sample_well' : {
            'liquid_labware': 'elution_plate',
            'liquid_wells' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3'],
            'liquid_wells_volume' : 0,
            'well_type' : 'individual'
        },
        'sample_tube_wells' : {
            'liquid_labware': 'sample_rack',
            'liquid_wells'  : ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2', 'A3', 'B3', 'C3', 'D3', 'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5', 'D5', 'A6', 'B6', 'C6', 'D6' ],
            'liquid_wells_volume' : 500,
            'well_type' : 'individual'
        }
    }

    user_tip_sequence = {
        'rna_lysis_buffer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1']
        },
        'ethanol_sample_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2']
        },
        'magbinding_bead_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 
                                'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5']
        },
        'sample_transfer_tips' : {
            'tip_box':'pipette_1000_tip_box_11',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',]
        },
        'sample_1000_mix_tips' : {
            'tip_box':'pipette_1000_tip_box_11',
            'tip_selected' : ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 
                                'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',]
        },
        'sample_300_mix_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'sample_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'magbead_dna_rna_wash_1_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',]
        },
        'magbead_dna_rna_wash_1_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
                                'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',]
        },
        'magbead_dna_rna_wash_1_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
                                'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',]
        },
        'magbead_dna_rna_wash_2_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7']
        },
        'magbead_dna_rna_wash_2_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 
                                'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',]
        },
        'magbead_dna_rna_wash_2_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 
                                'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',]
        },
        'ethanol_1_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',]
        },
        'ethanol_1_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3']
        },
        'ethanol_1_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_8',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3']
        },
        'ethanol_2_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9']
        },
        'ethanol_2_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_7',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'ethanol_2_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_7',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_rnase_free_water_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_4',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_rnase_free_water_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_7',
            'tip_selected' : ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
                                'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',]
        },
        'elution_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_7',
            'tip_selected' : ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
                                'A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',]
        },
        'dnase_reaction_mix_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_reaction_mix_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_rna_prep_buffer_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'H9',]
        },
        'dnase_rna_prep_buffer_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_rna_prep_buffer_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'H11', 
                                'A12', 'B12', 'C12', 'D12', 'E12', 'F12','G12', 'H12']
        },
        'dnase_ethanol_1_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8']
        },
        'dnase_ethanol_1_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 
                                'D7', 'E7', 'F7', 'G7', 'H7']
        },
        'dnase_ethanol_1_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6', 'A7', 'B7', 'C7', 
                                'D7', 'E7', 'F7', 'G7', 'H7']
        },
        'dnase_ethanol_2_transfer_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4']
        },
        'dnase_ethanol_2_mixing_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3']
        },
        'dnase_ethanol_2_supernatant_tips' : {
            'tip_box':'pipette_200_tip_box_10',
            'tip_selected' : ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
                                'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3']
        },
    }

    class Pipette:
        def __init__(self, pipette_API, pipette_position):
            self.pipette_API = pipette_API
            self.pipette_position = pipette_position

            self.pipette = protocol.load_instrument(self.pipette_API, self.pipette_position)

        def get_pipette(self):
            return self.pipette

        def get_type_of_pipette(self):
            if self.pipette_API.find("multi") == -1:
                return "single"
            return "multi"
        

    pipette_list={}

    if user_pipette['left_pipette'] != None:
        pipette_list['left_pipette'] = Pipette(user_pipette['left_pipette'], 'left')
        
    if user_pipette['right_pipette'] != None:
        pipette_list['right_pipette'] = Pipette(user_pipette['right_pipette'], 'right')

    class Module:
        def __init__(self, module_API, module_deck_slot):
            self.module_API = module_API
            self.module_deck_slot = module_deck_slot

            if self.module_API == 'thermocycler module':
                self.module = protocol.load_module(self.module_API)
            else:
                self.module = protocol.load_module(self.module_API, self.module_deck_slot)

            self.initialize_module()

        def get_module(self):
            return self.module

        def initialize_module(self):
            if self.module_API == 'thermocycler module':
                self.module.deactivate()
                self.module.open_lid()
            elif self.module_API == 'magnetic module gen2' or self.module_API == 'magnetic module':
                self.module.disengage()
            elif self.module_API == 'temperature module':
                self.module.deactivate()

    module_list = {}

    for name, module_data in user_module.items():
        if module_data['module_api_name'] != 'thermocycler module':
            module_list[name] = Module(module_data['module_api_name'], module_data['module_deck_slot'])
        else:
            module_list[name] = Module(module_data['module_api_name'], None)
    
    class Labware:
        def __init__(self, labware_API, labware_deck_slot):
            self.labware_API = labware_API
            self.labware_deck_slot = labware_deck_slot

            if isinstance(self.labware_deck_slot, int):
                self.labware = protocol.load_labware(self.labware_API, self.labware_deck_slot)
            else:
                self.labware =  module_list[self.labware_deck_slot].get_module().load_labware(self.labware_API)
            
            self.labware_total_wells = len(self.labware.wells())

        def get_labware(self):
            return self.labware

        def get_total_number_of_wells(self):
            return self.labware_total_wells

    labware_list = {}

    for name, labware_data in user_labware.items():
        labware_list[name] = Labware(labware_data['labware_api_name'], labware_data['labware_deck_slot'])

    class PipetteBox:
        def __init__(self, pipette_box_API, pipette_box_deck_slot):
            self.pipette_box_API = pipette_box_API
            self.pipette_box_deck_slot = pipette_box_deck_slot
            self.pipette_tip_box = protocol.load_labware(self.pipette_box_API, self.pipette_box_deck_slot)
            self.max_tip_volume = self.pipette_tip_box['A1'].max_volume

        def get_pipette_tip_box(self):
            return self.pipette_tip_box

        def get_max_tip_volume(self):
            return self.max_tip_volume

    pipette_tip_box_list = {}

    for name, pipette_tip_box_data in user_pipette_tip_box.items():
        pipette_tip_box_list[name] = PipetteBox(pipette_tip_box_data['pipette_tip_api_name'], pipette_tip_box_data['pipette_tip_deck_slot'])

    class LabwareSequence:
        def __init__(self, labware, wells, initial_volume, well_type):
            self.labware = labware_list[labware].get_labware()
            self.single_wells = wells
            self.multi_wells = []
            self.well_type = well_type

            self.row_list = []
            for well_name in self.single_wells:
                self.row_list.append(well_name[0])
            self.row_list = sorted(list(set(self.row_list)))
            
            self.column_list = []
            for column_num in self.single_wells:
                self.column_list.append(int(column_num[1:]))
            self.column_list = sorted(list(set(self.column_list)))

            for well in self.single_wells:
                if well.find('A') != -1:
                    self.multi_wells.append(well)

            self.well_volume = {}
            for keys in self.single_wells:
                self.well_volume[keys] = initial_volume
            
            self.stop_volume = .15* initial_volume

        def get_well_type(self):
            return self.well_type

        def get_labware(self):
            return self.labware

        def get_single_wells(self):
            return self.single_wells

        def get_multi_wells(self):
            return self.multi_wells
        
        def get_volume(self, well):
            return self.well_volume[well]
        
        def sub_volume(self, multi, wells, volume):
            if multi and self.well_type == 'reservoir':
                volume *= 8
                self.well_volume[wells] -= volume
                if self.well_volume[wells] < 0:
                    self.well_volume[wells] = 0
            if multi and self.well_type == 'individual':
                well_column = wells[1:]
                for row in self.row_list:
                    self.well_volume[f"{row}{well_column}"] -= volume
                    if self.well_volume[f"{row}{well_column}"] < 0:
                        self.well_volume[f"{row}{well_column}"] =0
            if not multi:
                self.well_volume[wells] -= volume
                if self.well_volume[wells] < 0:
                    self.well_volume[wells] = 0
        
        def add_volume(self, multi, wells, volume):
            if multi and self.well_type == 'reservoir':
                volume *= 8
                self.well_volume[wells] += volume
            if multi and self.well_type == 'individual':
                well_column = wells[1:]
                for row in self.row_list:
                    self.well_volume[f"{row}{well_column}"] += volume
            if not multi:
                self.well_volume[wells] += volume
        
        def get_permission_to_use(self, multi, well, volume):
            if multi and self.well_type == 'reservoir':
                volume *= 8
            if self.well_volume[well] - volume >= self.stop_volume:
                return True
            else:
                return False
        
        def refill_well(self, wells, volume):
            if self.well_type == 'individual':
                for well in wells:
                    self.well_volume[well] = volume
            else:
                self.well_volume[well] = volume

            

    labware_well_sequence = {}

    for name, well_sequence_data in user_labware_sequence.items():
        labware_well_sequence[name] = LabwareSequence(well_sequence_data['liquid_labware'], well_sequence_data['liquid_wells'], well_sequence_data['liquid_wells_volume'], well_sequence_data['well_type'])

    class TipSequence:
        def __init__(self,tipbox,tip_selected):
            self.tipbox = pipette_tip_box_list[tipbox].get_pipette_tip_box()
            self.max_pipette_volume = self.tipbox['A1'].max_volume
            self.single_tips = tip_selected
            self.multi_tips = []

            for tip in self.single_tips:
                if tip.find('A') != -1:
                    self.multi_tips.append(tip)
        
        def get_pipette_tip_box(self):
            return self.tipbox
        
        def get_max_pipette_volume(self):
            return self.max_pipette_volume
        
        def get_single_tips(self):
            return self.single_tips
        
        def get_multi_tips(self):
            return self.multi_tips

    tip_sequence = {}

    for name, tip_sequence_data in user_tip_sequence.items():
        tip_sequence[name] = TipSequence(tip_sequence_data['tip_box'], tip_sequence_data['tip_selected'])

    procedure = [
        # Transfer RNA Lysis Buffer and Sample + Mix
        {
            'name': 'Transfer RNA Lysis Buffer',
            'step':'transfer',
            'transfer_volume': sample_volume,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'rna_lysis_buffer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'rna_lysis_buffer',
                'aspirate_speed' : 50,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Transfer Sample',
            'step':'sample_transfer',
            'transfer_volume': sample_volume,
            'pipette_parameters':{
                'pipetter' : 'right_pipette',
                'load_tip': 'sample_transfer_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'sample_tube_wells',
                'aspirate_speed' : 50,
                'new_well_per_aspirate': True
            },

            'dispense_parameters':{
                'dispense_pos': 'bottom',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Sample with RNA Lysis Buffer',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'sample_300_mix_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'sample_300_mix_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 500,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        # Transfer Ethanol and Mix
        {
            'name': 'Transfer Ethanol',
            'step':'transfer',
            'transfer_volume': sample_volume * 2,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_sample_transfer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'ethanol',
                'aspirate_speed' : 50,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Sample with Magbead and Ethanol',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'sample_300_mix_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'sample_300_mix_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 500,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        # Transfer Magbeads and Mix
        {
            'name': 'Transfer Magbeads',
            'step':'transfer',
            'transfer_volume': 20,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbinding_bead_transfer_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'magnetic_bead',
                'aspirate_speed' : 50,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },
            'dispense_parameters':{
                'dispense_pos': 'bottom',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True,
            },
            'pre_mix_parameters': {
                'mix_volume': 200,
                'mix_cycles': 10,
                'mix_pos' : {
                    'odd_and_even_mix': False,
                    'odd_mix_pos':[],
                    'even_mix_pos':[],
                    'general_mix_pos' : [[0, 0, 1],[0, 0, 5]]
                },
                'mix_speed' : 200,
            },
        },
        {
            'name': 'Mix Sample with Magbead',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'sample_300_mix_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'sample_300_mix_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 30,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 500,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Remove Supernatant',
            'step' : 'supernatant_removal',
            'supernatant_removal_volume': ((sample_volume * 4) + 100),
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'sample_supernatant_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : {
                    'odd_and_even_aspirate': True,
                    'odd_aspirate_position':[-1.5, 0, 0],
                    'even_aspirate_position':[1.5, 0, 0],
                    'general_aspiration_position': []
                },
                'aspirate_seq' : 'magnetic_sample_well',
                'new_well_per_aspirate': True,
                'aspirate_speed' : 25,
            },
            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'waste_reagent_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': False
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },
        #Transfer MagBead DNA/RNA Wash 1
        {
            'name': 'Transfer MagBead DNA/RNA Wash 1',
            'step':'transfer',
            'transfer_volume': 500,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_1_transfer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'magbead_dna_rna_wash_1_buffer',
                'aspirate_speed' : 100,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Magbeads with Magbead DNA/RNA Wash 1',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_1_mixing_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'magbead_dna_rna_wash_1_mixing_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 200,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Remove Supernatant',
            'step' : 'supernatant_removal',
            'supernatant_removal_volume': 600,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_1_mixing_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : {
                    'odd_and_even_aspirate': True,
                    'odd_aspirate_position':[-1.5, 0, 0],
                    'even_aspirate_position':[1.5, 0, 0],
                    'general_aspiration_position': []
                },
                'aspirate_seq' : 'magnetic_sample_well',
                'new_well_per_aspirate': True,
                'aspirate_speed' : 25,
            },
            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'waste_reagent_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': False
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },
        # Transfer Magbead DNA/RNA Wash 2
        {
            'name': 'Transfer Magbead DNA/RNA Wash 2',
            'step':'transfer',
            'transfer_volume': 500,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_2_transfer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'magbead_dna_rna_wash_2_buffer',
                'aspirate_speed' : 100,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Magbeads with Magbead DNA/RNA Wash 2',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_2_mixing_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'magbead_dna_rna_wash_2_mixing_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 200,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Remove Supernatant',
            'step' : 'supernatant_removal',
            'supernatant_removal_volume': 600,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'magbead_dna_rna_wash_2_supernatant_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : {
                    'odd_and_even_aspirate': True,
                    'odd_aspirate_position':[-1.5, 0, 0],
                    'even_aspirate_position':[1.5, 0, 0],
                    'general_aspiration_position': []
                },
                'aspirate_seq' : 'magnetic_sample_well',
                'new_well_per_aspirate': True,
                'aspirate_speed' : 25,
            },
            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'waste_reagent_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': False
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },
        # Ethanol 1 Transfer
        {
            'name': 'Transfer Ethanol 1',
            'step':'transfer',
            'transfer_volume': 500,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_1_transfer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'ethanol',
                'aspirate_speed' : 100,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Magbeads with Ethanol',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_1_mixing_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'ethanol_1_mixing_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 200,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Remove Supernatant',
            'step' : 'supernatant_removal',
            'supernatant_removal_volume': 600,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_1_supernatant_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : {
                    'odd_and_even_aspirate': True,
                    'odd_aspirate_position':[-1.5, 0, 0],
                    'even_aspirate_position':[1.5, 0, 0],
                    'general_aspiration_position': []
                },
                'aspirate_seq' : 'magnetic_sample_well',
                'new_well_per_aspirate': True,
                'aspirate_speed' : 25,
            },
            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'waste_reagent_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': False
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },
        # Transfer Ethanol 2
        {
            'name': 'Transfer Ethanol 2',
            'step':'transfer',
            'transfer_volume': 500,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_2_transfer_tips',
                'new_tips_per_transfer' : False,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'ethanol',
                'aspirate_speed' : 100,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Magbeads with Ethanol 2',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_2_mixing_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'ethanol_2_mixing_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 200,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': True,
                    'odd_mix_pos':odd_coordinates,
                    'even_mix_pos':even_coordinates,
                    'general_mix_pos' : []
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 200,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Remove Supernatant',
            'step' : 'supernatant_removal',
            'supernatant_removal_volume': 600,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'ethanol_2_supernatant_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : {
                    'odd_and_even_aspirate': True,
                    'odd_aspirate_position':[-1.5, 0, 0],
                    'even_aspirate_position':[1.5, 0, 0],
                    'general_aspiration_position': []
                },
                'aspirate_seq' : 'magnetic_sample_well',
                'new_well_per_aspirate': True,
                'aspirate_speed' : 25,
            },
            'dispense_parameters':{
                'dispense_pos': 'top',
                'dispense_seq': 'waste_reagent_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': False
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },
        # Dnase Treatment
        {
            'name': 'Dnase Treatment',
            'step': 'DNase Treatment',
            'dnase_procedure': [
                {
                    'name': 'Transfer Dnase Reaction Mix',
                    'step':'transfer',
                    'transfer_volume': 50,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_reaction_mix_transfer_tips',
                        'new_tips_per_transfer' : True,
                        'drop_tip' : 'dnase_reaction_mix_transfer_tips',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : 'bottom',
                        'aspirate_seq' : 'dnase_reaction_mix',
                        'aspirate_speed' : 50,
                        'new_well_per_aspirate': False,
                        'aspirate_drip_prevention': {
                            'aspirate_drip_prevention_speed': 10,
                        }
                    },

                    'dispense_parameters':{
                        'dispense_pos': 'bottom',
                        'dispense_seq': 'magnetic_sample_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': True
                    }
                },
                {
                    'name': 'Mix Dnase Reaction Mix with Magbeads',
                    'step':'mix',
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_reaction_mix_mixing_tips',
                        'new_tips_per_mix' : True,
                        'drop_tip' : 'dnase_reaction_mix_mixing_tips',
                    },
                    'mix_parameters':{ 
                        'mix_volume': 30,
                        'mix_cycles': 30,
                        'mix_pos' : {
                            'odd_and_even_mix': False,
                            'odd_mix_pos':[],
                            'even_mix_pos':[],
                            'general_mix_pos' : [[0, 0, 0], [0, 0, 1]]
                        },
                        'mix_seq' : 'magnetic_sample_well',
                        'mix_speed' : 30,
                        'mix_air_gap': {
                            'volume' : 10,
                            'height' : 1
                        }
                    },
                },
                {
                    'name': 'Incubate for 10 Minutes',
                    'step': 'wait',
                    'wait_parameters': {
                        'delay_time': 10,
                        'delay_time_units': 'minutes'
                    }
                },
                {
                    'name': 'Transfer RNA Prep Buffer',
                    'step':'transfer',
                    'transfer_volume': 500,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_rna_prep_buffer_transfer_tips',
                        'new_tips_per_transfer' : False,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : 'bottom',
                        'aspirate_seq' : 'dnase_rna_prep_buffer',
                        'aspirate_speed' : 50,
                        'new_well_per_aspirate': False,
                        'aspirate_drip_prevention': {
                            'aspirate_drip_prevention_speed': 10,
                        }
                    },

                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'magnetic_sample_well',
                        'dispense_speed' : 200,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': True
                    }
                },
                {
                    'name': 'Mix Magbeads with RNA Prep Buffer',
                    'step':'mix',
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_rna_prep_buffer_mixing_tips',
                        'new_tips_per_mix' : True,
                        'drop_tip' : 'dnase_rna_prep_buffer_mixing_tips',
                    },
                    'mix_parameters':{ 
                        'mix_volume': 200,
                        'mix_cycles': 15,
                        'mix_pos' : {
                            'odd_and_even_mix': True,
                            'odd_mix_pos':odd_coordinates,
                            'even_mix_pos':even_coordinates,
                            'general_mix_pos' : []
                        },
                        'mix_seq' : 'magnetic_sample_well',
                        'mix_speed' : 200,
                        'mix_air_gap': {
                            'volume' : 10,
                            'height' : 1
                        }
                    },
                },
                {
                    'name': 'Engage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'engage',
                        'engage_height': magnet_height_from_base
                    }
                },
                {
                    'name': 'Incubate on Magnet for 5 Minutes',
                    'step': 'wait',
                    'wait_parameters': {
                        'delay_time': 5,
                        'delay_time_units': 'minutes'
                    }
                },
                {
                    'name': 'Remove Supernatant',
                    'step' : 'supernatant_removal',
                    'supernatant_removal_volume': 600,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_rna_prep_buffer_supernatant_tips',
                        'new_tips_per_transfer' : True,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : {
                            'odd_and_even_aspirate': True,
                            'odd_aspirate_position':[-1.5, 0, 0],
                            'even_aspirate_position':[1.5, 0, 0],
                            'general_aspiration_position': []
                        },
                        'aspirate_seq' : 'magnetic_sample_well',
                        'new_well_per_aspirate': True,
                        'aspirate_speed' : 25,
                    },
                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'waste_reagent_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': False
                    }
                },
                {
                    'name': 'Disengage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'disengage',
                    }
                },
                # Transfer Ethanol 1
                {
                    'name': 'Transfer Ethanol 1',
                    'step':'transfer',
                    'transfer_volume': 500,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_1_transfer_tips',
                        'new_tips_per_transfer' : False,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : 'bottom',
                        'aspirate_seq' : 'dnase_ethanol',
                        'aspirate_speed' : 100,
                        'new_well_per_aspirate': False,
                        'aspirate_drip_prevention': {
                            'aspirate_drip_prevention_speed': 10,
                        }
                    },

                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'magnetic_sample_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': True
                    }
                },
                {
                    'name': 'Mix Magbeads with Ethanol',
                    'step':'mix',
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_1_mixing_tips',
                        'new_tips_per_mix' : True,
                        'drop_tip' : 'dnase_ethanol_1_mixing_tips',
                    },
                    'mix_parameters':{ 
                        'mix_volume': 200,
                        'mix_cycles': 15,
                        'mix_pos' : {
                            'odd_and_even_mix': True,
                            'odd_mix_pos':odd_coordinates,
                            'even_mix_pos':even_coordinates,
                            'general_mix_pos' : []
                        },
                        'mix_seq' : 'magnetic_sample_well',
                        'mix_speed' : 200,
                        'mix_air_gap': {
                            'volume' : 10,
                            'height' : 1
                        }
                    },
                },
                {
                    'name': 'Engage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'engage',
                        'engage_height': magnet_height_from_base
                    }
                },
                {
                    'name': 'Incubate on Magnet for 5 Minutes',
                    'step': 'wait',
                    'wait_parameters': {
                        'delay_time': 5,
                        'delay_time_units': 'minutes'
                    }
                },
                {
                    'name': 'Remove Supernatant',
                    'step' : 'supernatant_removal',
                    'supernatant_removal_volume': 600,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_1_supernatant_tips',
                        'new_tips_per_transfer' : True,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : {
                            'odd_and_even_aspirate': True,
                            'odd_aspirate_position':[-1.5, 0, 0],
                            'even_aspirate_position':[1.5, 0, 0],
                            'general_aspiration_position': []
                        },
                        'aspirate_seq' : 'magnetic_sample_well',
                        'new_well_per_aspirate': True,
                        'aspirate_speed' : 25,
                    },
                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'waste_reagent_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': False
                    }
                },
                {
                    'name': 'Disengage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'disengage',
                    }
                },
                # Transfer Ethanol 2
                {
                    'name': 'Transfer Ethanol 2',
                    'step':'transfer',
                    'transfer_volume': 500,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_2_transfer_tips',
                        'new_tips_per_transfer' : False,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : 'bottom',
                        'aspirate_seq' : 'dnase_ethanol',
                        'aspirate_speed' : 100,
                        'new_well_per_aspirate': False,
                        'aspirate_drip_prevention': {
                            'aspirate_drip_prevention_speed': 10,
                        }
                    },

                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'magnetic_sample_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': True
                    }
                },
                {
                    'name': 'Mix Magbeads with Ethanol',
                    'step':'mix',
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_2_mixing_tips',
                        'new_tips_per_mix' : True,
                        'drop_tip' : 'dnase_ethanol_2_mixing_tips',
                    },
                    'mix_parameters':{ 
                        'mix_volume': 200,
                        'mix_cycles': 15,
                        'mix_pos' : {
                            'odd_and_even_mix': True,
                            'odd_mix_pos':odd_coordinates,
                            'even_mix_pos':even_coordinates,
                            'general_mix_pos' : []
                        },
                        'mix_seq' : 'magnetic_sample_well',
                        'mix_speed' : 200,
                        'mix_air_gap': {
                            'volume' : 10,
                            'height' : 1
                        }
                    },
                },
                {
                    'name': 'Engage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'engage',
                        'engage_height': magnet_height_from_base
                    }
                },
                {
                    'name': 'Incubate on Magnet for 5 Minutes',
                    'step': 'wait',
                    'wait_parameters': {
                        'delay_time': 5,
                        'delay_time_units': 'minutes'
                    }
                },
                {
                    'name': 'Remove Supernatant',
                    'step' : 'supernatant_removal',
                    'supernatant_removal_volume': 600,
                    'pipette_parameters':{
                        'pipetter' : 'left_pipette',
                        'load_tip': 'dnase_ethanol_2_supernatant_tips',
                        'new_tips_per_transfer' : True,
                        'drop_tip' : 'trash',
                    },
                    'aspirate_parameters':{ 
                        'aspirate_pos' : {
                            'odd_and_even_aspirate': True,
                            'odd_aspirate_position':[-1.5, 0, 0],
                            'even_aspirate_position':[1.5, 0, 0],
                            'general_aspiration_position': []
                        },
                        'aspirate_seq' : 'magnetic_sample_well',
                        'new_well_per_aspirate': True,
                        'aspirate_speed' : 25,
                    },
                    'dispense_parameters':{
                        'dispense_pos': 'top',
                        'dispense_seq': 'waste_reagent_well',
                        'dispense_speed' : 100,
                        'dispense_air_gap':{
                            'volume' : 10,
                            'height' : 1
                        },
                        'new_well_per_dispense': False
                    }
                },
                {
                    'name': 'Disengage Magnet',
                    'step': 'magnet',
                    'magnet_parameters': {
                        'magnet_module': 'magnetic_module',
                        'engage_or_disengage': 'disengage',
                    }
                },
            ]
        },
        # Dry Beads
        {
            'name': 'Incubate to Dry for 20 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 20,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Transfer DNase/RNase Free Water',
            'step':'transfer',
            'transfer_volume': 50,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'dnase_rnase_free_water_transfer_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'dnase_rnase_free_water',
                'aspirate_speed' : 50,
                'new_well_per_aspirate': False,
                'aspirate_drip_prevention': {
                    'aspirate_drip_prevention_speed': 10,
                }
            },

            'dispense_parameters':{
                'dispense_pos': 'bottom',
                'dispense_seq': 'magnetic_sample_well',
                'dispense_speed' : 100,
                'dispense_air_gap':{
                    'volume' : 10,
                    'height' : 1
                },
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Mix Magbeads with DNase/RNase Free Water',
            'step':'mix',
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'dnase_rnase_free_water_mixing_tips',
                'new_tips_per_mix' : True,
                'drop_tip' : 'dnase_rnase_free_water_mixing_tips',
            },
            'mix_parameters':{ 
                'mix_volume': 50,
                'mix_cycles': 15,
                'mix_pos' : {
                    'odd_and_even_mix': False,
                    'odd_mix_pos':[],
                    'even_mix_pos':[],
                    'general_mix_pos' : [[0, 0, 0], [0, 0, 1]]
                },
                'mix_seq' : 'magnetic_sample_well',
                'mix_speed' : 200,
                'mix_air_gap': {
                    'volume' : 10,
                    'height' : 1
                }
            },
        },
        {
            'name': 'Engage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'engage',
                'engage_height': magnet_height_from_base
            }
        },
        {
            'name': 'Incubate on Magnet for 5 Minutes',
            'step': 'wait',
            'wait_parameters': {
                'delay_time': 5,
                'delay_time_units': 'minutes'
            }
        },
        {
            'name': 'Transfer Elution to Elution Plate',
            'step':'transfer',
            'transfer_volume': 50,
            'pipette_parameters':{
                'pipetter' : 'left_pipette',
                'load_tip': 'elution_transfer_tips',
                'new_tips_per_transfer' : True,
                'drop_tip' : 'trash',
            },
            'aspirate_parameters':{ 
                'aspirate_pos' : 'bottom',
                'aspirate_seq' : 'magnetic_sample_well',
                'aspirate_speed' : 10,
                'new_well_per_aspirate': True
            },
            'dispense_parameters':{
                'dispense_pos': 'bottom',
                'dispense_seq': 'elution_sample_well',
                'dispense_speed' : 100,
                'new_well_per_dispense': True
            }
        },
        {
            'name': 'Disengage Magnet',
            'step': 'magnet',
            'magnet_parameters': {
                'magnet_module': 'magnetic_module',
                'engage_or_disengage': 'disengage',
            }
        },

    ]

    def Transfer(transfer_parameters, sample_number):
        # Get Pipette
        pipetter_class = pipette_list[transfer_parameters['pipette_parameters']['pipetter']]
        pipetter = pipetter_class.get_pipette()
        
        # Checks for multichannel or not
        bool_multi = True if pipetter_class.get_type_of_pipette() == 'multi' else False
        
        # Get Loading Pipette Tips
        load_tip_class = tip_sequence[transfer_parameters['pipette_parameters']['load_tip']]
        load_tip_box = load_tip_class.get_pipette_tip_box()
        pipetter_max_transfer_volume = load_tip_class.get_max_pipette_volume()

        # Checks bool_multi to see if it is picking up with a multichannel or single channel
        load_tip_sequence = load_tip_class.get_multi_tips() if bool_multi else load_tip_class.get_single_tips()
        
        # Get Pipette Tip Destination
        if transfer_parameters['pipette_parameters']['drop_tip'] == 'trash':
           drop_tip_sequence = 'trash' 
        else:
            drop_tip_class = tip_sequence[transfer_parameters['pipette_parameters']['drop_tip']]
            drop_tip_box = drop_tip_class.get_pipette_tip_box()
            drop_tip_sequence = drop_tip_class.get_multi_tips() if bool_multi else drop_tip_class.get_single_tips()
        
        #Change Tips or Multi Dispense?
        new_tips_per_transfer = transfer_parameters['pipette_parameters']['new_tips_per_transfer']
        
        #Transfer
        transfer_volume = transfer_parameters['transfer_volume']

        # Aspirate
        aspirate_pos = transfer_parameters['aspirate_parameters']['aspirate_pos']
        aspirate_well_object = labware_well_sequence[transfer_parameters['aspirate_parameters']['aspirate_seq']]
        aspirate_seq = aspirate_well_object.get_multi_wells() if bool_multi else aspirate_well_object.get_single_wells()
        aspirate_labware = aspirate_well_object.get_labware()
        aspirate_speed = transfer_parameters['aspirate_parameters']['aspirate_speed']
        new_well_per_aspirate = transfer_parameters['aspirate_parameters']['new_well_per_aspirate']

        # Dispense
        dispense_pos = transfer_parameters['dispense_parameters']['dispense_pos']
        dispense_well_object = labware_well_sequence[transfer_parameters['dispense_parameters']['dispense_seq']]
        dispense_seq = dispense_well_object.get_multi_wells() if bool_multi else dispense_well_object.get_single_wells()
        dispense_labware = dispense_well_object.get_labware()
        dispense_speed = transfer_parameters['dispense_parameters']['dispense_speed']
        new_well_per_dispense = transfer_parameters['dispense_parameters']['new_well_per_dispense']

        #Number of Transfers
        transfer_total = sample_number if not bool_multi else math.ceil(sample_number/8)
        
        #Optional Parameters
        aspirate_air_gap_bool = False
        aspirate_air_gap_volume = 0
        aspirate_air_gap_height = 0
        if 'aspirate_air_gap' in transfer_parameters['aspirate_parameters']:
            aspirate_air_gap_bool = True
            aspirate_air_gap = transfer_parameters['aspirate_parameters']['aspirate_air_gap']
            aspirate_air_gap_volume = aspirate_air_gap['volume']
            aspirate_air_gap_height = aspirate_air_gap['height']            
        
        aspirate_drip_prevention_bool = False
        aspirate_drip_prevention_speed = 400
        if 'aspirate_drip_prevention' in transfer_parameters['aspirate_parameters']:
            aspirate_drip_prevention_bool = True
            aspirate_drip_prevention = transfer_parameters['aspirate_parameters']['aspirate_drip_prevention']
            aspirate_drip_prevention_speed = aspirate_drip_prevention['aspirate_drip_prevention_speed']
        
        dispense_air_gap_bool = False
        dispense_air_gap_volume = 0
        dispense_air_gap_height = 0
        if 'dispense_air_gap' in transfer_parameters['dispense_parameters']:
            dispense_air_gap_bool = True
            dispense_air_gap = transfer_parameters['dispense_parameters']['dispense_air_gap']
            dispense_air_gap_volume = dispense_air_gap['volume']
            dispense_air_gap_height = dispense_air_gap['height']
            
        dispense_blow_out_bool = False
        if 'dispense_blow_out' in transfer_parameters['dispense_parameters']:
            dispense_blow_out_bool = True
        
        pre_mix_bool = False
        if 'pre_mix_parameters' in transfer_parameters:
            pre_mix_bool = True

            mix_volume = transfer_parameters['pre_mix_parameters']['mix_volume']
            mix_cycle = transfer_parameters['pre_mix_parameters']['mix_cycles']
            mix_speed = transfer_parameters['pre_mix_parameters']['mix_speed']
                
            mix_pos = transfer_parameters['pre_mix_parameters']['mix_pos']
            odd_and_even_mix = mix_pos['odd_and_even_mix']
            if odd_and_even_mix:
                odd_mix_pos = mix_pos['odd_mix_pos']
                even_mix_pos = mix_pos['even_mix_pos']
            else:
                general_mix_pos = mix_pos['general_mix_pos']

        tip_counter = 0
        aspirate_well_count = 0
        dispense_well_count = 0

        pipetter.flow_rate.aspirate = aspirate_speed
        pipetter.flow_rate.dispense = dispense_speed

        while not aspirate_well_object.get_permission_to_use(bool_multi, aspirate_seq[aspirate_well_count], transfer_volume):
            aspirate_well_count += 1
        
        if not new_tips_per_transfer:
            pipetter.pick_up_tip(load_tip_box[load_tip_sequence[tip_counter]])

        for transfer_itter in range(transfer_total):
            if new_tips_per_transfer:
                pipetter.pick_up_tip(load_tip_box[load_tip_sequence[tip_counter]])
            total_vol_transfer = 0

            #Get Aspriate Position
            if aspirate_pos == 'bottom':
                source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom()
            else:
                source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom().move(types.Point(x=aspirate_pos[x], y=aspirate_pos[y], z=aspirate_pos[z]))

            #Get Dispense Position
            if dispense_pos == 'bottom':
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).bottom()
            elif dispense_pos == 'top':
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).top()
            else:
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).bottom().move(types.Point(x=aspirate_pos[x], y=aspirate_pos[y], z=aspirate_pos[z]))

            if pre_mix_bool:
                if pipetter.current_volume != 0:
                    pipetter.dispense(pipetter.current_volume, aspirate_labware.well(aspirate_seq[aspirate_well_count]).top())

                pipetter.flow_rate.aspirate = mix_speed
                pipetter.flow_rate.dispense = mix_speed
                if odd_and_even_mix:
                    if int(mix_seq[mix_itter][-1]) %2 == 0:
                        current_mix_pos = even_mix_pos
                    else:
                        current_mix_pos = odd_mix_pos
                else:
                    current_mix_pos = general_mix_pos
                
                for mix_cycle_count in range(mix_cycle):
                    for mix_coordinates in range(0,len(current_mix_pos),2):
                        pipetter.aspirate(mix_volume, aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom().move(types.Point(x=current_mix_pos[mix_coordinates][0], y=current_mix_pos[mix_coordinates][1], z=current_mix_pos[mix_coordinates][2])))
                        pipetter.dispense(mix_volume, aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom().move(types.Point(x=current_mix_pos[mix_coordinates+1][0], y=current_mix_pos[mix_coordinates+1][1], z=current_mix_pos[mix_coordinates+1][2])))
                pipetter.flow_rate.aspirate = aspirate_speed
                pipetter.flow_rate.dispense = dispense_speed

            while(total_vol_transfer < transfer_volume):
                volume = min(transfer_volume - total_vol_transfer,pipetter_max_transfer_volume)
                total_vol_transfer += volume
                
                if aspirate_pos == 'bottom':
                    source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom()
                else:
                    source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom().move(types.Point(x=aspirate_pos[x], y=aspirate_pos[y], z=aspirate_pos[z]))

                if pipetter.current_volume != 0:
                    pipetter.dispense(pipetter.current_volume, aspirate_labware.well(aspirate_seq[aspirate_well_count]).top())

                pipetter.aspirate(volume, source_position)

                if aspirate_air_gap_bool:
                    pipetter.air_gap(aspirate_air_gap_volume, aspirate_air_gap_height)

                if aspirate_drip_prevention_bool:
                    pipetter.move_to(aspirate_labware.well(aspirate_seq[aspirate_well_count]).top(), speed=aspirate_drip_prevention_speed)


                pipetter.dispense(pipetter.current_volume, destination_position)

                if dispense_blow_out_bool:
                    pipetter.blow_out()
                
                if dispense_air_gap_bool:
                    pipetter.air_gap(dispense_air_gap_volume, dispense_air_gap_height)

                aspirate_well_object.sub_volume(bool_multi, aspirate_seq[aspirate_well_count], volume)
                dispense_well_object.add_volume(bool_multi, dispense_seq[dispense_well_count], volume)

                if not new_well_per_aspirate:
                    if not aspirate_well_object.get_permission_to_use(bool_multi, aspirate_seq[aspirate_well_count], volume):
                        aspirate_well_count += 1
                    
            
            if new_well_per_aspirate:
                aspirate_well_count += 1

            if new_well_per_dispense:
                dispense_well_count += 1
            
            if new_tips_per_transfer:
                if drop_tip_sequence == 'trash':
                    pipetter.drop_tip()
                else:
                    pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])
                tip_counter += 1
        
        if pipetter.has_tip:
            if drop_tip_sequence == 'trash':
                pipetter.drop_tip()
            else:
                pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])

    def Mix(mix_parameters, sample_number):
        # Get Pipette
        pipetter_class = pipette_list[mix_parameters['pipette_parameters']['pipetter']]
        pipetter = pipetter_class.get_pipette()
        
        # Checks for multichannel or not
        bool_multi = True if pipetter_class.get_type_of_pipette() == 'multi' else False
        
        # Get Loading Pipette Tips
        load_tip_class = tip_sequence[mix_parameters['pipette_parameters']['load_tip']]
        load_tip_box = load_tip_class.get_pipette_tip_box()
        pipetter_max_transfer_volume = load_tip_class.get_max_pipette_volume()

        # Checks bool_multi to see if it is picking up with a multichannel or single channel
        load_tip_sequence = load_tip_class.get_multi_tips() if bool_multi else load_tip_class.get_single_tips()

        # Get Pipette Tip Destination
        if mix_parameters['pipette_parameters']['drop_tip'] == 'trash':
           drop_tip_sequence = 'trash' 
        else:
            drop_tip_class = tip_sequence[mix_parameters['pipette_parameters']['drop_tip']]
            drop_tip_box = drop_tip_class.get_pipette_tip_box()
            drop_tip_sequence = drop_tip_class.get_multi_tips() if bool_multi else drop_tip_class.get_single_tips()
        
        #Change Tips or Multi Dispense?
        new_tips_per_mix = mix_parameters['pipette_parameters']['new_tips_per_mix']
        
        mix_volume = mix_parameters['mix_parameters']['mix_volume']
        mix_cycle = mix_parameters['mix_parameters']['mix_cycles']
        mix_speed = mix_parameters['mix_parameters']['mix_speed']

        mix_well_object = labware_well_sequence[mix_parameters['mix_parameters']['mix_seq']]
        mix_seq = mix_well_object.get_multi_wells() if bool_multi else mix_well_object.get_single_wells()
        mix_labware = mix_well_object.get_labware()

        if mix_well_object.get_well_type() == 'individual':
            mix_total = sample_number if not bool_multi else math.ceil(sample_number/8)
        else:
            mix_total = len(mix_well_object.get_multi_wells())
            
        mix_pos = mix_parameters['mix_parameters']['mix_pos']
        odd_and_even_mix = mix_pos['odd_and_even_mix']
        if odd_and_even_mix:
            odd_mix_pos = mix_pos['odd_mix_pos']
            even_mix_pos = mix_pos['even_mix_pos']
        else:
            general_mix_pos = mix_pos['general_mix_pos']

        if 'mix_air_gap' in mix_parameters['mix_parameters']:
            mix_air_gap_bool = True
            mix_air_gap = mix_parameters['mix_parameters']['mix_air_gap']
            mix_air_gap_volume = mix_air_gap['volume']
            mix_air_gap_height = mix_air_gap['height']
        else:
            mix_air_gap_bool = False

        if 'mix_blow_out' in mix_parameters['mix_parameters']:
            mix_blow_out_bool = True
        else:
            mix_blow_out_bool = False

        tip_counter = 0

        current_mix_pos = []

        pipetter.flow_rate.aspirate = mix_speed
        pipetter.flow_rate.dispense = mix_speed

        for mix_itter in range(mix_total):
            if new_tips_per_mix:
                pipetter.pick_up_tip(load_tip_box[load_tip_sequence[tip_counter]])
            if odd_and_even_mix:
                if int(mix_seq[mix_itter][-1]) %2 == 0:
                    current_mix_pos = even_mix_pos
                else:
                    current_mix_pos = odd_mix_pos
            else:
                current_mix_pos = general_mix_pos
            
            if pipetter.current_volume != 0:
                pipetter.dispense(pipetter.current_volume, mix_labware.well(mix_seq[mix_itter]).top())

            for mix_cycle_count in range(mix_cycle):
                for mix_coordinates in range(0,len(current_mix_pos),2):
                    pipetter.aspirate(mix_volume, mix_labware.well(mix_seq[mix_itter]).bottom().move(types.Point(x=current_mix_pos[mix_coordinates][0], y=current_mix_pos[mix_coordinates][1], z=current_mix_pos[mix_coordinates][2])))
                    pipetter.dispense(mix_volume, mix_labware.well(mix_seq[mix_itter]).bottom().move(types.Point(x=current_mix_pos[mix_coordinates+1][0], y=current_mix_pos[mix_coordinates+1][1], z=current_mix_pos[mix_coordinates+1][2])))
        
            if mix_air_gap_bool:
                pipetter.air_gap(mix_air_gap_volume, mix_air_gap_height)
            
            if mix_blow_out_bool:
                pipetter.blow_out()
            
            if new_tips_per_mix:
                if drop_tip_sequence == 'trash':
                    pipetter.drop_tip()
                else:
                    pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])
                tip_counter += 1
                
        
        if pipetter.has_tip:
            if drop_tip_sequence == 'trash':
                pipetter.drop_tip()
            else:
                pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])

    def Wait(wait_parameters):
        delay_time = wait_parameters['wait_parameters']['delay_time']
        delay_time_units = wait_parameters['wait_parameters']['delay_time_units']
        if delay_time_units == 'minutes':
            protocol.delay(minutes = delay_time)
        elif delay_time_units == 'hours':
            protocol.delay(hours = delay_time)
        elif delay_time_units == 'seconds':
            protocol.delay(seconds = delay_time)

    def Magnet(magnet_parameters):
        magnet_module = module_list[magnet_parameters['magnet_parameters']['magnet_module']].get_module()
        engage_or_disengage = magnet_parameters['magnet_parameters']['engage_or_disengage']

        if engage_or_disengage == 'engage':
            engage_height = magnet_parameters['magnet_parameters']['engage_height']
            magnet_module.engage(height_from_base=engage_height)
        else:
            magnet_module.disengage()

    def Supernatant_Removal(supernatant_removal_parameters, sample_number):
        pipetter_class = pipette_list[supernatant_removal_parameters['pipette_parameters']['pipetter']]
        pipetter = pipetter_class.get_pipette()
        
        # Checks for multichannel or not
        bool_multi = True if pipetter_class.get_type_of_pipette() == 'multi' else False
        
        # Get Loading Pipette Tips
        load_tip_class = tip_sequence[supernatant_removal_parameters['pipette_parameters']['load_tip']]
        load_tip_box = load_tip_class.get_pipette_tip_box()
        pipetter_max_transfer_volume = load_tip_class.get_max_pipette_volume()

        # Checks bool_multi to see if it is picking up with a multichannel or single channel
        load_tip_sequence = load_tip_class.get_multi_tips() if bool_multi else load_tip_class.get_single_tips()

        # Get Pipette Tip Destination
        if supernatant_removal_parameters['pipette_parameters']['drop_tip'] == 'trash':
           drop_tip_sequence = 'trash' 
        else:
            drop_tip_class = tip_sequence[supernatant_removal_parameters['pipette_parameters']['drop_tip']]
            drop_tip_box = drop_tip_class.get_pipette_tip_box()
            drop_tip_sequence = drop_tip_class.get_multi_tips() if bool_multi else drop_tip_class.get_single_tips()
        
        #Change Tips or Multi Dispense?
        new_tips_per_transfer = supernatant_removal_parameters['pipette_parameters']['new_tips_per_transfer']
        
        #Transfer
        supernatant_removal_volume = supernatant_removal_parameters['supernatant_removal_volume']

        # Aspirate
        aspirate_pos = supernatant_removal_parameters['aspirate_parameters']['aspirate_pos']
        odd_and_even_aspirate = aspirate_pos['odd_and_even_aspirate']
        if odd_and_even_aspirate:
            odd_aspirate_position = aspirate_pos['odd_aspirate_position']
            even_aspirate_position = aspirate_pos['even_aspirate_position']
        else:
            general_aspirate_position = aspirate_pos['general_aspiration_position']
        aspirate_well_object = labware_well_sequence[supernatant_removal_parameters['aspirate_parameters']['aspirate_seq']]
        aspirate_seq = aspirate_well_object.get_multi_wells() if bool_multi else aspirate_well_object.get_single_wells()
        aspirate_labware = aspirate_well_object.get_labware()
        aspirate_speed = supernatant_removal_parameters['aspirate_parameters']['aspirate_speed']
        new_well_per_aspirate = supernatant_removal_parameters['aspirate_parameters']['new_well_per_aspirate']

        # Dispense
        dispense_pos = supernatant_removal_parameters['dispense_parameters']['dispense_pos']
        dispense_well_object = labware_well_sequence[supernatant_removal_parameters['dispense_parameters']['dispense_seq']]
        dispense_seq = dispense_well_object.get_multi_wells() if bool_multi else dispense_well_object.get_single_wells()
        dispense_labware = dispense_well_object.get_labware()
        dispense_speed = supernatant_removal_parameters['dispense_parameters']['dispense_speed']
        new_well_per_dispense = supernatant_removal_parameters['dispense_parameters']['new_well_per_dispense']

        #Number of Transfers
        supernatant_removal_total = sample_number if not bool_multi else math.ceil(sample_number/8)
        
        pipetter.flow_rate.aspirate = aspirate_speed
        pipetter.flow_rate.dispense = dispense_speed

        #Optional Parameters
        if 'aspirate_air_gap' in supernatant_removal_parameters['aspirate_parameters']:
            aspirate_air_gap_bool = True
            aspirate_air_gap = supernatant_removal_parameters['aspirate_parameters']['aspirate_air_gap']
            aspirate_air_gap_volume = aspirate_air_gap['volume']
            aspirate_air_gap_height = aspirate_air_gap['height']
        else:
            aspirate_air_gap_bool = False
            aspirate_air_gap_volume = 0
            aspirate_air_gap_height = 0
        
        if 'dispense_air_gap' in supernatant_removal_parameters['dispense_parameters']:
            dispense_air_gap_bool = True
            dispense_air_gap = supernatant_removal_parameters['dispense_parameters']['dispense_air_gap']
            dispense_air_gap_volume = dispense_air_gap['volume']
            dispense_air_gap_height = dispense_air_gap['height']
        else:
            dispense_air_gap_bool = False
            dispense_air_gap_volume = 0
            dispense_air_gap_height = 0
        
        if 'dispense_blow_out' in supernatant_removal_parameters['dispense_parameters']:
            dispense_blow_out_bool = True
        else:
            dispense_blow_out_bool = False

        tip_counter = 0
        aspirate_well_count = 0
        dispense_well_count = 0
        
        if not new_tips_per_transfer:
            pipetter.pick_up_tip(load_tip_box[load_tip_sequence[tip_counter]])

        for supernatant_itter in range(supernatant_removal_total):
            if new_tips_per_transfer:
                pipetter.pick_up_tip(load_tip_box[load_tip_sequence[tip_counter]])
            total_vol_transfer = 0

            #Get Aspriate Position

            if odd_and_even_aspirate:
                if int(aspirate_seq[supernatant_itter][-1])%2 == 0:
                    current_aspirate_pos = even_aspirate_position
                else:
                    current_aspirate_pos = odd_aspirate_position
            else:
                current_aspirate_pos = general_aspirate_position

            if aspirate_pos == 'bottom':
                source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom()
            else:
                source_position = aspirate_labware.well(aspirate_seq[aspirate_well_count]).bottom().move(types.Point(x=current_aspirate_pos[0], y=current_aspirate_pos[1], z=current_aspirate_pos[2]))

            #Get Dispense Position
            if dispense_pos == 'bottom':
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).bottom()
            elif dispense_pos == 'top':
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).top()
            else:
                destination_position = dispense_labware.well(dispense_seq[dispense_well_count]).bottom().move(types.Point(x=aspirate_pos[x], y=aspirate_pos[y], z=aspirate_pos[z]))

            while(total_vol_transfer < supernatant_removal_volume):
                volume = min(supernatant_removal_volume - total_vol_transfer,pipetter_max_transfer_volume)
                total_vol_transfer += volume
                
                if pipetter.current_volume != 0:
                    pipetter.dispense(pipetter.current_volume, aspirate_labware.well(aspirate_seq[aspirate_well_count]).top())

                pipetter.aspirate(volume, source_position)

                if aspirate_air_gap_bool:
                    pipetter.air_gap(aspirate_air_gap_volume, aspirate_air_gap_height)

                pipetter.dispense(pipetter.current_volume, destination_position)

                if dispense_blow_out_bool:
                    pipetter.blow_out()
                
                if dispense_air_gap_bool:
                    pipetter.air_gap(dispense_air_gap_volume, dispense_air_gap_height)
                    
            aspirate_well_object.sub_volume(bool_multi, aspirate_seq[aspirate_well_count], supernatant_removal_volume)
            dispense_well_object.add_volume(bool_multi, dispense_seq[dispense_well_count], supernatant_removal_volume)
            
            if new_well_per_aspirate:
                aspirate_well_count += 1
            
            if new_well_per_dispense:
                dispense_well_count += 1
            
            if new_tips_per_transfer:
                if drop_tip_sequence == 'trash':
                    pipetter.drop_tip()
                else:
                    pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])
                tip_counter += 1
        
        if pipetter.has_tip:
            if drop_tip_sequence == 'trash':
                pipetter.drop_tip()
            else:
                pipetter.drop_tip(drop_tip_box[drop_tip_sequence[tip_counter]])



        
    step_counter = 1
    for step in procedure:
        if step['step'] == 'DNase Treatment':
            if dnase_treatment:
                for dnase_step in step['dnase_procedure']:
                    protocol.comment(f"Step {step_counter} {dnase_step['step']}: {dnase_step['name']}")
                    protocol.comment("")
                    step_counter +=1
                    if dnase_step['step'] == 'transfer':
                        Transfer(dnase_step, sample_number)
                    elif dnase_step['step'] == 'mix':
                        Mix(dnase_step, sample_number)
                    elif dnase_step['step'] == 'wait':
                        Wait(dnase_step)
                    elif dnase_step['step'] == 'magnet':
                        Magnet(dnase_step)
                    elif dnase_step['step'] == 'supernatant_removal':
                        Supernatant_Removal(dnase_step, sample_number)
            else:
                continue
            
            continue

        if step['step'] == 'sample_transfer':
            if sample_transfer_step:
                step['step'] = 'transfer'
            else:
                continue

        protocol.comment(f"Step {step_counter} {step['step']}: {step['name']}")
        protocol.comment("")
        step_counter +=1
        if step['step'] == 'transfer':
            Transfer(step, sample_number)
        elif step['step'] == 'mix':
            Mix(step, sample_number)
        elif step['step'] == 'wait':
            Wait(step)
        elif step['step'] == 'magnet':
            Magnet(step)
        elif step['step'] == 'supernatant_removal':
            Supernatant_Removal(step, sample_number)
