import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from GlobalSensitivityScripts.GlobalSensitivity import GSA

GSA.elementary_effect_analysis(sys.argv[1])