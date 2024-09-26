import numpy as np
import pandas as pd
from copy import deepcopy
import csv
import os

def k_mediods_adjacent(df, K):

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
                centroids[k] = df[clusters == k].median()
    
    return clusters, centroids