class raster:
	meta = {}

	@classmethod
	def __init__(cls, geotiff):
		cls.meta = raster.getData(geotiff)

	@classmethod
	def getData(cls, geotiff):
		metadata = geotiff.split('.')[0].split('-')
		data = {'sensor': metadata[1], 'product': metadata[2]}
		cls.meta = data

		# some operation

		return data

	@classmethod
	def show(cls):
		metax = cls.meta
		print(f'{metax}')
    
	@classmethod
	def fill(cls, sensor):
		if sensor.upper() == cls.meta['product']:
			print('present')
		else:
			print('absent')

		# some operation

geotiff = 'Antpod-L2A-VI2.tif'
print(f'{raster.meta}\n')
raster(geotiff)
print(f'{raster.meta}\n')

sensor = 'vi2'
raster.fill(sensor)