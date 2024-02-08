import matplotlib.pyplot as plt 
import geopandas
import pandas as pd
from shapely.geometry import Point

shp_path = r"wroclaw/borders.shp"
wroclaw = geopandas.read_file(shp_path)
wroclaw = wroclaw.to_crs(epsg=4326)
data = pd.read_csv('listings.csv', delimiter=';')
data['PricePerSqM'] = (data['Price'] / data['Area']).astype(int)
means = data[['PricePerSqM', 'District']].groupby('District').mean()

wroclaw = wroclaw.rename(columns=
                         {'OBJECTID'   : 'ID',
                          'NROSIEDLA'  : 'DistrictNo',
                          'NAZWAOSIED' : 'District',
                          'DATA'       : 'Data',
                          'SHAPE_AREA' : 'ShapeArea',
                          'SHAPE_LEN'  : 'ShapeLen'})

def plt_prices_per_district():
    wroclaw = wroclaw.join(means, on='District', how='left')

    ax = wroclaw.plot(column='PricePerSqM',
                legend=True,
                legend_kwds={"label": "Price in PLN"},
                cmap='YlOrRd',
                missing_kwds={"color": "lightgrey"})
    ax.set_axis_off()

    '''
    #labels for the districts;
    #add visibility on hovering or leave it out
    wroclaw['RepPt'] = wroclaw['geometry'].apply(lambda x: x.representative_point().coords[:])
    wroclaw['RepPt'] = [coords[0] for coords in wroclaw['RepPt']]
    for idx, row in wroclaw.iterrows():
        txt = ax.text(row['RepPt'][0],
                row['RepPt'][1],
                s=row['District'],
                horizontalalignment='center',
                fontsize='x-small',
                bbox={'facecolor': 'white', 'alpha':0.8, 'edgecolor':'none'})
    '''
    plt.title("Average Flat Price by District Heatmap")

    fig = plt.gcf()
    fig.canvas.manager.set_window_title('xD')

    #plt.savefig("district_avg_price.png")
    plt.show()

def plt_all_prices():
    data_points = geopandas.GeoDataFrame(data,
                                          crs="epsg:4326",
                                          geometry=[Point(xy) for xy in zip(data.Longitude, data.Latitude)])
    wroclaw.plot(color='white', edgecolor='black')
    data_points.plot(ax=plt.gca(), column='PricePerSqM', cmap='plasma', markersize=6, legend=True)

    print("Number of points plotted:", len(data_points))
    plt.title('Price per Square Meter with Wroclaw District Borders')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

plt_all_prices()
