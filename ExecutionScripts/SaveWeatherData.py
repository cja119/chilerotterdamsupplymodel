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
from ClusteringScripts.Kmeans import *
from OptimisationScripts.OptimisationModel import OptimModel
from PreOptimisationDataStore.DefaultParameters import Default_Params
from pyomo.environ import value as pyomo_value
from os import getcwd,chdir
from pickle import dump,load

points = [(-57,-68),(-56,-67),(-55.33,-70.33),(-55.33,-71.33)]
start_date   =  np.datetime64('2022-01-01', 'ns') 
end_date     = np.datetime64('2023-01-01', 'ns') 

weatherdata = Meteorological(date = (start_date,end_date),
                                location= 'Coastal Chile', 
                                wind = True,
                                solar = False, 
                                interval = 3600,
                                storage_location ="./WeatherData", 
                                n_samp = 100, 
                                sample_type = "Structured", 
                                latitudes =(-57, -55.33), 
                                longitudes =(-71.33, -67)
                                )

renewableenergy =    RenewableEnergy(weatherdata,
                                        points,
                                        [(0,0.0),       # These are points along the power curve. 
                                            (3,0.0),       # are used in the ouput curve.
                                            (4,0.648),     # Wind speeds are in [m/s].
                                            (5,1.4832),
                                            (6,2.736),
                                            (7,4.4676),  
                                            (8,6.7104),
                                            (9,9.3168),
                                            (10,11.2392),
                                            (11,11.8008),
                                            (12,11.8728),
                                            (13,11.88),
                                            (30,11.88),
                                            ]
                                            )
df = pd.DataFrame(renewableenergy.power_output)

dir = getcwd()
chdir(dir+'/PreOptimisationDataStore')
open('WeatherData.pickle', 'a').close()
with open('WeatherData.pickle', 'wb') as f:
    dump(df, f)
chdir(dir) 