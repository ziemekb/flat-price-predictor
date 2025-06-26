import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pathlib import Path

SHP_PATH = Path().resolve().parent / 'wroclaw/borders.shp'

def classify_coords(latitude, longitude):
    location = geopandas.GeoDataFrame(
                geometry=geopandas.points_from_xy([longitude], [latitude]), 
                crs='EPSG:4326'
               )
    for idx, row in wroclaw.iterrows():
        if(row['geometry'].contains(location).at[0, 'geometry']):
            return row['NAZWAOSIED']
    return None

wroclaw = geopandas.read_file(SHP_PATH)
wroclaw = wroclaw.to_crs('EPSG:4326')
