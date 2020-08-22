"""
Module to handle Vector and Raster Manipulations for images exported using GEE library

Author: AntPod Designs Pvt Ltd
Contributors: Kaaviya Ramkumar
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
import warnings
warnings. filterwarnings("ignore")


def rasterCaller(userID, mapConfig, sensor, antpodProduct, status=False):
    """ Function to call mapper - dictionary of functions according to the products

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : one of {antpodL2ABands, antpodL2ATC, antpodL2AVI2, antpodL2AVI}
        status: to display status of function completion
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

    if status:
        print("Calling raster map ... successful")

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


def getRasterVI(userID, mapConfig, sensor, antpodProduct, status=False):
    """ Function to get raster tif files with VI bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod VI products
        status: to display status of function completion
    Returns:
        A list of tif images
    """
    filesVI = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '-' + "*.tif")
    filesVI.sort()

    if status:
        print("Found ", len(filesVI), " TIF files ... successful")

    return filesVI


def getRasterVI2(userID, mapConfig, sensor, antpodProduct, status=False):
    """ Function to get raster tif files with VI2 bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod VI2 products
        status: to display status of function completion
    Returns:
        A list of tif images
    """
    filesVI2 = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesVI2.sort()

    if status:
        print("Found ", len(filesVI2), " TIF files ... successful")

    return filesVI2


def getRasterBands(userID, mapConfig, sensor, antpodProduct,  status=False):
    """ Function to get raster tif files with raw Sentinel bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod Band products
        status: to display status of function completion
    Returns:
        A list of tif images
    """
    filesBands = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesBands.sort()

    if status:
        print("Found ", len(filesBands), " TIF files ... successful")

    return filesBands


def getRasterTC(userID, mapConfig, sensor, antpodProduct, status=False):
    """ Function to get raster tif files with TC bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod TC products
        status: to display status of function completion
    Returns:
        A list of tif images
    """
    filesTC = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '*.tif')
    filesTC.sort()

    if status:
        print("Found ", len(filesTC), " TIF files ... successful")

    return filesTC


def getRasterVXX(userID, mapConfig, sensor, antpodProduct, status=False):
    """ Function to get raster tif files with VI bands

    Args:
        userID : Antpod user ID
        mapConfig : Antpod map ID
        sensor : one of {'L2A','L1C'}
        antpodProduct : List of antpod VXX products
        status: to display status of function completion
    Returns:
        A list of tif images
    """
    filesVXX = glob(userID + '-' + mapConfig + '-' + sensor[0] + '-' + antpodProduct + '-' + "*.tif")
    filesVXX.sort()

    if status:
        print("Found ", len(filesVXX), " TIF files ... successful")

    return filesVXX


rasterMapper = {
    'VI': getRasterVI,
    'VI2': getRasterVI2,
    'TC': getRasterTC,
    'BANDS': getRasterBands,
    'VXX': getRasterVXX
}


def extractCollectionDates(meta, status=False):
    """ Function to get dates from multiple tif files

    Args:
        meta : dictionary of rasterio DatasetReader object
        status: to display status of function completion
    Returns:
        A list of strings (dates)
    """
    dates = [key for key in meta.keys()]

    if status:
        print(len(dates), " dates available ... successful")

    return dates


def extractSingleDate(file, status=False):
    """ Function to get dates from multiple tif files

    Args:
        file : a TIF image file
        status: to display status of function completion
    Returns:
        date : a string containing date of the file
    """
    if '.tif' in file:
        file = file.replace('.tif', '')
    date = '-'.join(file.split('-')[-3:])

    if status:
        print('Acquisition date : ', date, ' ... successful')

    return date


def openSingleRaster(file, status=False):
    """ Function to get dates from a single TIF file

    Args:
        file : a TIF image file
        status: to display status of function completion
    Returns:
        meta : dictionary of rasterio DatasetReader object
    """
    meta = rio.open(file)
    if status:
        date = extractSingleDate(file)
        print(meta.count, " bands available in the raster on ", date, " ... successful")

    return meta


def readMultipleRaster(datasetReader, status=False):
    """ Function to read the raster data and store them as numpy arrays for easy manipulation

    Args:
        datasetReader : a rasterio DatasetReader object
        status: to display status of function completion
    Returns:
        A numpy list of float values of the tif image for each bands present in datasetReader
    """
    numpyListofBands = [datasetReader.read(i) for i in range(1, datasetReader.count + 1)]

    if status:
        print(len(numpyListofBands), " Numpy arrays available ... successful")

    return numpyListofBands


def readMultipleDatasetReader(meta, status=False):
    """ Function to read the raster data and store them as numpy arrays for easy manipulation

    Args:
        meta : dictionary of Rasterio DatasetReader object
        status: to display status of function completion
    Returns:
        A numpy list of float values of the tif image for each bands present in all datasetReader objects
    """
    numpyListofList = [readMultipleRaster(meta[keys]) for keys in meta]

    if status:
        print(len(numpyListofList), " raster dataset reader available ... successful")

    return numpyListofList


def retBandBounds(datasetReader, status=False):
    """ Function to return bounds of a DatasetReader object

    Args:
        datasetReader : a rasterio DatasetReader object
        status: to display status of function completion
    Returns:
       a BoundingBox object of rasterio.coords module
    """
    bounds = datasetReader.bounds

    if status:
        print("Bounding box of dataset reader : ", bounds)

    return bounds


def showRaster(datasetReader, index, cmap='RdYlGn'):
    """ Function to plot numpy array obtained after reading rasterio DatasetReader (works
    best for NDVI, need to adjust max values for other indices)

    Args:
        datasetReader : a rasterio DatasetReader object
        index : an integer value specifying the index to locate in meta
        cmap : a colormap to plot the image  accordingly
    Returns:
       nil
    """
    plotIndex = datasetReader.read(index)
    rioplot.show(plotIndex, cmap=cmap)


def retGeoDF(file, status=False):
    """ Function to read a GeoJSON file format

    Args:
        file : a geojson file
        status: to display status of function completion
    Returns:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
    """
    if 'geojson' not in file:
        file = file + '.geojson'

    if file not in os.listdir():
        "ERROR : cannot locate the file in the given directory ... failed"
    else:
        geo = gpd.read_file(file)
        grid = createGrid(geo, status)
        geodf = overlayGrid(grid, geo)

        if status:
            print("Finishing overlay process ... successful")

        return geodf


def createGrid(geo, status=False):
    """ Function to create a 2D square grid map from GeoJSON geometry

    Args:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
        status: to display status of function completion
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
    grid = gpd.GeoDataFrame({'geometry': polygons})

    if status:
        print("Creating grids ... successful")
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
    from pyproj import CRS
    crs_proj = CRS("EPSG:4326")
    geo.to_crs(crs_proj)
    geo.to_crs(crs_proj)
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


def writeGeoJSON(filename, geodf, status=False):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        filename : a string
        status: to display status of function completion
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column with changed CRS
    """
    file = filename + '.geojson'
    geodf.to_file(file, driver='GeoJSON')

    if status:
        print("Exporting GeoJSON ... successful")


def setGeoDFCRS(geodf, epsg=4326):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        epsg : a coordinate reference system with a default value of 4326
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column with changed CRS
    """
    return geodf.to_crs(epsg=epsg)


def retGeoDFBounds(geodf, status=False):
    """ Function to return total bounds of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        status: to display status of function completion
    Returns:
        bounds : a numpy array with boundaries of GeoDataFrame in the form of
        maximum and minimum of latitudes and longitudes
    """
    bounds = geodf.total_bounds

    if status:
        print("Bounds of GeoDataFrame : ", bounds)

    return bounds


def retWindowRaster(datasetReader, geodf, status=False):
    """ Function to create a window that contains rectangular subset of rasterio
    DatasetReader object according to the bounding box of GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        status: to display status of function completion
    Returns:
        windowRaster : a windows.Window object to view a rectangular subset
        of a raster dataset
    """
    geodfBBox = retGeoDFBounds(geodf, status)
    windowRaster = datasetReader.window(*geodfBBox)

    if status:
        print("Creating raster window ... successful")

    return windowRaster


def retClipGeoData(datasetReader, geodf, index, status=False):
    """ Function to clip rectangular subset of rasterio DatasetReader object clipped
    according to the bounding box of GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        index : a string containing the name of index to be retrieved
        status: to display status of function completion
    Returns:
        windowRaster : a windows.Window object to view a rectangular subset
        of a raster dataset
        clipGeoData : a numpy subset array of the rasterio dataset file adjusted
        according to the window provided by GeoDataFrame boundaries
    """
    windowRaster = retWindowRaster(datasetReader, geodf, status)
    clipGeoData = datasetReader.read(index, window=windowRaster)

    if status:
        print("Clipping GeoDataFrame and Rasterio objects ... successful")

    return windowRaster, clipGeoData


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


def retTransform(datasetReader, windowRaster, status=False):
    """ Function to return a transform matrix

    Args:
        datasetReader : a single rasterio DatasetReader object
        windowRaster : a windows.Window object to view a rectangular subset
        of a raster dataset
        status: to display status of function completion
    Returns:
        transform : an affine transform for a datasetReader window
    """
    # windowRaster = retWindowRaster(datasetReader, geodf)
    # TODO: Check if the function is working and then remove the above line

    transform = datasetReader.window_transform(windowRaster)

    if status:
        print("Creating affine transform ... successful")

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
    windowRaster, clipGeoData = retClipGeoData(datasetReader, geodf, index)
    transform = retTransform(datasetReader, windowRaster)
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


def fillMeanIndexValues(datasetReader, geodf, prodList, status=False):
    """ Function to drop assign labels to zones imported rom shapefiles column
        in the GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        prodList : a list containing the name of indices
        status: to display status of function completion
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with the mean values of indices
        from prodList
    """
    analysis = 'mean'
    meanValues = [analysis + x for x in prodList]
    i = 0
    for index in range(1, datasetReader.count + 1):
        windowRaster, clipGeoData = retClipGeoData(datasetReader, geodf, index)
        transform = retTransform(datasetReader, windowRaster)
        stats = rasterstats.zonal_stats(geodf.geometry, clipGeoData,
                                        nodata=-999, affine=transform)
        for stat in stats:
            try:
                geodf.loc[i, meanValues[index - 1]] = stat['mean']
            except Exception as e:
                print(str(e))
            i = i + 1
        i = 0

        if status:
            print("Appending ", meanValues[index-1], ' values ... successful')

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
