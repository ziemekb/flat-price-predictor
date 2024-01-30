import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from plots import plt_prices_per_district

data = pd.read_csv('listings.csv', delimiter=';')
data['PricePerSqM'] = (data['Price'] / data['Area']).astype(int)
means = data[['PricePerSqM', 'District']].groupby('District').mean()
plt_prices_per_district(means)

flats = data.drop(columns=['Latitude', 'Longitude', 'PricePerSqM'])
print(flats.columns)

