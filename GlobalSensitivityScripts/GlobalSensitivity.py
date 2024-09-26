import sys
import os
import csv

# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from numpy.random import randint, seed
from numpy import zeros, tril, vstack, ones, ndarray,empty, mean
from functools import reduce
from operator import getitem
from copy import deepcopy
from OptimisationScripts.OptimisationModel import OptimModel
from pyomo.environ import value as pyomo_value
from math import isnan
from os import getcwd,chdir
from pickle import dump, load
from ClusteringScripts.Kmeans import save_csv
import ast

def expand_key(key_str):
    """
    Convert a string representation of a tuple into a list of keys.
    """
    # Safely evaluate the string as a Python tuple
    try:
        return list(ast.literal_eval(key_str))
    except (SyntaxError, ValueError):
        return [key_str]  # In case the eval fails, return the original string as a single-element list

def get_top_n_keys(filename, folder, n=None):
    # Combine the folder and filename to get the full file path
    csv_file = os.path.join(folder, filename)
    
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    
    # Read the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        
        # Extract data and convert keys from strings to lists
        data = [(expand_key(row[0]), float(row[1])) for row in reader]
    
    # Determine how many top items to return
    if n is None:
        n = len(data)
    
    # Sort the data by values in descending order and get the top n keys
    top_n_data = sorted(data, key=lambda x: x[1], reverse=True)[:n]
    
    # Separate the keys and values for the top n data
    top_n_keys = [item[0] for item in top_n_data]
    top_n_values = [item[1] for item in top_n_data]
    
    # Return the top n keys and their corresponding values
    return top_n_keys, top_n_values


def filter_dict(data_dict, filtering_parameter):
    filtered_dict = {k: v for k, v in data_dict.items() 
                     if not (isinstance(v, float) and isnan(v)) and v >= filtering_parameter}
    return filtered_dict

def remove_keys_from_nested_dict(nested_dict, keys_to_remove):
    def recurse(d):
        if isinstance(d, dict):
            keys_to_delete = []
            for key, value in d.items():
                if isinstance(value, dict):
                    recurse(value)  # Recursively call function for nested dictionary
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            recurse(item)  # Recursively call function for nested dictionary in list
                if key in keys_to_remove:
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del d[key]
    
    recurse(nested_dict)
    return nested_dict

def tuple_to_nested_dict(input_dict):

    nested_dict = {}
    
    for key_tuple, value in input_dict.items():
        current_level = nested_dict
        for part in key_tuple[:-1]:  
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[key_tuple[-1]] = value  
    
    return nested_dict

def getFromDict(dataDict, mapList):
    return reduce(getitem, mapList, dataDict)

def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

def build_param_dict(parameters,keys,pertubation_vector,tuple_keys,key):
    param_vector = empty(len(keys))
    
    for i in range(len(keys)):
        bounds = getFromDict(parameters, keys[i])
        value = (bounds[-1] - bounds[0]) * pertubation_vector[i] + bounds[0]
        param_vector[i] = value
        setInDict(parameters, keys[i], value)
    if tuple_keys is None:
        pass
    else:
        for i in range(len(tuple_keys)):
            try:
                bounds = getFromDict(parameters, keys[i])
                value = bounds[1]
                setInDict(parameters, keys[i], value)
            except Exception as _:
                pass

    return(parameters,param_vector)

def wrap_around_bounds(nested_list):
    for i in range(len(nested_list)):
        if isinstance(nested_list[i], list and ndarray):
            nested_list[i] = wrap_around_bounds(nested_list[i])
        else:
            if nested_list[i] > 1:
                nested_list[i] -= 1
    return(nested_list)            
    
def get_k_value(parameters,heirarchy=[],stored_keys=[]):
    for key,value in parameters.items():
        if isinstance(value,int or float or bool):
            pass
        elif isinstance(value,tuple):
            temp = heirarchy.copy()
            temp.append(key)
            stored_keys.append(temp)
        elif isinstance(value, dict):
            heirarchy.append(key)
            heirarchy, stored_keys = get_k_value(value,heirarchy,stored_keys)
    heirarchy = heirarchy[:-1]
    return heirarchy, stored_keys

class GSA:
    instance = None
    def __init__(self,params,param_grid=4,number_trajectories=200,keys_list = None,randomseed = 42, EE = True, OAT = False,label=''):
        seed(randomseed)
        parameters = remove_keys_from_nested_dict(deepcopy(params),[key for key, value in params['booleans']['vector_choice'].items() if not value])
        self.parameters = parameters
        self.param_grid = param_grid
        self.number_trajectories = number_trajectories
        self.increment = param_grid / (2*(param_grid-1))
        self.label= label
        blank,tuple_keys = get_k_value(parameters)
	
        if keys_list is None:
            self.keys_list = tuple_keys
            self.tuple_keys = None
        else:
            self.keys_list = keys_list
            self.tuple_keys = tuple_keys
        
        if EE:
            self.generate_trajectories()
            self.build_models()
        elif OAT:
            self.one_at_a_time_analysis()



    def generate_trajectories(self):
        K = len(self.keys_list)
        
        starting_points = randint(0,(self.param_grid - 1),(self.number_trajectories,K))/(self.param_grid -1)
        trajectories = zeros((self.number_trajectories,K+1,K))
        pertubation_vector = vstack((zeros((1, K)), tril(ones((K, K)))))
        pertubation_vector *= self.increment

        for k in range(self.number_trajectories):
            for j in range(K+1):
                for i in range(K):
                    trajectories[k,j,i] = starting_points[k,i] + pertubation_vector[j,i]

        self.trajectories = wrap_around_bounds(trajectories)
        pass



    def build_models(self):
        self.param_dicts = empty((self.number_trajectories,len(self.keys_list)+1),dtype=object)
        self.pertubations = empty((self.number_trajectories,len(self.keys_list)),dtype=object)
        self.models = empty((self.number_trajectories,len(self.keys_list)+1),dtype=object)
        self.pertubation_dict = [{} for _ in range(self.number_trajectories)]
        self.unit_pertubations =  empty((self.number_trajectories,len(self.keys_list)),dtype=object)

        with open(f'SolverLogs/{self.label}_EE.log', 'w') as file:
            file.write('')

        for k in range(self.number_trajectories):
            key = 'initial'
            old_param_vector = zeros(len(self.keys_list))
            for j in range(len(self.keys_list)+1):
                params = self.parameters.copy()
                self.param_dicts[k][j],param_vector = build_param_dict(deepcopy(params),self.keys_list,self.trajectories[k][j],self.tuple_keys,key)
                if j >= 1:
                    self.pertubation_dict[k][tuple(key) if isinstance(key,list) else key] = sum([param_vector[i] - old_param_vector[i] for i in range(len(param_vector))]) 
                    self.pertubations[k][j-1] = sum([param_vector[i] - old_param_vector[i] for i in range(len(param_vector))]) 
                    self.unit_pertubations[k][j-1] = sum([self.trajectories[k][j][i] - self.trajectories[k][j-1][i] for i in range(len(self.trajectories[k][j]))])
                old_param_vector = param_vector
                self.models[k][j] = OptimModel(deepcopy(self.param_dicts[k][j]),key=f'{self.label}_Trajectory_{k}_Parameter_{j}').build_model()
                with open(f'SolverLogs/{self.label}_EE.log', 'a') as file:
                    file.write(f'{self.label}_Trajectory_{k}_Parameter_{j}' +'\n')
                if j < len(self.keys_list):
                    key = self.keys_list[j]
                
        dir = getcwd()
        chdir(dir+'/PreSolvedModels')        
        open(f'{self.label}_GSA_Class_EE.pickle', 'a').close()
        with open(f'{self.label}_GSA_Class_EE.pickle', 'wb') as f:
            dump(self, f)
        chdir(dir)
        pass

    def solve_models(self):
        self.LCOHs = empty((self.number_trajectories,len(self.keys_list)+1),dtype=float)

        for k in range(self.number_trajectories):
            for j in range(len(self.keys_list)+1):
                self.models[k,j] = OptimModel.get_solve(key = f'Trajectory_{k}_Parameter_{j}')
                self.LCOHs[k,j] = pyomo_value(self.models[k,j].instance.LCOH)
        pass

    @classmethod
    def elementary_effect_analysis(cls,key):
        cls.label = key
        if cls.instance is None:
            dir = getcwd()
            chdir(dir+'/PreSolvedModels')
            with open(key+'_GSA_Class_EE.pickle', 'rb') as f:
                cls = load(f)
            chdir(dir)

        cls.EEs = empty((cls.number_trajectories,len(cls.keys_list)),dtype=float)
        cls.means = empty(len(cls.keys_list))
        cls.stds = empty(len(cls.keys_list))
        cls.mean_abs = empty(len(cls.keys_list))
        cls.mean_scaled = empty(len(cls.keys_list))
        cls.LCOHs = empty((cls.number_trajectories,len(cls.keys_list)+1),dtype=float)

        sol_dict = {}
        LCOH_dict = {}
        for k in range(cls.number_trajectories):
            for j in range(0,len(cls.keys_list)+1):
                key = f'{cls.label}_Trajectory_{k}_Parameter_{j}'
                cls.models[k,j] = OptimModel.get_solve(key = key,reinitialise=True)
                cls.LCOHs[k,j] = pyomo_value(OptimModel.get_solve(key=key,reinitialise=True).instance.LCOH)
                LCOH_dict[(k,j)] = cls.LCOHs[k,j]
                if j == 0:
                    pass
                else:
                    cls.EEs[k,j-1] = (cls.LCOHs[k,j] - cls.LCOHs[k,j-1]) / cls.unit_pertubations[k,j-1]
                    print(key, cls.LCOHs[k,j],cls.LCOHs[k,j-1],cls.unit_pertubations[k,j-1])

        for j in range(len(cls.keys_list)):
            cls.means[j] = mean(cls.EEs[:,j])
            cls.mean_abs[j] = mean(abs(cls.EEs[:,j]))
            sol_dict[tuple(cls.keys_list[j]) if isinstance(cls.keys_list[j],list) else cls.keys_list[j]] = cls.mean_abs[j]
        save_csv(sol_dict,f'{cls.label}_EE_Analysis','DataAnalysis')
        save_csv(LCOH_dict,f'{cls.label}_EE_LCOH_Values','DataAnalysis')
        pass

    def one_at_a_time_analysis(self):
        
        self.param_dicts    = empty((len(self.keys_list),self.param_grid),dtype=object)
        self.models         = empty((len(self.keys_list),self.param_grid),dtype=object)

        with open(f'SolverLogs/{self.label}_OAT.log', 'w') as file:
            file.write('')

        for i in range(len(self.keys_list)): 
            for j in range(self.param_grid):
                key = self.label+f'{i}_{j}'
                self.param_dicts[i,j] = deepcopy(self.parameters)
                bounds = getFromDict(self.param_dicts[i,j],self.keys_list[i])
                value = (bounds[-1] - bounds[0]) * (j/(self.param_grid-1)) + bounds[0]
                setInDict(self.param_dicts[i,j], self.keys_list[i], value)
                print(key,deepcopy(self.param_dicts[i][j]))
                self.models[i][j] = OptimModel(deepcopy(self.param_dicts[i][j]),key=key).build_model()
                with open(f'SolverLogs/{self.label}_OAT.log', 'a') as file:
                    file.write(key +'\n')

        dir = getcwd()
        chdir(dir+'/PreSolvedModels')        
        open(f'{self.label}_GSA_Class.pickle', 'a').close()
        with open(f'{self.label}_GSA_Class.pickle', 'wb') as f:
            dump(self, f)
        chdir(dir)


    @classmethod
    def solve_models_OAT(cls,key):
        cls.label = key
        if cls.instance is None:
            dir = getcwd()
            chdir(dir+'/PreSolvedModels')
            with open(key+'_GSA_Class.pickle', 'rb') as f:
                cls = load(f)
            chdir(dir)

        cls.LCOHs = empty((len(cls.keys_list),cls.param_grid),dtype=float)
        cls.EE = empty((len(cls.keys_list),cls.param_grid-1),dtype=float)
        cls.mean_EE = empty(len(cls.keys_list))
        sol_dict = {}

        for i in range(len(cls.keys_list)):
            for j in range(cls.param_grid):
                key = cls.label+f'{i}_{j}'
                cls.models[i,j] = OptimModel.get_solve(key = key,reinitialise=True)
                cls.LCOHs[i,j] = pyomo_value(OptimModel.get_solve(key=cls.label+f'{i}_{j}',reinitialise=True).instance.LCOH)
                if j >= 1:
                    cls.EE[i,j-1] = cls.LCOHs[i,j] - cls.LCOHs[i,j-1]
                    
            cls.mean_EE[i] = mean(abs(cls.EE[i,:]))
            sol_dict[tuple(cls.keys_list[i]) if isinstance(cls.keys_list[i],list) else cls.keys_list[i]] = cls.mean_EE[i]
        #cls.sol_dict = filter_dict(sol_dict, 10e-6)
        cls.sol_dict = sol_dict
        save_csv(cls.sol_dict,f'{cls.label}_OAT_Analysis','DataAnalysis')
        pass

