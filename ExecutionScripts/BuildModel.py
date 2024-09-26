import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params

booleans = {'vector_choice':{'LH2':True if sys.argv[2] == 'LH2' else False,
                                'NH3':True if sys.argv[2] == 'NH3' else False
                                },
                'ship_sizes':{'small':True,
                            'medium':True,
                            'large':True
                            },
                'electrolysers':{'alkaline':True,
                                'PEM':True,
                                'SOFC':True
                                },
                'grid_connection':sys.argv[3].lower() in ['True','true', '1', 'yes'],
                'fuel_cell':True,
                'battery_storage':True,
                'reconversion':sys.argv[1].lower() in ['True','true', '1', 'yes'],
                'relaxed_ramping':False
                }

parameters = Default_Params().formulation_parameters
parameters['booleans'] = booleans
parameters['shipping_regularity'] = 200
model = OptimModel(parameters, key=sys.argv[4])

    
