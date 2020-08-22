class raster:
	@staticmethod
	def getData(geotiff):
		metadata = geotiff.split('.')[0].split('-')
		data = {'sensor': metadata[1], 'product': metadata[2]}

		# some operation

		return data

	@staticmethod
	def show(geotiff):
		meta = raster.getData(geotiff)

		# some operation

		print(f'{meta}')
    
	@staticmethod
	def fill(sensor, geotiff):
		if sensor.upper() == raster.getData(geotiff)['product']:
			print('present')
		else:
			print('absent')

		# some operation
 

geotiff = 'Antpod-L2A-VI2.tif'
sensor = 'vi2'
raster.fill(sensor, geotiff)