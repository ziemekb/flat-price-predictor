import matplotlib.pyplot as plt 
import geopandas

def plt_prices_per_district(means):
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
    wroclaw['RepPt'] = wroclaw['geometry'].apply(lambda x: x.representative_point().coords[:])
    wroclaw['RepPt'] = [coords[0] for coords in wroclaw['RepPt']]

    ax = wroclaw.plot(column='PricePerSqM',
                legend=True,
                legend_kwds={"label": "Price in PLN"},
                cmap='YlOrRd',
                missing_kwds={"color": "lightgrey"})
    ax.set_axis_off()
    '''
    #labels for the districts;
    #add visibility on hovering or leave it out
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

    plt.show()
