import numpy as np
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches


def percentile_stretch(img, pmin=0., pmax=100.):
    '''
    This is where you should write a docstring.
    '''
    # here, we make sure that pmin < pmax, and that they are between 0, 100
    if not 0 <= pmin < pmax <= 100:
        raise ValueError('0 <= pmin < pmax <= 100')
    # here, we make sure that the image is only 2-dimensional
    if not img.ndim == 2:
        raise ValueError('Image can only have two dimensions (row, column)')

    minval = np.percentile(img, pmin)
    maxval = np.percentile(img, pmax)

    stretched = (img - minval) / (maxval - minval)  # stretch the image to 0, 1
    stretched[img < minval] = 0  # set anything less than minval to the new minimum, 0.
    stretched[img > maxval] = 1  # set anything greater than maxval to the new maximum, 1.

    return stretched


def img_display(img, ax, bands, stretch_args=None, **imshow_args):
    '''
    This is where you should write a docstring.
    '''
    dispimg = img.copy().astype(np.float32)  # make a copy of the original image,
    # but be sure to cast it as a floating-point image, rather than an integer

    for b in range(img.shape[0]):  # loop over each band, stretching using percentile_stretch()
        if stretch_args is None:  # if stretch_args is None, use the default values for percentile_stretch
            dispimg[b] = percentile_stretch(img[b])
        else:
            dispimg[b] = percentile_stretch(img[b], **stretch_args)

    # next, we transpose the image to re-order the indices
    dispimg = dispimg.transpose([1, 2, 0])

    # finally, we display the image
    handle = ax.imshow(dispimg[:, :, bands], **imshow_args)

    return handle, ax

# ------------------------------------------------------------------------
# note - rasterio's open() function works in much the same way as python's - once we open a file,
# we have to make sure to close it. One easy way to do this in a script is by using the with statement shown
# below - once we get to the end of this statement, the file is closed.
with rio.open('data_files/NI_Mosaic.tif') as dataset:
    img = dataset.read()
    xmin, ymin, xmax, ymax = dataset.bounds

# your code goes here!
# start by loading the outlines and point data to add to the map
counties = gpd.read_file('C:/GIS_Course/EGM722/egm722/Week2/data_files/Counties.shp')

towns = gpd.read_file('C:/GIS_Course/EGM722/egm722/Week2/data_files/Towns.shp')

# next, create the figure and axis objects to add the map to

myCRS = ccrs.UTM(29)

fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# now, add the satellite image to the map
my_kwargs = {'extent': [xmin, xmax, ymin, ymax],
             'transform': myCRS}

my_stretch = {'pmin': 0.1, 'pmax': 99.9}

h, ax = img_display(img, ax, [2, 1, 0], stretch_args=my_stretch, **my_kwargs)
fig

# next, add the county outlines to the map
county_names = list(counties.CountyName.unique())
county_names.sort()  # sort the counties alphabetically by name

for ii, name in enumerate(county_names):
    feat = ShapelyFeature(counties.loc[counties['CountyName'] == name, 'geometry'],  # first argument is the geometry
                          myCRS,  # second argument is the CRS
                          edgecolor='r',  # outline the feature in black
                          facecolor='none',
                          linewidth=1,  # set the outline width to be 1 pt
                          alpha=1)  # set the alpha (transparency) to be 0.25 (out of 1)
    ax.add_feature(feat)  # once we have created the feature, we have to add it to the map using ax.add_feature()

# then, add the town and city points to the map, but separately

just_towns = towns.loc[towns['town_city'] == 0]
town_handle = ax.plot(just_towns.geometry.x, just_towns.geometry.y, 's', color='b', ms=6, transform=myCRS)

just_cities = towns.loc[towns['town_city'] == 1]
city_handle = ax.plot(just_cities.geometry.x, just_cities.geometry.y, 'd', color='m', ms=6, transform=myCRS)

# finally, try to add a transparent overlay to the map
# note: one way you could do this is to combine the individual county shapes into a single shape, then
print(counties.columns)
ni = counties.dissolve()
print(ni.geometry)
print(dataset.bounds)

#clip = Polygon(shell=[(550000.0,5985000.0,735000.0,6135000.0)], holes=[[ni.geometry, ni.geometry[0]]])
# use a geometric operation, such as a symmetric difference, to create a hole in a rectangle.


# then, you can add the output of the symmetric difference operation to the map as a semi-transparent feature.


# last but not least, add gridlines to the map
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

handles = town_handle + city_handle

labels = ['Town', 'City']

leg = ax.legend(handles, labels, fontsize=10, loc='upper left', frameon=True, framealpha=1)


# and of course, save the map!
fig.savefig('prac4Asgm.png', bbox_inches='tight', dpi=300)
