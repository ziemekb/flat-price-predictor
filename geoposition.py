import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Point

def classify_coor(latitude, longitude):
    location = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy([longitude], [latitude]), 
                                      crs="EPSG:4326")
    for idx, row in wroclaw.iterrows():
        if(row['geometry'].contains(location).at[0, 'geometry']):
            return row['NAZWAOSIED']
    return None

shp_path = r"wroclaw/borders.shp"
wroclaw = geopandas.read_file(shp_path)
wroclaw = wroclaw.to_crs("EPSG:4326")

#print(classify_coor(51.1168551569616, 16.95513647328204))
