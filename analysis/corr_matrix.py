import os
import pandas as pd
import numpy as np
import seaborn as sn

# Loading the dataset
BIKE = pd.read_csv("day.csv")

# Numeric columns of the dataset
numeric_col = ['temp','atemp','hum','windspeed']

# Correlation Matrix formation
corr_matrix = BIKE.loc[:,numeric_col].corr()

#Using heatmap to visualize the correlation matrix
sn.heatmap(corr_matrix, annot=True)
