"""
Module to handle Vector and Raster Manipulations for images exported using GEE library

Author: AntPod Designs Pvt Ltd
Contributors: Kaaviya Ramkumar
"""

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
import os
from sys import exit
import warnings
warnings. filterwarnings("ignore")


def createGrid(geo, status: bool = False, side: float = 0.0005):
    """ Function to create a 2D square grid map from GeoJSON geometry

    Args:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
        status: to display status of function completion
        side : length of side of each grid with a default minimum values of
        0.0005
    Returns:
        grid : a GeoDataFrame as pandas.DataFrame with list of Polygons as grids
    """
    # bbox = [longmin, latmin, longmax, latmax] #bbox format
    # bbox = User.boi (once we interconnect User from GEE files)
    # ymin, xmin, ymax, xmax = bbox[0], bbox[1], bbox[2], bbox[3]

    xmin, ymin, xmax, ymax = geo.total_bounds
    rows = int(np.ceil((ymax - ymin) / side))
    cols = int(np.ceil((xmax - xmin) / side))
    XleftOrigin = xmin
    XrightOrigin = xmin + side
    YtopOrigin = ymax
    YbottomOrigin = ymax - side
    polygons = []

    try:
        for i in range(cols):
            Ytop = YtopOrigin
            Ybottom = YbottomOrigin
            for j in range(rows):
                polygons.append(
                    Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom),
                             (XleftOrigin, Ybottom)]))
                Ytop = Ytop - side
                Ybottom = Ybottom - side
            XleftOrigin = XleftOrigin + side
            XrightOrigin = XrightOrigin + side
    except Exception as e:
        print(str(e))

    grid = gpd.GeoDataFrame({'geometry': polygons})

    if status:
        print("Creating grids ... successful")

    return grid


def setGeoDFCRS(geodf, epsg=4326, status: bool = False):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        status: to display status of function completion
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        epsg : a coordinate reference system with a default value of 4326
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column with changed CRS
    """
    try:
        from pyproj import CRS
        newEPSG = "EPSG:" + str(epsg)
        crs_proj = CRS(newEPSG)
        return geodf.to_crs(crs_proj)

    except Exception as e:
        if status:
            print(str(e))


def overlayGrid(grid, geo, epsg):
    """ Function to create a 2D square grid map from GeoJSON geometry

    Args:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
        grid : a GeoDataFrame as pandas.DataFrame with list of Polygons as grids
        epsg : a coordinate reference system with a default value of 4326
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame that has been overlayed
        by a shapefile of grids
    """
    setGeoDFCRS(geo, epsg)
    setGeoDFCRS(grid, epsg)
    geodf = gpd.overlay(grid, geo)

    return geodf


def retGeoDF(geoFile, status: bool = False, epsg=4326):
    """ Function to read a GeoJSON file format

    Args:
        geoFile : a geojson file
        status: to display status of function completion
        epsg : a coordinate reference system with a default value of 4326
    Returns:
        geo : a GeoDataFrame as pandas.DataFrame with a geometry column
    """
    if 'geojson' not in geoFile:
        geoFile = geoFile + '.geojson'

    if geoFile not in os.listdir():
        exit("Cannot locate GeoJSON given directory ... failed")
    else:
        geo = gpd.read_file(geoFile)
        grid = createGrid(geo, status)
        geodf = overlayGrid(grid, geo, epsg)

        if status:
            print("Finishing overlay process ... successful")

        return geodf


def insertGeoDFCol(geodf, colName: str, value=0):
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


def dropGeoDFCol(geodf, colName: str):
    """ Function to drop existing column in the GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        colName : a string
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with one less column
    """
    geodf = geodf.drop([colName], axis=1)
    return geodf


def writeGeoJSON(filename: str, geodf, status: bool = False):
    """ Function to set coordinate reference system of a GeoDataFrame

    Args:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column
        filename : a string
        status: to display status of function completion
    Returns:
        geodf : a GeoDataFrame as pandas.DataFrame with a geometry column with changed CRS
    """
    file = filename + '.geojson'

    try:
        geodf.to_file(file, driver='GeoJSON')
    except Exception as e:
        print(str(e))

    if status:
        print("Exporting GeoJSON ... successful")
