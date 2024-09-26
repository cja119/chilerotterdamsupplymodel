import numpy as np
import pandas as pd
from copy import deepcopy
import csv
import os
import random
from math import floor, ceil
from csv import DictReader
from os import path

def generate_random_integers(K, n):
    if K > n:
        raise ValueError("K cannot be greater than n")

    # Step 1: Generate K-1 random integers in the range from 1 to n-1
    partition_points = sorted(random.sample(range(1, n), K-1))

    # Step 2: Add 0 and n to the partition points
    partition_points = [0] + partition_points + [n]

    # Step 3: Calculate the differences between consecutive partition points
    random_integers = [partition_points[i+1] - partition_points[i] for i in range(K)]

    return random_integers

def new_k_means(df, K):

    df = df.sort_index()

    np.random.seed(0)  
    initial_centroids = np.random.choice(df.values.flatten(), K, replace=False)
    
    centroids = initial_centroids
    clusters = pd.Series(list(range(1,K))*floor(df.shape[0]/K))

    obj_old = np.inf
    eps = 10e-3
    obj = (1/df.shape[0])*sum([(centroids[k] * clusters[k] - sum(df[range(0,k) if k == 0 else range(k-1,k)]))**2 for k in range(K)])
    
    while obj_old - obj >= eps:
        obj_old = obj
        for j in range(len(clusters)-1):
            clusters_l = clusters.copy()
            clusters_u = clusters.copy()

            centroids_l = centroids.copy()
            centroids_u = centroids.copy()

            clusters_u.iloc[j] += 1
            clusters_u.iloc[j+1] -= 1

            clusters_l.iloc[j] -= 1
            clusters_l.iloc[j+1] += 1
            

            for k in range(K):
                if k == 0:

                    centroids_l[k] = df[[i for i in range(len(df)) if i <= clusters_l[k]]].mean()
                    centroids_u[k] = df[[i for i in range(len(df)) if i <= clusters_u[k]]].mean()
                else:
                    centroids_l[k] = df[[i for i in range(len(df)) if clusters_l[k-1] < i <= clusters_l[k]]].mean()
                    centroids_u[k] = df[[i for i in range(len(df)) if clusters_u[k-1] < i <= clusters_u[k]]].mean()
            print([i for i in range(len(df)) if clusters_u[k-1] < i <= clusters_u[k]])
            obj_l = (1/df.shape[0])*sum([(centroids_l[k] * clusters_l[k] - sum(df[range(0,k) if k == 0 else range(k-1,k)]))**2 for k in range(K)])
            obj_u = (1/df.shape[0])*sum([(centroids_u[k] * clusters_u[k] - sum(df[range(0,k) if k == 0 else range(k-1,k)]))**2 for k in range(K)])
        
            if obj_l <= obj:
                obj = obj_l
                clusters = clusters_l.copy()
                centroids = centroids_l.copy()

            if obj_u <= obj:
                obj = obj_u
                clusters = clusters_u.copy()
                centroids = centroids_u.copy()
            print(obj,obj_l,obj_u)
    full_clusters = []
    for k in range(K):
        for i in np.ones(clusters[k])*k:
            full_clusters.append(i)

    return clusters, centroids



def k_means_adjacent(df, K):

    df = df.sort_index()

    np.random.seed(0)  
    initial_centroids = np.random.choice(df.values.flatten(), K, replace=False)
    
    centroids = initial_centroids
    clusters = pd.Series(np.zeros(df.shape[0]), index=df.index)
    previous_clusters = pd.Series(np.ones(df.shape[0]) * -1, index=df.index)
    
    while not clusters.equals(previous_clusters):
        previous_clusters = clusters.copy()
    
        for i in range(len(df)):
            distances = np.abs(df.values[i] - centroids)
            clusters.iloc[i] = np.argmin(distances)
            
            # If not the first point, ensure continuity
            if i > 0 and clusters.iloc[i] != clusters.iloc[i-1]:
                # Check if switching to the previous cluster is better
                if np.abs(df.values[i] - centroids[int(clusters.iloc[i-1])]) < distances[int(clusters.iloc[i])]:
                    clusters.iloc[i] = clusters.iloc[i-1]
        
        for k in range(K):
            if (clusters == k).any():
                centroids[k] = df[clusters == k].mean()
    
    return clusters, centroids



def count_consecutive_integers(arr,keys):
    if arr.empty:  # Return an empty list if the input array is empty
        return []

    result = []
    current_value = arr[0]
    count = 1

    for i in range(1, len(arr)):
        if arr.iloc[i] == current_value:
            count += 1
        else:
            result.append((keys[int(current_value)], count))
            current_value = arr[i]
            count = 1
    
    # Append the last group
    result.append((keys[int(current_value)], count))

    inc = 0
    list = []
    for i in result:
        list.append([inc,i[1]])
        inc += i[1]
    main_array = np.array(list)
    return result, main_array

def repeat_tuples(tuple_list):
    result = []
    for value, count in tuple_list:
        result.extend([value] * count)
    return result

def normalized_euclidean_norm(list1, list2):
    # Ensure the lists are numpy arrays
    array1 = np.array(list1)
    array2 = np.array(list2)
    
    # Check if both arrays have the same length
    if array1.shape != array2.shape:
        raise ValueError("Both lists must have the same length.")
    
    # Calculate the squared differences
    squared_diff = np.square(array1 - array2)
    
    # Sum the squared differences
    sum_squared_diff = np.sum(squared_diff)
    
    # Calculate the Euclidean norm (square root of sum of squared differences)
    euclidean_norm = np.sqrt(sum_squared_diff)
    
    # Normalize by the length of the list
    normalized_euclidean_norm = euclidean_norm / len(array1)
    
    return normalized_euclidean_norm

def insert_array(array1,array2):
    start_times = np.sort(np.concatenate((array1[:,0],array2[:,0])))

    no_dupes = []
    [no_dupes.append(x) for x in start_times if x not in no_dupes]
    durations = []
    for i in range(0,len(no_dupes)-1):
        if i == len(no_dupes)-1:
            pass
        else:
            durations.append(no_dupes[i+1]-no_dupes[i])
    durations.append(1)
    return np.vstack((no_dupes,durations)).T

def generate_stacked_array(start_date,end_date,interval=168,load_time=8,voyage_time=360):
    a = end_date - start_date
    delta = int(a/(3600*1000000000))/interval
    array1 = np.arange(-1,ceil(delta)+1)*interval + 1
    array2 = np.arange(-1,ceil(delta)+1)*interval
    array3 = np.arange(-1,ceil(delta)+1)*interval + load_time + 1
    array4 = np.arange(-1,ceil(delta)+1)*interval + load_time
    array5 = np.arange(-1,ceil(delta)+1)*interval + load_time + voyage_time + 1
    array6 = np.arange(-1,ceil(delta)+1)*interval + load_time + voyage_time

    master_array = np.sort(np.concatenate((array1,array2,array3,array4,array5,array6)))
    mask = master_array <= delta*interval 
    temp_array = master_array[mask]
    mask2 = temp_array >= 0
    filtered_array = temp_array[mask2]

    array_of_ones = np.ones(len(filtered_array),dtype=int)
    stacked_array = np.vstack((filtered_array,array_of_ones)).T
    return stacked_array

def save_csv(array,title,folder='PreOptimisationDataStore'):
    if isinstance(array,dict):
        data = array        
        pass
    else:
        data = {i: value for i,value in enumerate(array)}
        
    # Open the file in write mode to empty its content before writing new data
    csv_file = os.path.join(folder, title)
    os.makedirs(folder, exist_ok=True)

    with open(csv_file, mode='w', newline='') as file:
        # Create a writer object
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(['Key', 'Value'])
        
        # Write the data rows
        for key, value in data.items():
            writer.writerow([key, value])

