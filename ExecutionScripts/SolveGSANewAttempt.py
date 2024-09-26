import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel

solve = OptimModel.class_solve(key=sys.argv[1], feasibility=float(sys.argv[2]),optimality=float(sys.argv[3]),mip_percentage=int(sys.argv[4]),random_seed=int(sys.argv[5])) 

