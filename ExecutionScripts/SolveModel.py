import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel

solve = OptimModel.class_solve(key=sys.argv[1], feasibility = 1e-5, optimality = 1e-8, mip_percentage = 5, random_seed=7827382,parallel=False)
solve.generate_plots(solve)
