"""
Created on Mon Jul  6 15:44:48 2020

@author: prkaa
"""
#%%
import antpodTest as apd

#%%
userID = "APX00001"
mapConfig = "XX"
sensor = ["L2A", "L1C"]
antpodProduct = ["VI2", "VI"]
VI2Products =['NDVI' ,'GNDVI', 'PSRI', 'NDCI']
VIProducts = ['EVI', 'SAVI', 'ARVI'] 
products = {}
products["VI2"] = ['NDVI' ,'GNDVI', 'PSRI', 'NDCI']
products["VI"] = ['EVI', 'SAVI', 'ARVI'] 

#%%

geodf = apd.readShapefile()
geodf = apd.setGeoDFCRS(geodf, epsg=4326)

#%%

for prod,values in products.items() :
    
    files = apd.rasterCaller(userID, mapConfig, sensor, prod)
    meta = apd.openRaster(files, prod)
    numpyListofList = apd.readMultipleDatasetReader(meta)
    list_dates = apd.extractDates(meta)
    date = list_dates[32]
    print("Acquistion date: ", date)
    dataset = meta[date]
    geodf = apd.fillMeanIndexValues(dataset,geodf,values)
    
    