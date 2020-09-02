# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 16:39:58 2020

@author: prkaa
"""

#%%
import antpodTest as apd

#%%
userID = "APX00001"
mapConfig = "XX"
sensor = ["L2A", "L1C"]
antpodProduct = "VI2"

files = apd.rasterCaller(userID, mapConfig, sensor, antpodProduct)
meta = apd.openRaster(files, antpodProduct)
numpyListofList = apd.readMultipleDatasetReader(meta)
list_dates = apd.extractDates(meta)
date = list_dates[32]

dataset = meta[date]

geodf = apd.readShapefile()

geodf = apd.setGeoDFCRS(geodf, epsg=4326)
apd.plotShapefileOnRaster(dataset, geodf,1, cmap='RdYlGn')

#%%
VI2Products =['NDVI' ,'GNDVI', 'PSRI', 'NDCI']

    
geodf = apd.fillMeanIndexValues(dataset,geodf,VI2Products)

#%%

antpodProduct = "VI"
files2 = apd.rasterCaller(userID, mapConfig, sensor, antpodProduct)
meta2 = apd.openRaster(files2, antpodProduct)
dataset2 = meta2[date]


VIProducts = ['EVI', 'SAVI', 'ARVI'] 

geodf = apd.fillMeanIndexValues(dataset2,geodf,VIProducts)

#%%

geodf = apd.insertGeoDFCol(geodf, 'date', date)