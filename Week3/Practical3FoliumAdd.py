import numpy as np
import pandas as pd
import geopandas as gpd
import folium

wards = gpd.read_file('data_files/NI_Wards.shp')
print(wards.columns)

m = wards.explore('Population', cmap='viridis')

df = pd.read_csv('data_files/Airports.csv') # read the csv dat
df2 = pd.read_csv('data_files/translink-stationsni.csv') # read the csv data bus/train stations

# create a new geodataframe
airports = gpd.GeoDataFrame(df[['name', 'website']], # use the csv data, but only the name/website columns
                            geometry=gpd.points_from_xy(df['lon'], df['lat']), # set the geometry using points_from_xy
                            crs='epsg:4326') # set the CRS using a text representation of the EPSG code for WGS84 lat/lon


bustrain = gpd.GeoDataFrame(df2,
                            geometry=gpd.points_from_xy(df2['easting'], df2['northing']),
                            crs='epsg:29901') # insert bustrain data

# change coordinate system to UTM
bustrain = bustrain.to_crs(epsg='4326')

print(bustrain.columns)


# add the airport points to the existing map
airports.explore('name',
                 m=m, # add the markers to the same map we just created
                 marker_type='marker', # use a marker for the points, instead of a circle
                 popup=True, # show the information as a popup when we click on the marker
                 legend=False, # don't show a separate legend for the point layer
                )

bustrain.explore('Type',
                 m=m, # add the markers to the same map we just created
                 marker_type='circle', # use a marker for the points, instead of a circle
                 popup=True, # show the information as a popup when we click on the marker
                 legend=False, # don't show a separate legend for the point layer
                )

# add transport data and merge with wards data
transport = pd.read_csv('data_files/transport_data.csv')

merged = wards.merge(transport, left_on='Ward Code', right_on='Ward Code')

# add column with bustops per capita
for ind, row in merged.iterrows():
    merged.loc[ind, 'BusCap']= row['Population']/row['NumBus']

m = merged.explore('BusCap', # show the Distance column
                   cmap='plasma', # use the 'plasma' colormap from matplotlib
                   legend_kwds={'caption': 'amount of people per busstop'} # set the caption to a longer explanation
                  )

# define marker for airports
airport_args = {
    'm': m, # add the markers to the same map we just created
    'marker_type': 'marker', # use a marker for the points, instead of a circle
    'popup': True, # show the information as a popup when we click on the marker
    'legend': False, # don't show a separate legend for the point layer
    'marker_kwds': {'icon': folium.Icon(color='red', icon='plane', prefix='fa')} # make the markers red with a plane icon from FA
}

# define marker for bus train station

bustrain_args = {
    'm': m,
    'marker_type': 'marker',
    'popup': True,
    'legend': True,
    'marker_kwds': {'icon': folium.Icon(color='orange', icon='bus-simple', prefix='fa')}
}


# use the airport_args with the ** unpacking operator - more on this next week!
airports.explore('name', **airport_args)

bustrain.explore('Type', **bustrain_args)

m # show the map

m.save('NI_Transport_test.html')