"""
Module to handle Vector and Raster Manipulations for images exported using GEE library

Author: AntPod Designs Pvt Ltd
Contributors: Kaaviya Ramkumar
"""

from antpod.apUtils.sensorMap import *

import os
import warnings
import rasterstats
import rasterio as rio
from rasterio import plot

warnings.filterwarnings("ignore")


def extractSingleDate(tiffImage: str, status: bool = False):
    """ Function to get dates from multiple tif files

    Args:
        tiffImage : a TIF image file
        status: to display status of function completion
    Returns:
        date : a string containing date of the file
    """
    if '.tif' in tiffImage:
        tiffImage = tiffImage.replace('.tif', '')
    date = '-'.join(tiffImage.split('-')[-3:])

    if status:
        print('Acquisition date : ', date, ' ... successful')

    return date


def openSingleRaster(tiffImage: str, status: bool = False):
    """ Function to get dates from a single TIF file

    Args:
        tiffImage : a TIF image file
        status: to display status of function completion
    Returns:
        datasetReader : dictionary of rasterio DatasetReader object
    """
    datasetReader = rio.open(tiffImage)
    if status:
        date = extractSingleDate(tiffImage, status)
        print(datasetReader.count, " bands available in the raster on ", date, " ... successful")

    return datasetReader


def rasterCaller(tiffImage: str, status: bool = False):
    """ Function to call mapper - dictionary of functions according to the products

    Args:
        tiffImage : A tiff image file
        status : to display status of function completion
    Returns:
        datasetReader : dictionary of rasterio DatasetReader object
    """
    if tiffImage not in os.listdir():
        print('Image not found.')

    datasetReader = openSingleRaster(tiffImage)
    if status:
        print("Calling raster map ... successful")

    return datasetReader


def retBandBounds(datasetReader, status: bool = False):
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


def showRaster(datasetReader, antpodProduct: str, sensor: str, ind: str, cmap: str = 'RdYlGn'):
    """ Function to plot numpy array obtained after reading rasterio DatasetReader (works
    best for NDVI, need to adjust max values for other indices)

    Args:
        datasetReader : a rasterio DatasetReader object
        antpodProduct : a string containing name of the antpod product (band) to be displayed
        sensor : a string value specifying the sensor
        ind : an integer value for locating the index for datasetReader object
        cmap : a colormap to plot the image  accordingly
    Returns:
       nil
    """
    prod = getSensorProducts(sensor)
    if antpodProduct in prod:
        bands = prod[antpodProduct]
    else:
        print("Band not found in sensormap.json")
        return
    b = bands.index(ind)
    plotIndex = datasetReader.read(int(b+1))
    plot.show(plotIndex, cmap=cmap, title=ind)


def retGeoDFBounds(geodf, status: bool = False):
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


def retWindowRaster(datasetReader, geodf, status: bool = False):
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


def retClipGeoData(datasetReader, geodf, index: int, status: bool = False):
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


def retTransform(datasetReader, windowRaster, status: bool = False):
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


def fillMeanIndexValues(datasetReader, geodf, prodList: list, status: bool = False):
    """ Function to fill zonal statistics for AntPod products in the GeoDataFrame

    Args:
        datasetReader : a single rasterio DatasetReader object
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        prodList : a list containing the name of indices
        status: to display status of function completion
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with the mean values of indices
        from prodList
    """
    if len(prodList) != datasetReader.count:
        exit("Length of list and count of datasetReader do not match ... failed.")

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
            print("Appending ", meanValues[index - 1], ' values ... successful')

    return geodf
