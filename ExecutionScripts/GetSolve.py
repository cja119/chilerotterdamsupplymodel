import sys
import os
from pyomo.environ import value as pyomo_value

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel

key = sys.argv[1]

solved_model_1 = OptimModel.get_solve(key)
solved_model_1.generate_plots(solved_model_1,sankey_height=700,sankey_threshold=2*10**-3,LCOH_threshold=0.01)
print(pyomo_value(solved_model_1.instance.LCOH))
