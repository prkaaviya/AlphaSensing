import os
import antpodTest as apd

userID = "APX00000"
mapConfig = "XX"
sensor = ["L2A", "L1C"]
antpodProduct =  "VXX"
VXXProducts = ['NDVI', 'SAVI', 'AVI', 'EVI', 'ARVI', 'GNDVI', 'NDCI', 'NPCRI', 'PSRI', 'BSI', 'NDMI', 'NDWI', 'SI']

#%%
files = apd.rasterCaller(userID, mapConfig, sensor, antpodProduct)
meta = apd.openRaster(files, antpodProduct)
list_dates = apd.extractDates(meta)
geodf = apd.readShapefile(userID)
geodf = apd.setGeoDFCRS(geodf, epsg=4326)
#geodf.plot()

#%%
date = list_dates[0]
dataset = meta[date]

#%%
geodf = apd.fillMeanIndexValues(dataset, geodf, VXXProducts)
#csvFile = userID + '-' + mapConfig + '-' +  date + "-MEAN-INDICES.csv"
print("Acquistion date: ", date)
#geodf.to_csv(csvFile)
geodf
