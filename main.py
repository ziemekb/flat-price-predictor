import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv('listings.csv', delimiter=';')
data['PricePerSqM'] = (data['Price'] / data['Area']).astype(int)
means = data[['PricePerSqM', 'District']].groupby('District').mean()

shp_path = r"wroclaw/borders.shp"
wroclaw = geopandas.read_file(shp_path)

wroclaw = wroclaw.rename(columns=
                         {'OBJECTID'   : 'ID',
                          'NROSIEDLA'  : 'DistrictNo',
                          'NAZWAOSIED' : 'District',
                          'DATA'       : 'Data',
                          'SHAPE_AREA' : 'ShapeArea',
                          'SHAPE_LEN'  : 'ShapeLen'})
wroclaw = wroclaw.join(means, on='District', how='left')

ax = wroclaw.plot(column='PricePerSqM', 
            legend=True,
            legend_kwds={"label": "Price in PLN"},
            cmap='YlOrRd', 
            missing_kwds={"color": "lightgrey"})
ax.set_axis_off()
plt.show()

