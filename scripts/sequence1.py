# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 14:20:35 2020

@author: prkaa
"""

import antpod7 as apd
import os

#%%

userID = "APX00001"
mapConfig = "XX"
sensor = ["L2A", "L1C"]
antpodProduct = "BANDS"

#%%
def gotoTiffDirectory():
    curDirectory = os.getcwd()
    if 'tiff' in os.listdir():
        os.chdir(os.path.join(curDirectory,'tiff'))
    else:
        print('ERROR: Tiff images are not in the directory.')
        
def gotoShpDirectory():
    curDirectory = os.getcwd()
    if 'shapefiles' in os.listdir():
        os.chdir(os.path.join(curDirectory,'shapefiles'))
    else:
        print('ERROR: Shapefile is not in the directory.')

#%%

filesRaster = apd.rasterCaller(userID, mapConfig, sensor, antpodProduct)

meta = apd.openRaster(filesRaster, antpodProduct)


#%%

listDates = apd.extractDates(meta)

numpyListofBands = apd.readMultipleDatasetReader(meta)

gotoShpDirectory()

shapefile = list(glob('*.shp'))

geodf = readShapefile(shapefile[0])

geodf = setGeoDFCRS(geodf, epsg=4326)

bounds = retGeoDFBounds(geodf)

multipleWindowRaster = multipleWindowing(meta, geodf)

multipleClipGeoData = multipleClipping(meta, geodf)

#%%
