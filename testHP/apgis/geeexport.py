"""
Class module that implements the class *Export*.

The Export class is a static class that contains individual inner classes for different
Earth Engine Export formats like Image, Tables, Map and Video. Additionally custom implementation
is available for ImageCollections.
Individual inner classes hold all the methods required to process the export, generate the tasks
and to start and poll them.
Contains unary and batch export process functions to the cloud, drive, local OS and EE asset library.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import ee

import apgis.geebase as gee
import apgis.geeindex as index
import apgis.apexception as apexception

from apgis.aprequestlist import RequestList
from apgis.apfield import Field
from apgis.apdate import Date

INSTANTIATION_ERROR = "This class cannot be instantiated"


class Export:
    """
    *Class for Earth Engine Asset Export Handling.*

    **Sub Classes:**\n
    - ``Image:``        Class for Image exports.
    - ``ImageCollection:``  Class for ImageCollection exports.
    - ``Table:``         Class for Table exports.
    - ``Map:``      Class for Map exports.
    - ``Video:``        Class for Video exports.

    The Export class is a static class that contains individual inner classes for different
    Earth Engine Export formats like Image, Tables, Map and Video. Additionally custom implementation
    is available for ImageCollections.
    Individual inner classes hold all the methods required to process the export, generate the tasks
    and to start and poll them.
    Contains unary and batch export process functions to the cloud, drive, local OS and EE asset library.

    References:
        Some references related to this topic are:\n
    *Earth Engine Exports:*
    https://developers.google.com/earth-engine/guides/exporting
    """

    def __init__(self):
        """ **Forbids Class instantiation** """
        raise AssertionError(INSTANTIATION_ERROR)

    class Image:
        """
        *Class for ee.Image export processing, task generation and task execution.*

        **Class Methods:**
        - ``toDrive:``  A method to export Image to Google Drive.
        - ``toCloud:``  A method to export Image to Google Cloud Storage.
        - ``toAsset:``  A method to export Image to Google Earth Engine Asset Library.
        - ``toDisk:``   A method to export Image to Local Disk.
        """

        def __init__(self):
            """ **Forbids Class instantiation** """
            raise AssertionError(INSTANTIATION_ERROR)

        @staticmethod
        def __process_image_export__(image: ee.Image,
                                     requestList: RequestList) -> list:
            """ *A staticmethod to process and export request for Images.*

            All the bands that are required to be generated are created and added into a base image.
            The required bands are taken from the RequestList object. A Image is created for each product
            on the RequestList and then returned as a list of Images that are then processed by the
            export method that invokes this method.

            Args:
                image:      The image to be processed for export.
                requestList:    A RequestList object which contains in a list of strings, the products to be
                                exported as independent images along with relevant context such as satellite
                                and sensor names along with bands required to be generated.
            Returns:
                list:       A list of ee.Image objects for each product in the requestList
            Raises:
                TypeError:      Occurs if the parameter type checks fail.
                ValueError:     Occurs if the image is not associated with Sensor ID in requestList.
                EEExportError:      Occurs if band generation or export list generation runtimes fail.
            """
            if not isinstance(image, ee.Image):
                raise TypeError("Image Export Processing Failed @ type check: "
                                "image must be an ee.Image")

            if not isinstance(requestList, RequestList):
                raise TypeError("Image Export Processing Failed @ type check: "
                                "requestList must be a RequestList object")

            if not gee.verifyImage(image=image, mode=requestList.sensor):
                raise ValueError(f"Image Export Processing Failed @ image validation: "
                                 f"image must be a {requestList.sensor} acquisition")

            try:
                products = requestList.products
                reqBands = requestList.reqBands

                bandlist = []
                for band in reqBands:
                    indexBand = index.generateIndex(image=image, index=band, sensor=requestList.sensor)
                    bandlist.append(indexBand)

                for band in bandlist:
                    image = image.addBands(band)

            except Exception as e:
                raise apexception.EEExportError(f"Image Export Processing Failed @ band generation: {e}")

            try:
                exportList = []
                for product in products:
                    selection = requestList.sensorProducts[product]
                    export = image.select(selection)
                    exportList.append(export)

                return exportList

            except Exception as e:
                raise apexception.EEExportError(f"Image Export Processing Failed @ export list generation: {e}")

        @staticmethod
        def toDrive(image: ee.Image,
                    requestList: RequestList,
                    field: Field,
                    aqDate: Date,
                    folder: str = "Unassigned Exports",
                    dimensions=None, region=None, scale=10,
                    crs='EPSG:4326', crsTransform=None, maxPixels=100000000,
                    shardSize=None, fileDimensions=None, skipEmptyTiles=True,
                    fileFormat='GeoTIFF', formatOptions=None, *args, **kwargs):
            """ *A method to export Earth Engine Image to Google Drive.*

            The method takes export parameters that are supported by the EE Batch Export System for
            Google Drive Exports along with Request Layer objects for the AntPod Platform.\n

            Image is processed and all the bands that are required to be generated are
            created and added into a base image. The required bands are taken from the RequestList object.\n

            An Image is created for each product on the RequestList and then Google Drive Export tasks are
            created for each of the Images. This task list is returned.

            THE EARTH ENGINE SESSION MUST BE INITIALIZED WITH AN INTERNAL OAUTH CONFIGURATION.
            PROJECT ID/ SERVICE ACCOUNT AUTHENTICATION IS NOT ALLOWED FOR GOOGLE DRIVE EXPORTS.\n

            Export is uploaded to the Google Drive of the account associated with the Earth Engine
            Internal Config file.

            Args:
                image:          The image to be exported.
                requestList:    A RequestList object which contains in a list of strings, the products to be
                                exported as independent images along with relevant context.
                field:          A Field object containing parameters used to authenticate user and to construct
                                the export filename.
                aqDate:         The date of acquisition of the image to export. Used to construct the filename.
                folder:         The name of a unique folder in your Drive account to export into.
                dimensions:     The dimensions of the exported image. Takes either a single positive integer
                                as the maximum dimension or "WIDTHxHEIGHT" where WIDTH and HEIGHT are each
                                positive integers.
                region:         The lon,lat coordinates for a LinearRing or Polygon specifying the region to
                                export. Can be specified as a nested lists of numbers or a serialized string.
                                Defaults to the image's geometry.
                scale:          The resolution in meters per pixel. Defaults to the native resolution of the
                                image asset unless a crsTransform is specified.
                crs:            The coordinate reference system of the exported image's projection.
                                Defaults to the image's default projection. Defaults to 'EPSG:4326'
                crsTransform:   A comma-separated string of 6 numbers describing the affine transform of the
                                coordinate reference system of the exported image's projection, in the order:
                                xScale, xShearing, xTranslation, yShearing, yScale and yTranslation.
                                Defaults to the image's native CRS transform.
                maxPixels:      The maximum allowed number of pixels in the exported image. The task will fail
                                if the exported region covers more pixels in the specified projection.
                                Defaults to 100,000,000.
                shardSize:      Size in pixels of the shards in which this image will be computed.
                                Defaults to 256.
                fileDimensions: The dimensions in pixels of each image file, if the image is too large to fit
                                in a single file. May specify a single number to indicate a square shape,
                                or a tuple of two dimensions to indicate (width,height). Note that the image
                                will still be clipped to the overall image dimensions.
                                Must be a multiple of shardSize.
                skipEmptyTiles: If true, skip writing empty (i.e. fully-masked) image tiles. Defaults to False.
                fileFormat:     The string file format to which the image is exported. Currently only 'GeoTIFF'
                                and 'TFRecord' are supported, defaults to 'GeoTIFF'.
                formatOptions:  A dictionary of string keys to format specific options.
            Returns:
                list:       A list of unstarted Tasks.
            Raises:
                TypeError:      Occurs if the parameter type checks fail.
                ValueError:     Occurs if the image is not associated with Sensor ID in requestList.
                EEExportError:  Occurs if export runtime fails.
            """
            if not isinstance(image, ee.Image):
                raise TypeError("Google Drive Image Export Failed @ type check:"
                                "image must be an ee.Image")

            if not isinstance(requestList, RequestList):
                raise TypeError("Google Drive Image Export Failed @ type check:"
                                "requestList must be RequestList object")

            if not isinstance(field, Field):
                raise TypeError("Google Drive Image Export Failed @ type check:"
                                "field must be a Field object")

            if not isinstance(aqDate, Date):
                raise TypeError("Google Drive Image Export Failed @ type check:"
                                "aqDate must be a Date object")

            if not gee.verifyImage(image=image, mode=requestList.sensor):
                raise ValueError(f"Google Drive Image Export Failed @ image validation:"
                                 f"image must be a {requestList.sensor} acquisition")

            try:
                if not region:
                    region = field.eeROI

                # TODO: Implement dynamic scaling for different sensors.

                # TODO: Acquire date from either the image or the requestList. or
                #  cross verify and remove the argument parameter.

                stdConfig = {
                    "folder": folder,
                    "dimensions": dimensions,
                    "region": region,
                    "scale": scale,
                    "crs": crs,
                    "crsTransform": crsTransform,
                    "maxPixels": maxPixels,
                    "shardSize": shardSize,
                    "fileDimensions": fileDimensions,
                    "skipEmptyTiles": skipEmptyTiles,
                    "fileFormat": fileFormat,
                    "formatOptions": formatOptions
                }

            except Exception as e:
                raise apexception.EEExportError(f"Google Drive Image Export Failed @ Task Parameter Building: {e}")

            try:
                products = requestList.products
                exports = Export.Image.__process_image_export__(image=image, requestList=requestList)

                if len(exports) != len(products):
                    raise AssertionError("Export & Request Lists Size Mismatch")

            except apexception.EEExportError as e:
                raise apexception.EEExportError(f"Google Drive Image Export Failed @ Export Processing: {e}")

            try:
                filename = "-".join([field.apfieldID, requestList.sensor])

                tasklist = []
                for (export, product) in zip(exports, products):
                    taskConfig = {
                        "image": export,
                        "description": f"Drive Image Export Task-{product}",
                        "fileNamePrefix": "-".join([filename, product, aqDate.dateString]),
                    }
                    task = ee.batch.Export.image.toDrive(**taskConfig, **stdConfig)
                    tasklist.append(task)

                return tasklist

            except Exception as e:
                raise apexception.EEExportError(f"Google Drive Image Export Failed @ Task Generation: {e}")

        @staticmethod
        def toCloud(image: ee.Image,
                    requestList: RequestList,
                    field: Field,
                    aqDate: Date,
                    bucket="antpod-apgis-exports",
                    dimensions=None, region=None, scale=10,
                    crs='EPSG:4326', crsTransform=None, maxPixels=100000000,
                    shardSize=None, fileDimensions=None, skipEmptyTiles=True,
                    fileFormat='GeoTIFF', formatOptions=None, *args, **kwargs):
            """doc"""
            if not isinstance(image, ee.Image):
                raise TypeError("Google Cloud Image Export Failed @ type check:"
                                "image must be an ee.Image")

            if not isinstance(requestList, RequestList):
                raise TypeError("Google Cloud Image Export Failed @ type check:"
                                "requestList must be RequestList object")

            if not isinstance(field, Field):
                raise TypeError("Google Cloud Image Export Failed @ type check:"
                                "field must be a Field object")

            if not isinstance(aqDate, Date):
                raise TypeError("Google Cloud Image Export Failed @ type check:"
                                "aqDate must be a Date object")

            if not gee.verifyImage(image=image, mode=requestList.sensor):
                raise ValueError(f"Google Cloud Image Export Failed @ image validation:"
                                 f"image must be a {requestList.sensor} acquisition")

            try:
                if not region:
                    region = field.eeROI

                # TODO: Implement dynamic scaling for different sensors.

                # TODO: Acquire date from either the image or the requestList. or
                #  cross verify and remove the argument parameter.

                stdConfig = {
                    "bucket": bucket,
                    "dimensions": dimensions,
                    "region": region,
                    "scale": scale,
                    "crs": crs,
                    "crsTransform": crsTransform,
                    "maxPixels": maxPixels,
                    "shardSize": shardSize,
                    "fileDimensions": fileDimensions,
                    "skipEmptyTiles": skipEmptyTiles,
                    "fileFormat": fileFormat,
                    "formatOptions": formatOptions
                }

            except Exception as e:
                raise apexception.EEExportError(f"Google Cloud Image Export Failed @ Task Parameter Building: {e}")

            try:
                products = requestList.products
                exports = Export.Image.__process_image_export__(image=image, requestList=requestList)

                if len(exports) != len(products):
                    raise apexception.EEExportError("Export & Request Lists Size Mismatch")

            except apexception.EEExportError as e:
                raise apexception.EEExportError(f"Google Cloud Image Export Failed @ Export Processing: {e}")

            try:
                filename = "-".join([field.apfieldID, requestList.sensor])

                tasklist = []
                for (export, product) in zip(exports, products):
                    taskConfig = {
                        "image": export,
                        "description": f"Cloud Image Export Task-{product}",
                        "fileNamePrefix": "-".join([filename, product, aqDate.dateString]),
                    }
                    task = ee.batch.Export.image.toCloudStorage(**taskConfig, **stdConfig)
                    tasklist.append(task)

                return tasklist

            except Exception as e:
                raise apexception.EEExportError(f"Google Cloud Image Export Failed @ Task Generation: {e}")

        @staticmethod
        def toAsset(self):
            """doc"""
            raise NotImplementedError("Image Exports to EE Assets are unavailable at this time")

        @staticmethod
        def toDisk(self):
            """doc"""
            raise NotImplementedError("Image Exports to Local Disk are unavailable at this time")

    class ImageCollection:
        """
        *Class for ee.ImageCollection export processing, task generation and task execution.*

        **Class Methods:**\n
        - ``toDrive:``  A method to export ImageCollection to Google Drive.
        - ``toCloud:``  A method to export ImageCollection to Google Cloud Storage.
        - ``toAsset:``  A method to export ImageCollection to Google Earth Engine Asset Library.
        - ``toDisk:``   A method to export ImageCollection to Local Disk.
        """

        def __init__(self):
            """ Forbids Class instantiation """
            raise AssertionError(INSTANTIATION_ERROR)

        @staticmethod
        def __process_image_collection_export__(imageCol: ee.ImageCollection,
                                                requestList: RequestList):
            """ *A staticmethod to process and export request for ImageCollections.*

            All the bands that are required to be generated are created and added into
            each image in the collection. The required bands are taken from the RequestList object.
            The band generation math is mapped over the entire collection.\n
            Collection exports are just iterative batch exports i.e an Image is created for each product
            on the RequestList for each Image in the ImageCollection and then returned as a list of list of
            Images that are then processed by the export method that invokes this method.

            Args:
                imageCol:       The imageCollection to be processed for export.
                requestList:    A RequestList object which contains in a list of strings, the products to be
                                exported as independent images along with relevant context such as satellite
                                and sensor names along with bands required to be generated.
            Returns:
                list:       A list containing a list of ee.Image objects for each Image in the Collection.
                list:       The list of Images contains an Image for each product in the requestList
            Raises:
                TypeError:      if parameter type checks fail.
                ValueError:     if imageCollection is not associated with Sensor ID in requestList.
                EEExportError:  if band generation or export list generation runtimes fail.
            """
            if not isinstance(imageCol, ee.ImageCollection):
                raise TypeError("ImageCollection Export Processing Failed @ type check: "
                                "imageCol must be an ee.ImageCollection")

            if not isinstance(requestList, RequestList):
                raise TypeError("ImageCollection Export Processing Failed @ type check: "
                                "requestList must be a RequestList object")

            try:
                mosCol, datelist, count = gee.generateMosaicCollection(imageCol=imageCol, sensor=requestList.sensor)

                if not gee.verifyCollection(imageCol=mosCol, mode=requestList.sensor):
                    raise ValueError(f"ImageCollection Export Processing Failed @ collection validation: "
                                     f"image must be a {requestList.sensor} acquisition")

            except Exception as e:
                raise apexception.EEExportError(f"ImageCollection Export Processing Failed @ mosaic generation: {e}")

            try:
                products = requestList.products
                sat = requestList.sat

                for product in products:
                    imagelist = []
                    productCol = mosCol.map(index.INDEX_MAP[sat][product])

                    # TODO: Implement with EE Iterate.
                    for i in range(0, count):
                        image = gee.extractImage(imageCol=productCol, index=i)
                        image = gee.fixMetadata(image=image, sensor="L2A", aqDate=Date(datelist[i]))
                        imagelist.append(image)

                    productCol = ee.ImageCollection(imagelist)
                    mosCol = mosCol.combine(productCol)

            except Exception as e:
                raise apexception.EEExportError(f"ImageCollection Export Processing Failed @ band generation: {e}")

            try:
                sensorProducts = requestList.sensorProducts

                exportList = []
                for i in range(0, count):
                    image = gee.extractImage(imageCol=mosCol, index=i)

                    exportProductList = []
                    for product in products:
                        export = image.select(sensorProducts[product])
                        exportProductList.append(export)

                    exportList.append(exportProductList)

                return exportList, datelist

            except Exception as e:
                raise apexception.EEExportError(f"ImageCollection Export Processing Failed @ "
                                                f"export list generation: {e}")

        @staticmethod
        def toDrive(imageCol: ee.ImageCollection,
                    requestList: RequestList,
                    field: Field,
                    folder: str = "Unassigned Exports",
                    dimensions=None, region=None, scale=10,
                    crs='EPSG:4326', crsTransform=None, maxPixels=100000000,
                    shardSize=None, fileDimensions=None, skipEmptyTiles=True,
                    fileFormat='GeoTIFF', formatOptions=None, *args, **kwargs) -> list:
            """ *A method to export Earth Engine ImageCollection to Google Drive.*

            The method takes export parameters that are supported by the EE Batch Export System for
            Google Drive Exports along with Request Layer objects for the AntPod Platform.\n

            ImageCollection is processed by creating a collection of mosaic Images such that there is
            one Image for each unique acquisition date in the ImageCollection.\n
            Band generation algorithms are mapped over the entire collection.
            The required bands are taken from the RequestList object.\n

            Collection exports are just iterative batch exports i.e an Image is created for each product
            on the RequestList for each Image in the ImageCollection.
            A task is created for each Image and each product for each Image and then returned as a
            list of list of tasks.

            THE EARTH ENGINE SESSION MUST BE INITIALIZED WITH AN INTERNAL OAUTH CONFIGURATION.
            PROJECT ID/ SERVICE ACCOUNT AUTHENTICATION IS NOT ALLOWED FOR GOOGLE DRIVE EXPORTS.\n

            Export is uploaded to the Google Drive of the account associated with the Earth Engine
            Internal Config file.

            Args:
                imageCol:       The image to be exported.
                requestList:    A RequestList object which contains in a list of strings, the products to be
                                exported as independent images along with relevant context.
                field:          A Field object containing parameters used to authenticate user and to construct
                                the export filename.

                folder:         The name of a unique folder in your Drive account to export into.
                dimensions:     The dimensions of the exported image. Takes either a single positive integer
                                as the maximum dimension or "WIDTHxHEIGHT" where WIDTH and HEIGHT are each
                                positive integers.
                region:         The lon,lat coordinates for a LinearRing or Polygon specifying the region to
                                export. Can be specified as a nested lists of numbers or a serialized string.
                                Defaults to the image's geometry.
                scale:          The resolution in meters per pixel. Defaults to the native resolution of the
                                image asset unless a crsTransform is specified.
                crs:            The coordinate reference system of the exported image's projection.
                                Defaults to the image's default projection. Defaults to 'EPSG:4326'
                crsTransform:       A comma-separated string of 6 numbers describing the affine transform of the
                                    coordinate reference system of the exported image's projection, in the order:
                                    xScale, xShearing, xTranslation, yShearing, yScale and yTranslation.
                                    Defaults to the image's native CRS transform.
                maxPixels:          The maximum allowed number of pixels in the exported image. The task will fail
                                    if the exported region covers more pixels in the specified projection.
                                    Defaults to 100,000,000.
                shardSize:          Size in pixels of the shards in which this image will be computed.
                                    Defaults to 256.
                fileDimensions:     The dimensions in pixels of each image file, if the image is too large to fit
                                    in a single file. May specify a single number to indicate a square shape,
                                    or a tuple of two dimensions to indicate (width,height). Note that the image
                                    will still be clipped to the overall image dimensions.
                                    Must be a multiple of shardSize.
                skipEmptyTiles:     If true, skip writing empty (i.e. fully-masked) image tiles. Defaults to False.
                fileFormat:         The string file format to which the image is exported. Currently only 'GeoTIFF'
                                    and 'TFRecord' are supported, defaults to 'GeoTIFF'.
                formatOptions:      A dictionary of string keys to format specific options.
            Returns:
                list:       A list of lists that contain unstarted Tasks.
            Raises:
                TypeError:          if parameter type checks fail.
                ValueError:         if if collection is not associated with Sensor ID in requestList.
                EEExportError:      if export runtime fails.
            """
            if not isinstance(imageCol, ee.ImageCollection):
                raise TypeError("Google Drive ImageCollection Export Failed @ type check:"
                                "image must be an ee.Image")

            if not isinstance(requestList, RequestList):
                raise TypeError("Google Drive ImageCollection Export Failed @ type check:"
                                "requestList must be RequestList object")

            if not isinstance(field, Field):
                raise TypeError("Google Drive ImageCollection Export Failed @ type check:"
                                "field must be a Field object")

            if not gee.verifyCollection(imageCol=imageCol, mode=requestList.sensor):
                raise ValueError(f"Google Drive ImageCollection Export Failed @ image validation:"
                                 f"image must be a {requestList.sensor} acquisition")

            try:
                if not region:
                    region = field.eeROI

                stdConfig = {
                    "folder": folder,
                    "dimensions": dimensions,
                    "region": region,
                    "scale": scale,
                    "crs": crs,
                    "crsTransform": crsTransform,
                    "maxPixels": maxPixels,
                    "shardSize": shardSize,
                    "fileDimensions": fileDimensions,
                    "skipEmptyTiles": skipEmptyTiles,
                    "fileFormat": fileFormat,
                    "formatOptions": formatOptions
                }

            except Exception as e:
                raise apexception.EEExportError(f"Google Drive ImageCollection Export Failed @ "
                                                f"Task Parameter Building: {e}")

            try:
                products = requestList.products
                exportList, datelist = Export.ImageCollection.__process_image_collection_export__(imageCol, requestList)

                if len(exportList) != len(datelist):
                    raise apexception.EEExportError("ExportList & Date Lists Size Mismatch")

                if len(exportList[0]) != len(products):
                    raise apexception.EEExportError("Exports & Product Lists Size Mismatch")

            except apexception.EEExportError as e:
                raise apexception.EEExportError(f"Google Drive ImageCollection Export Failed @ Export Processing: {e}")

            try:
                filename = "-".join([field.apfieldID, requestList.sensor])

                taskList = []
                for (imagelist, date) in zip(exportList, datelist):
                    aqDate = Date(date).dateString
                    exports = imagelist

                    productTaskList = []
                    for (export, product) in zip(exports, products):
                        taskConfig = {
                            "image": export,
                            "description": f"Drive Image Export Task-{product}",
                            "fileNamePrefix": "-".join([filename, product, aqDate]),
                        }
                        task = ee.batch.Export.image.toDrive(**taskConfig, **stdConfig)
                        productTaskList.append(task)

                    taskList.append(productTaskList)

                return taskList

            except Exception as e:
                raise apexception.EEExportError(f"Google Drive ImageCollection Export Failed @ Task Generation: {e}")

        @staticmethod
        def toCloud(imageCol: ee.ImageCollection,
                    requestList: RequestList,
                    field: Field,
                    bucket="antpod-apgis-exports",
                    dimensions=None, region=None, scale=10,
                    crs='EPSG:4326', crsTransform=None, maxPixels=100000000,
                    shardSize=None, fileDimensions=None, skipEmptyTiles=True,
                    fileFormat='GeoTIFF', formatOptions=None, *args, **kwargs):
            """doc"""
            if not isinstance(imageCol, ee.ImageCollection):
                raise TypeError("Google Cloud ImageCollection Export Failed @ type check:"
                                "image must be an ee.Image")

            if not isinstance(requestList, RequestList):
                raise TypeError("Google Cloud ImageCollection Export Failed @ type check:"
                                "requestList must be RequestList object")

            if not isinstance(field, Field):
                raise TypeError("Google Cloud ImageCollection Export Failed @ type check:"
                                "field must be a Field object")

            if not gee.verifyCollection(imageCol=imageCol, mode=requestList.sensor):
                raise ValueError(f"Google Cloud ImageCollection Export Failed @ image validation:"
                                 f"image must be a {requestList.sensor} acquisition")

            try:
                if not region:
                    region = field.eeROI

                stdConfig = {
                    "bucket": bucket,
                    "dimensions": dimensions,
                    "region": region,
                    "scale": scale,
                    "crs": crs,
                    "crsTransform": crsTransform,
                    "maxPixels": maxPixels,
                    "shardSize": shardSize,
                    "fileDimensions": fileDimensions,
                    "skipEmptyTiles": skipEmptyTiles,
                    "fileFormat": fileFormat,
                    "formatOptions": formatOptions
                }

            except Exception as e:
                raise apexception.EEExportError(f"Google Drive ImageCollection Export Failed @ "
                                                f"Task Parameter Building: {e}")

            try:
                products = requestList.products
                exportList, datelist = Export.ImageCollection.__process_image_collection_export__(imageCol, requestList)

                if len(exportList) != len(datelist):
                    raise apexception.EEExportError("ExportList & Date Lists Size Mismatch")

                if len(exportList[0]) != len(products):
                    raise apexception.EEExportError("Exports & Product Lists Size Mismatch")

            except apexception.EEExportError as e:
                raise apexception.EEExportError(f"Google Cloud ImageCollection Export Failed @ Export Processing: {e}")

            try:
                filename = "-".join([field.apfieldID, requestList.sensor])

                taskList = []
                for (imagelist, date) in zip(exportList, datelist):
                    aqDate = Date(date).dateString
                    exports = imagelist

                    productTaskList = []
                    for (export, product) in zip(exports, products):
                        taskConfig = {
                            "image": export,
                            "description": f"Cloud Image Export Task-{product}",
                            "fileNamePrefix": "-".join([filename, product, aqDate]),
                        }
                        task = ee.batch.Export.image.toCloudStorage(**taskConfig, **stdConfig)
                        productTaskList.append(task)

                    taskList.append(productTaskList)

                return taskList

            except Exception as e:
                raise apexception.EEExportError(f"Google Cloud ImageCollection Export Failed @ Task Generation: {e}")

        @staticmethod
        def toAsset(self):
            """doc"""
            raise NotImplementedError("ImageCollection Exports to EE Assets are unavailable at this time")

        @staticmethod
        def toDisk(self):
            """doc"""
            raise NotImplementedError("ImageCollection Exports to Local Disk are unavailable at this time")

    class Table:
        """
        *Static Class for ee.Feature and ee.FeatureCollection export processing, task generation and task execution.*

        **Class Methods:**\n
        - ``toDrive:``  A method to export Table to Google Drive.
        - ``toCloud:``  A method to export Table to Google Cloud Storage.
        - ``toAsset:``  A method to export Table to Google Earth Engine Asset Library.
        - ``toDisk:``   A method to export Table to Local Disk.
        """
        def __init__(self):
            """ **Forbids Class instantiation** """
            raise AssertionError(INSTANTIATION_ERROR)

        @staticmethod
        def __processTableExport__():
            """doc"""
            raise NotImplementedError("Table Exports are unavailable at this time")

        @staticmethod
        def toDrive(self):
            """doc"""
            raise NotImplementedError("Table Exports to Drive are unavailable at this time")

        @staticmethod
        def toCloud(self):
            """doc"""
            raise NotImplementedError("Table Exports to Cloud Storage are unavailable at this time")

        @staticmethod
        def toAsset(self):
            """doc"""
            raise NotImplementedError("Table Exports to EE Assets are unavailable at this time")

    class Map:
        """
        *Static Class for Map export processing, task generation and task execution.*

        **Class Methods:**\n
        - ``toDrive:``  A method to export Map to Google Drive.
        - ``toCloud:``  A method to export Map to Google Cloud Storage.
        - ``toAsset:``  A method to export Map to Google Earth Engine Asset Library.
        - ``toDisk:``   A method to export Map to Local Disk.
        """
        def __init__(self):
            """ **Forbids Class instantiation** """
            raise AssertionError(INSTANTIATION_ERROR)

        @staticmethod
        def __processMapExport__():
            """doc"""
            raise NotImplementedError("Map Exports are unavailable at this time")

        @staticmethod
        def toDrive(self):
            """doc"""
            raise NotImplementedError("Map Exports to Drive are unavailable at this time")

        @staticmethod
        def toCloud(self):
            """doc"""
            raise NotImplementedError("Map Exports to Cloud Storage are unavailable at this time")

        @staticmethod
        def toAsset(self):
            """doc"""
            raise NotImplementedError("Map Exports to EE Assets are unavailable at this time")

    class Video:
        """
        *Static Class for Video export processing, task generation and task execution.*

        **Class Methods:**\n
        - ``toDrive:``  A method to export Video to Google Drive.
        - ``toCloud:``  A method to export Video to Google Cloud Storage.
        - ``toAsset:``  A method to export Video to Google Earth Engine Asset Library.
        - ``toDisk:``   A method to export Video to Local Disk.
        """
        def __init__(self):
            """ **Forbids Class instantiation** """
            raise AssertionError(INSTANTIATION_ERROR)

        @staticmethod
        def __processVideoExport__():
            """doc"""
            raise NotImplementedError("Video Exports are unavailable at this time")

        @staticmethod
        def toDrive(self):
            """doc"""
            raise NotImplementedError("Video Exports to Drive are unavailable at this time")

        @staticmethod
        def toCloud(self):
            """doc"""
            raise NotImplementedError("Video Exports to Cloud Storage are unavailable at this time")

        @staticmethod
        def toAsset(self):
            """doc"""
            raise NotImplementedError("Video Exports to EE Assets are unavailable at this time")
