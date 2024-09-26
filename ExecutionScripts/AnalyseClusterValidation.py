import sys
import os
import matplotlib.pyplot as plt
from pyomo.environ import value as pyomo_value
from numpy import mean
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams, cycler
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np
# Example: Create a simple custom colormap
colors =  ["#232333",
                "#000080",
                "#DC143C", 
                    "#0000CD",
                    "#008080",
                    "#232333", 
                    "#C71585", 
                    
                    "#006400",
                    "#40E0D0", 
                    "#EE82EE",
                    "#7B68EE", 
                    "#FF0000",
                    "#FF8C00", 
                    "#00FF7F", 
                    "#F5F5F5", 
                    "#00BFFF",
                    "#F0E68C",
                    "#AFEEEE",
                    "#FFB6C1",
                    "#E6E6FA", 
                    "#FA8072", 
                    "#FFA500", 
                    "#98FB98"
                    ]

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['CMU Serif'] + rcParams['font.serif']
rcParams['axes.prop_cycle'] = cycler(color=colors)
# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../') 
sys.path.append(module_folder_path)

from OptimisationScripts.OptimisationModel import OptimModel
dir = os.getcwd()

clusters = [20,50,100,250,500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250,5500,5750,6000,6250,6500,6750,7000,7250,7500,7750,8000]
NH3clusters = [clusters[i] for i in range(len(clusters)) if clusters[i] not in [1750,3500,5250,4500,4250,4750,5250,5500,5750,6500,6750,7000,7500,7750,8000]]
LH2clusters = [clusters[i] for i in range(len(clusters)) if clusters[i] not in [500,3500,4250,4500,5500,5750,6250,6500,7000,7250,7500,7750,8000]]
NH3LCOHs = []
vector = 'NH3'
for i in NH3clusters:
    key = f'Cluster_Val_{vector}_Reconversion-True_Grid-True_{i}'
    try:
        os.chdir(dir)
        model_instance = OptimModel.get_solve(key=key, reinitialise=True).instance
        NH3LCOHs.append([i, pyomo_value(model_instance.LCOH)])
        os.chdir(dir)
    except Exception as e:
        os.chdir(dir)
        # Print the error and the problematic cluster value
        print(f"Failed at cluster {i} with error: {e}")
        # Optional: Add additional debugging information
        import traceback
        traceback.print_exc()
        os.chdir(dir)
        continue
LH2LCOHs = []
vector = 'LH2'
for i in LH2clusters:
    key = f'Cluster_Val_{vector}_Reconversion-True_Grid-True_{i}'
    try:
        model_instance = OptimModel.get_solve(key=key, reinitialise=True).instance
        LH2LCOHs.append([i, pyomo_value(model_instance.LCOH)])
    except Exception as e:
        # Print the error and the problematic cluster value
        print(f"Failed at cluster {i} with error: {e}")
        # Optional: Add additional debugging information
        import traceback
        traceback.print_exc()
        continue

errNH3 = [5 for i in range(len(NH3clusters))]
errLH2 = [5 for i in range(len(LH2clusters))]

print(len(NH3LCOHs),len(NH3clusters))
print(len(LH2LCOHs),len(LH2clusters))

print(NH3LCOHs)
print(LH2LCOHs)
plt.figure(figsize=(10, 5))
plt.errorbar([i[0] for i in NH3LCOHs],[i[1] for i in NH3LCOHs]/(mean([i[1] for i in NH3LCOHs])),yerr=[[NH3LCOHs[i][1]*errNH3[i]/100 for i in range(len(NH3LCOHs))],[0]*len(NH3LCOHs)]/(mean([i[1] for i in NH3LCOHs])),capsize=5,fmt='-o',label='NH3')
plt.errorbar([i[0] for i in LH2LCOHs],[i[1] for i in LH2LCOHs]/(mean([i[1] for i in LH2LCOHs])),yerr=[[LH2LCOHs[i][1]*errLH2[i]/100 for i in range(len(LH2LCOHs))],[0]*len(LH2LCOHs)]/(mean([i[1] for i in LH2LCOHs])),capsize=5,fmt='-o',label='LH2')

plt.legend()
plt.ylim(bottom=0,top = 1.05)
plt.ylabel('Normalised LCOH [-]')
plt.xlabel('Number of Clusters')
plt.show()
