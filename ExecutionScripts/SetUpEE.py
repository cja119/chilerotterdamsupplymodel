import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from GlobalSensitivityScripts.GlobalSensitivity import GSA, get_top_n_keys
from PreOptimisationDataStore.DefaultParameters import Default_Params

keys_list, _ = get_top_n_keys(filename=sys.argv[4]+'_OAT_Analysis',folder='DataAnalysis', n=int(sys.argv[5]))
print(keys_list)


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
parameters['shipping_regularity'] = 200
parameters['booleans'] = booleans

global_sens = GSA(parameters,
                  param_grid=4,
                  number_trajectories=int(sys.argv[6]),
                  keys_list = keys_list,
                  randomseed = 42,
                  EE = True, 
                  OAT = False,
		  label=sys.argv[4])

