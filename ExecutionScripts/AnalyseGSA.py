import sys
import os
import ast
import numpy as np
import matplotlib.pyplot as plt 
# Get the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
module_folder_path = os.path.join(current_dir, '../')
sys.path.append(module_folder_path)

from csv import DictReader
from os import path
from sklearn.cluster import KMeans
from GlobalSensitivityScripts.GlobalSensitivity import filter_dict
def combine_tuple_elements(tup):
    result = []
    for item in tup:
        if isinstance(item, tuple):
            result.append(combine_tuple_elements(item)) 
        elif isinstance(item, str):
            result.append(item)
        else:
            raise ValueError("Tuple elements must be either strings or tuples of strings.")
    
    return ' '.join(result)

def average_last_elements(inner_list):
    return sum(item[-1] for item in inner_list) / len(inner_list)

def convert_keys_to_tuples(keys):
    tuple_keys = [ast.literal_eval(key) for key in keys]
    return tuple_keys

def grab_from_store(title,folder='PreOptimisationDataStore'):
    data = {}
    csv_file = path.join(folder, title)

    # Open and read the CSV file
    with open(csv_file, 'r') as file:
        reader = DictReader(file)
        for row in reader:
            key = row['Key']
            try:
                value = float(row['Value'])
            except:
                value = row['Value']
            data[key] = value
    return data

title='NH3_OAT_Analysis'
folder = 'DataAnalysis'

sol_dict = filter_dict(dict(zip(convert_keys_to_tuples(grab_from_store(title,folder).keys()),grab_from_store(title,folder).values())),10e-3)

n_c = 5

kmeans = KMeans(n_clusters=n_c, random_state=0)
X = np.array(list(sol_dict.values())).reshape(-1,1)
kmeans.fit(X)

labelled_data = [[],[],[],[],[]]

for i in range(len(X)):
    labelled_data[kmeans.labels_[i]].append([list(sol_dict.keys())[i],X[i][0]])

for i in range(n_c):
    labelled_data[i].sort(key = lambda x: x[-1],reverse=True)

sorted_data = sorted(labelled_data, key=average_last_elements,reverse=True)

count = 1

temp = [[],[],[],[],[]]
inc = 0
for i in range(len(sorted_data)):
    for q in range(len(sorted_data[i])):
        inc += sorted_data[i][q][-1]
        temp[i].append(inc)

for i in sorted_data:
    plt.bar([combine_tuple_elements(j[0]) for j in i],[j[-1] for j in i],label=f'Cluster {count}')
    count += 1
plt.legend()
plt.xticks(rotation=45, ha='right')
plt.show()

for i in range(0,len(sorted_data)):
    plt.plot([combine_tuple_elements(j[0]) for j in sorted_data[i]],np.array(temp[i])/inc,label=f'Cluster {i+1}')

plt.legend()
plt.xticks(rotation=45, ha='right')
plt.show()
