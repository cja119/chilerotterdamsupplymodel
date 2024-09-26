import sys
import os

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)


from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd
from MeteorologicalScripts.GetWeatherData import Meteorological
from MeteorologicalScripts.RenwableEnergyModelling import RenewableEnergy
from MeteorologicalScripts.DemandProfile import *
from ClusteringScripts.Wards_Method import *
from ClusteringScripts.Kmeans import *
from OptimisationScripts.OptimisationModel import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params
from pyomo.environ import value as pyomo_value
from os import getcwd,chdir
from pickle import dump,load

clusters = [20,50,100,250,500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250,5500,5750,6000,6250,6500,6750,7000,7250,7500,7750,8000]
if sys.argv[2] == 'LH2':
    clusters = [3500,4250,4500,5500,5750,6250,6500,7000,7250,7500,7750,8000]
else:
    clusters = [1750,3500,5250,4500,4750,5250,5500,5750,6500,6750,7500,7750,8000]

start_date   =  np.datetime64('2022-01-01', 'ns') 
end_date     = np.datetime64('2023-01-01', 'ns') 
K = clusters[int(sys.argv[5])-1]

dir = getcwd()
chdir(dir+'/PreOptimisationDataStore')
with open('WeatherData.pickle', 'rb') as f:
    df = load(f)
chdir(dir)

clustered_array = consecutive_clustering(df,K,'medoid')

predictions = [item for i in clustered_array for item in [i[0]] * int(i[1])]
predictions.append(predictions[-1])

clustered_times = [[0,0]]
for i in range(1,len(clustered_array)+1):
    clustered_times.append([int(clustered_times[i-1][1]+clustered_times[i-1][0]),int(clustered_array[i-1][1])])

stacked_array  = generate_stacked_array(start_date,end_date,200,8,360)
time_array = insert_array(stacked_array,np.array(clustered_times[1:]))
wind_speed = []

for t in time_array:
    wind_speed.append(predictions[t[0]])


demand_signal = Demand_profle(number_points = time_array[-1,0]+1 ,
                            number_time_steps = 50,
                            peak_seasonal_demand =0.25,
                            net_frequency = 1,
                            net_ramp = 0.2,
                            baseline = 1,
                            net_demand = 8.16*10**(8)/425.445/7,
                            stochasticity = 0.2,
                            amplitude = 0.2
                            )

save_csv(time_array[:,0],'time_data.csv')
save_csv(time_array[:,1],'time_duration.csv')
save_csv(wind_speed,'wind_speed.csv')
sampled_signal = [demand_signal.interpolate[i] for i in time_array[:,0]]
save_csv(sampled_signal, 'demand_signal.csv')

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
model = OptimModel(parameters, key=f'{sys.argv[4]}_{K}')
model.solve(key=f'{sys.argv[4]}_{K}')
