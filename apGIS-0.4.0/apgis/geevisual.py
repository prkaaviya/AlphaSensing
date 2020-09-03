"""
Module for visualisation tools.

Library of top-level function to visualise Earth Engine objects by simulating the
Code Editor Map with a IpyLeaflet widget using the geemap package.\n
Visit link for more information on installation of geemap on Conda
https://github.com/giswqs/geemap

Methods: ..

Author: AntPod Designs Pvt Ltd.
"""
import ee
import geemap

import apgis.geebase as gee
import apgis.geeindex as index

Map = geemap.Map(zoom=1)
Map.add_basemap("SATELLITE")

# True Colour Visual Parameters
S2TC = {'bands': ['TCI_R', 'TCI_G', 'TCI_B'], 'min': 0, 'max': 255}

# MCARI Visual Parameters
mcariVis = {'palette': ['FFFFFF', 'BFBFBF', '7F7F7F', '404040', '000000']}

# NDWI Visual Parameters
ndwiVis = {'min': -0.8, 'max': 0.8, 'palette': ['FFFFFF', '513927', '5B5430', '587147', '438F72',
                                                '00AAAD', '006666', '004C4C', '000000', ]}

# NDVI Visual Parameters
ndviVis = {'min': 0.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                               '004C00', '023B01', '012E01', '011D01', '011301']}
# GNDVI Visual Parameters
gndviVis = {'min': 0.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                                '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                                '004C00', '023B01', '012E01', '011D01', '011301']}
# EVI Visual Parameters
eviVis = {'min': -0.5, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                               '004C00', '023B01', '012E01', '011D01', '011301']}
# ARVI Visual Parameters
arviVis = {'min': 0.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
                                               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
                                               '004C00', '023B01', '012E01', '011D01', '011301']}


def displayTrueRGB_S2(image: ee.Image):
    """doc"""
    if not isinstance(image, ee.Image):
        raise TypeError

    if not gee.verifyImage(image=image, mode="S2"):
        raise ValueError

    Map.addLayer(image, S2TC, 'True Colour RGB Layer')


def displayIndex(image: ee.Image,
                 visParam: dict,
                 indexName: str):
    """doc"""
    if not isinstance(image, ee.Image):
        raise TypeError

    Map.addLayer(image, visParam, '{} Layer'.format(indexName))


def displayNDVIMasks(imageCol: ee.ImageCollection):
    """doc"""
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError

    values = [-1, 0.25, 0.33, 0.4, 0.5, 1]
    zones = ['Zero Activity', 'Very Bad Health', 'Bad Health', 'Good Health', 'Very Good Health Layer']

    for i, value in enumerate(values, start=0):
        image = gee.extractImage(imageCol=imageCol, index=i)
        displayIndex(image=image, visParam=ndviVis, indexName=zones[i])
