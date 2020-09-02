"""
Module to handle Vector and Raster Manipulations for images exported using GEE library

Author: AntPod Designs Pvt Ltd
Contributors: Kaaviya Ramkumar
Version: 0.1.7
"""

import rasterio as rio
from rasterio import plot as rioplot
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
import rasterstats
import os

# Directory for GeoJSON and Shapefile
farmGeoJSON = "F:\AntPod\Satellite Imagery\Python Codes\script\geojson\farm2.geojson"
farmShapefile = "F:\AntPod\Satellite Imagery\Python Codes\script\shapefiles\\farm2\\farm2.shp"

# Directory TIFF images
file = "F:\AntPod\Satellite Imagery\Python Codes\script\tiff\Jan-June2020-20200704T063533Z-001\Jan-June2020"

# User configurations that are prone to change
userID = "APX00001"
mapConfig = "XX"
sensor = ["L2A", "L1C"]

# Back end constant configuration parameters - Antpod Products
antpodL2ABands = "BANDS"
antpodL2ATC = "TC"
antpodL2AVI2 = "VI2"
antpodL2AVI = "VI"

# List of names of products and bands
listProdVI2 = ['NDVI','GNDVI','PSRI','NDCI']
listProdVI = ['EVI','SAVI','ARVI']
listS2Bands = ['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B11','B12']
listS2Indices = ['NDVI', 'GNDVI', 'MCARI', 'ARVI', 'LNDWI', 'BNDWI', 'MSI',
                 'NDII', 'NBR', 'NDCI', 'NDSI', 'SAVI', 'PSRI', 'EVI']

def rasterCaller(userID, mapConfig, sensor, antpodProduct):
    """ Function to call mapper - dictionary of functions according to the products

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProd : one of {antpodL2ABands, antpodL2ATC, antpodL2AVI2, antpodL2AVI}
    Returns:
        A function call to get Raster bands for mentioned antpodProduct
    """
    return rasterMapper[antpodProduct](userID, mapConfig, sensor,antpodProduct)


def openRaster(filesRaster, antpodProduct):
    """ Function to open a raster image of format TIF

    Args:
        filesRaster : List of names of raster images (obtained via rasterCaller())
        antpodProd : one of {antpodL2ABands, antpodL2ATC, antpodL2AVI2, antpodL2AVI}
    Returns:
        Dictionary of Rasterio DatasetReader object
    """
    meta = {filesRaster[i].split(antpodProduct + '-')[-1].split('.')[0]:
                rio.open(filesRaster[i]) for i in range(len(filesRaster))}
    return meta


def getRasterVI(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with VI bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
    Returns:
        A list of tif images
    """
    filesVI = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesVI.sort()
    return filesVI


def getRasterVI2(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with VI2 bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
    Returns:
        A list of tif images
    """
    filesVI2 = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesVI2.sort()
    return filesVI2


def getRasterBands(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with raw Sentinel bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
    Returns:
        A list of tif images
    """
    filesBands = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesBands.sort()
    return filesBands


def getRasterTC(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with TC bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
    Returns:
        A list of tif images
    """
    filesTC = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesTC.sort()
    return filesTC


rasterMapper = {
    'VI' : getRasterVI,
    'VI2' : getRasterVI2,
    'TC' : getRasterTC,
    'BANDS' : getRasterBands
}


def extractDates(meta):
    """ Function to get dates from tif files

    Args:
        meta : dictionary of rasterio DatasetReader object
    Returns:
        A list of strings (dates)
    """
    return [key for key in meta.keys()]


def readMultipleRaster(datasetReader):
    """ Function to read the raster data and store them as numpy arrays for easy manipulation

    Args:
        datasetReader : a rasterio DatasetReader object
    Returns:
        A numpy list of float values of the tif image for each bands present in datasetReader
    """
    numpyListofBands = [datasetReader.read(i) for i in range(1, datasetReader.count + 1)]
    return numpyListofBands


def readMultipleDatasetReader(meta):
    """ Function to read the raster data and store them as numpy arrays for easy manipulation

    Args:
        meta : dictionary of Rasterio DatasetReader object
    Returns:
        A numpy list of float values of the tif image for each bands present in all datasetReader objects
    """
    numpyListofList = [readMultipleRaster(meta[keys]) for keys in meta]
    return numpyListofList


def retBandBounds(band):
    """ Function to return bounds of a DatasetReader object

    Args:
        datasetReader : a rasterio DatasetReader object
    Returns:
       a BoundingBox object of rasterio.coords module
    """
    return band.bounds


def showRaster(indices, cmap='RdYlGn'):
    """ Function to plot numpy array obtained after reading rasterio DatasetReader (works
    best for NDVI, need to adjust max values for other indices)

    Args:
        indices : a numpy array
        cmap : a registered colormap to plot scalar data to colors
    Returns:
       nil
    """
    rioplot.show(indices, cmap=cmap)
    return


def readShapefile(shapefile):
    """ Function to read shapefile and create a GeoDataFrame

    Args:
        shapefile : a geospatial vector data format
    Returns:
       geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    """
    geodf = gpd.read_file(shapefile)
    return geodf


def setGeoDFCRS(geodf, epsg=4326):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column with changed CRS
    """
    return geodf.to_crs(epsg=epsg)


def retGeoDFBounds(geodf):
    """ Function to return total bounds of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        bounds : a numpy array with boundaries of GeoDataFrame in the form of
        maximum and minimum of latitudes and longitudes
    """
    bounds = geodf.total_bounds
    return bounds


def retWindowRaster(datasetReader, geodf):
    """ Function to create a windown that contains rectangular subset of rasterio
    DatasetReader object according to the bounding box of GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        windowRaster : a windows.Window object to view a rectangular subset
        of a raster dataset
    """
    geodfBBox = retGeoDFBounds(geodf)
    windowRaster = datasetReader.window(*geodfBBox)
    return windowRaster


def retclipGeoData(datasetReader, geodf):
    """ Function to clip rectangular subset of rasterio DatasetReader object clipped
    according to the bounding box of GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        clipGeoData : a numpy subset array of the rasterio dataset file adjusted
        according to the window provided by GeoDataFrame boundaries
    """
    windowRaster = retWindowRaster(datasetReader, geodf)
    clipGeoData = datasetReader.read(1, window=windowRaster)
    return clipGeoData


def plotShapefileOnRaster(datasetReader, geodf, cmap='RdYlGn'):
    """ Function to plot and show shapefile boundary onto the windowed subset of rasterio
    DatasetReader with the index as the basemap

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        cmap : a registered colormap to plot scalar data to colors
    Returns:
        nil
    """
    geodfBBox = retGeoDFBounds()
    windowRaster = retWindowRaster(datasetReader, geodf)
    clipGeoData = retclipGeoData(datasetReader, geodf)
    plt.imshow(clipGeoData, extent=geodfBBox[[0, 2, 1, 3]], cmap=cmap)
    geodf.boundary.plot(ax=plt.gca(), color='k')


def retTransform(datasetReader, geodf):
    """ Function to plot and show shapefile boundary onto the windowed subset of rasterio
    DatasetReader with the index as the basemap

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        transform : an affine transform for a datasetReader window
    """
    windowRaster = retWindowRaster(datasetReader, geodf)
    transform = datasetReader.window_transform(windowRaster)
    return transform


def multipleWindowing(meta, geodf):
    """ Function to create multiple windowed subset of rasterio
   DatasetReader for each image

   Args:
       meta : dictionary of Rasterio DatasetReader object
       geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
   Returns:
       multipleWindowRaster : a list of windows.Window object for each
       DatasetReader object
   """
    geodfBBox = retGeoDFBounds(geodf)
    multipleWindowRaster = [(meta[keys]).window(*geodfBBox) for keys in meta]
    return multipleWindowRaster


def multipleClipping(meta, geodf):
    """ Function to create multiple clipped subset of rasterio
    DatasetReader for each image

    Args:
        meta : dictionary of Rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    Returns:
        multipleWindowRaster : a list of windows.Window object for each
        DatasetReader object
    """
    multipleClipGeoData = [values.read(i, window=retWindowRaster(values, geodf))
                           for values in meta.values() for i in range(1, values.count + 1)]
    return multipleClipGeoData


def insertGeoDFCol(geodf, colName, value=0):
    """ Function to insert new column in the GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        colName : a string
        value : a default value to initialise rows of colName
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a new column
    """
    geodf.insert(len(geodf.columns), colName, value)
    return geodf


def dropGeoDFCol(geodf, colName):
    """ Function to drop existing column in the GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        colName : a string
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with one less column
    """
    geodf = geodf.drop([colName], axis=1)
    return geodf


def assignHealth(geodf):
    
    stat = rasterstats.zonal_stats(geodf.geometry.head(), clipped_band, affine=transform)
    
    for i in range(len(stat)):
        if (stat[i]['mean'] < 0.45):
            geodf.loc[i, 'health'] = 'bad'
            geodf.loc[i, 'meanNDVI'] = stat[i]['mean']

        elif (stat[i]['mean'] >= 0.45 and stat[i]['mean'] < 0.55):
            geodf.loc[i, 'health'] = 'ok'
            geodf.loc[i, 'meanNDVI'] = stat[i]['mean']

        elif (stat[i]['mean'] >= 0.55):
            geodf.loc[i, 'health'] = 'good'
            geodf.loc[i, 'meanNDVI'] = stat[i]['mean']

    return geodf


def getZoneHealth(geodf):
    good = geodf[geodf.health == 'good']
    bad = geodf[geodf.health == 'bad']
    ok = geodf[geodf.health == 'ok']

    return good, bad, ok


def plotZoneHealth(geodf, title):
    good, bad, ok = getZoneHealth(geodf)

    good.plot(ax=plt.gca(), color='g')
    bad.plot(ax=plt.gca(), color='r')
    ok.plot(ax=plt.gca(), color='y')
    geodf.boundary.plot(ax=plt.gca(), color='k')
    plt.axis('off')

