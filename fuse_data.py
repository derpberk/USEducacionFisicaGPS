import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os


# Read every csv in the folder
path = "DATOS/PRUEBA_4_10_2023"
files = os.listdir(path)
dfs = []
# Create a list of dataframes 
for file in files:
    df = pd.read_csv(path + "/" + file)
    dfs.append(df)

# Concatenate all the dataframes
df = pd.concat(dfs, ignore_index=True)

# Save the dataframe as a csv
df.to_csv("DATOS/PRUEBA_4_10_2023/joint_data.csv")

