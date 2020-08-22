"""
Module to handle Vector and Raster Manipulations for images exported using GEE library

Author: AntPod Designs Pvt Ltd
Contributors: Kaaviya Ramkumar & Manish Meganathan
Version: 0.1.12
"""

import os
import rasterstats
import numpy as np
from glob import glob
import rasterio as rio
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from rasterio import plot as rioplot


def rasterCaller(userID, mapConfig, sensor, antpodProduct):
    """ Function to call mapper - dictionary of functions according to the products

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : one of {antpodL2ABands, antpodL2ATC, antpodL2AVI2, antpodL2AVI}
    Returns:
        A function call to get Raster bands for mentioned antpodProduct
    """
    curDirectory = os.getcwd()
    if 'tiff' not in os.listdir():
        ch = os.path.dirname(curDirectory)
        os.chdir(ch)
        os.chdir(os.path.join(ch, 'tiff'))
    elif 'tiff' in os.listdir():
        os.chdir(os.path.join(os.getcwd(), 'tiff'))
    else:
        print('ERROR: Tiff is not in the directory.')

    return rasterMapper[antpodProduct](userID, mapConfig, sensor, antpodProduct)


def openRaster(filesRaster, antpodProduct):
    """ Function to open a raster image of format TIF

    Args:
        filesRaster : List of names of raster images (obtained via rasterCaller())
        antpodProduct : one of {antpodL2ABands, antpodL2ATC, antpodL2AVI2, antpodL2AVI, antpodVXX}
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
        antpodProduct : List of antpod VI products
    Returns:
        A list of tif images
    """
    filesVI = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '-' + "*.tif")
    filesVI.sort()
    return filesVI


def getRasterVI2(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with VI2 bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod VI2 products
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
        antpodProduct : List of antpod Band products
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
        antpodProduct : List of antpod TC products
    Returns:
        A list of tif images
    """
    filesTC = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesTC.sort()
    return filesTC


def getRasterVXX(userID, mapConfig, sensor, antpodProduct):
    """ Function to get raster tif files with VI bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod VXX products
    Returns:
        A list of tif images
    """
    filesVXX = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '-' + "*.tif")
    filesVXX.sort()
    return filesVXX


rasterMapper = {
    'VI': getRasterVI,
    'VI2': getRasterVI2,
    'TC': getRasterTC,
    'BANDS': getRasterBands,
    'VXX': getRasterVXX
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


def retBandBounds(datasetReader):
    """ Function to return bounds of a DatasetReader object

    Args:
        datasetReader : a rasterio DatasetReader object
    Returns:
       a BoundingBox object of rasterio.coords module
    """
    return datasetReader.bounds


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


def readGeoJSON(User):
    """ Function to read a GeoJSON file format

    Args:
        User : an object
    Returns:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
    """
    path = User.name + '.geojson'
    geo = gpd.read_file(path)
    return geo


def createGrid(geo):
    """ Function to create a 2D square grid map from GeoJSON geometry

    Args:
        User: an object
    Returns:
        grid : a GeoDataFrame as pandas.DataFrame with list of Polygons as grids
    """
    # bbox = [longmin, latmin, longmax, latmax] #bbox format
    # bbox = User.boi (once we interconnect User from GEE files)
    # ymin, xmin, ymax, xmax = bbox[0], bbox[1], bbox[2], bbox[3]

    xmin, ymin, xmax, ymax = geo.total_bounds
    side = 0.0005
    rows = int(np.ceil((ymax - ymin) / side))
    cols = int(np.ceil((xmax - xmin) / side))
    XleftOrigin = xmin
    XrightOrigin = xmin + side
    YtopOrigin = ymax
    YbottomOrigin = ymax - side
    polygons = []
    for i in range(cols):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(rows):
            polygons.append(
                Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)]))
            Ytop = Ytop - side
            Ybottom = Ybottom - side
        XleftOrigin = XleftOrigin + side
        XrightOrigin = XrightOrigin + side
    grid = gpd.GeoDataFrame({'geometry': polygons}, crs={'init': 'epsg:4326'})
    return grid


def overlayGrid(grid, geo):
    """ Function to create a 2D square grid map from GeoJSON geometry

    Args:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
        grid : a GeoDataFrame as pandas.DataFrame with list of Polygons as grids
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame that has been overlayed
        by a shapefile of grids
    """
    geodf = gpd.overlay(grid, geo)
    return geodf


def readShapefile(userID):
    """ Function to read shapefile and create a GeoDataFrame

    Args:
        userID = Antpod user ID
    Returns:
       geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
    """
    import sys
    sys.path.insert(1, "../shapefiles")

    dest = userID + '.shp'
    while 'shapefiles' not in os.listdir():
        curDirectory = os.getcwd()
        ch = os.path.dirname(curDirectory)
        os.chdir(ch)
        if 'shapefiles' in os.listdir():
            os.chdir(os.path.join(os.getcwd(), 'shapefiles'))
            break
    geodf = gpd.read_file(dest)
    return geodf


def setGeoDFCRS(geodf, epsg=4326):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        epsg : a coordinate reference system with a default value of 4326
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
    """ Function to create a window that contains rectangular subset of rasterio
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


def retClipGeoData(datasetReader, geodf, index):
    """ Function to clip rectangular subset of rasterio DatasetReader object clipped
    according to the bounding box of GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        index : a string containing the name of index to be retrieved
    Returns:
        clipGeoData : a numpy subset array of the rasterio dataset file adjusted
        according to the window provided by GeoDataFrame boundaries
    """
    windowRaster = retWindowRaster(datasetReader, geodf)
    clipGeoData = datasetReader.read(index, window=windowRaster)
    return clipGeoData


def plotShapefileOnRaster(datasetReader, geodf, index, cmap='RdYlGn'):
    """ Function to plot and show shapefile boundary onto the windowed subset of rasterio
    DatasetReader with the index as the basemap

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        cmap : a registered colormap to plot scalar data to colors
        index : a string containing the name of index to be retrieved
    Returns:
        nil
    """
    geodfBBox = retGeoDFBounds(geodf)
    clipGeoData = retClipGeoData(datasetReader, geodf, index)
    plt.imshow(clipGeoData, extent=geodfBBox[[0, 2, 1, 3]], cmap=cmap)
    geodf.boundary.plot(ax=plt.gca(), color='k')


def retTransform(datasetReader, geodf):
    """ Function to return a transform matrix

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


def assignHealth(datasetReader, geodf, index):  # not complete
    """ Function to drop assign labels to zones imported rom shapefiles column
    in the GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        index : a string containing the name of index to be retrieved
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with one less column
    """
    clipGeoData = retClipGeoData(datasetReader, geodf, index)  # calling reWindowsRaster
    transform = retTransform(datasetReader, geodf)  # calling reWindowsRaster
    stats = rasterstats.zonal_stats(geodf.geometry, clipGeoData, affine=transform)
    i = 0
    for stat in stats:
        if stat['mean'] < 0.3:
            geodf.loc[i, 'health'] = 'bad'

        elif 0.3 <= stat['mean'] < 0.45:
            geodf.loc[i, 'health'] = 'ok'

        else:
            geodf.loc[i, 'health'] = 'good'

        geodf.loc[i, 'meanNDVI'] = stat['mean']
        i = i + 1
    return geodf


def fillMeanIndexValues(datasetReader, geodf, prodList):
    analysis = 'mean'
    meanValues = [analysis + x for x in prodList]
    i = 0
    for index in range(1, datasetReader.count + 1):
        stats = rasterstats.zonal_stats(geodf.geometry, retClipGeoData(datasetReader, geodf, index),
                                        affine=retTransform(datasetReader, geodf))
        # optimization needed in above code as windowsRaster() is being called two times
        for stat in stats:
            try:
                geodf.loc[i, meanValues[index - 1]] = stat['mean']
            except Exception as e:
                print(e)
            i = i + 1
        i = 0
    return geodf


def getZoneHealth(geodf):
    good = geodf[geodf.health == 'good']
    bad = geodf[geodf.health == 'bad']
    ok = geodf[geodf.health == 'ok']

    return good, bad, ok


def plotZoneHealth(geodf):
    good, bad, ok = getZoneHealth(geodf)

    good.plot(ax=plt.gca(), color='g')
    bad.plot(ax=plt.gca(), color='r')
    ok.plot(ax=plt.gca(), color='y')
    geodf.boundary.plot(ax=plt.gca(), color='k')
    plt.axis('off')
