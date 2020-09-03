"""
Base module for all Earth Engine modules.

Library of top-level functions to filter, verify, extract Images from ImageCollections.
It also contains function fix Image and ImageCollection properties and to mosaic ImageCollections.
Tools that generate ImageCollections with specified parameters are also found here.

Methods: verifyImage, verifyCollection, genCollection, extractImage, fixMetadata,
generateMosaicImage, generateMosaicCollection.

Author: AntPod Designs Pvt Ltd.
"""
import ee

import apgis.geetemporal as temporal
import apgis.apexception as apexception

from apgis.apdate import Date
from apgis.apconfig import Config

import typing
DateRange = typing.Tuple[Date, Date]

CONFIG = Config()


def verifyImage(image: ee.Image,
                mode: str):
    """ A function that verifies an Image according to a given mode.

    The function accepts a valid Sensor or Satellite ID as mode of verification.\n
    For Satellite IDs -> function evaluates for any valid Image acquired by the Satellite.\n
    For Sensor IDs -> function evaluates only for the specified Sensor Data Product.

    Keyword Args:
        image:          The Image that needs to be verified.
        mode:           The mode in which to verify. Accepts satellite and sensor IDs.
    Returns:
        A bool representing the verification.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if mode is invalid.
        EERuntimeError: if verification runtime fails.

    Examples:
        *Verifying Sentinel-2 Image:*
    ``>> flag = verifyImage(image=image, mode="S2")``

        *Verifying Sentinel-2 L2A Image:*
    ``>> flag = verifyImage(image=image, mode="L2A")``

        *Verifying Landsat-8 Image:*
    ``>> flag = verifyImage(image=image, mode="L8")``

    References:
        *Navigate to the Image Properties section of any dataset in the Earth Engine Catalog:*\n
    https://developers.google.com/earth-engine/datasets/catalog/
    """
    mapper = {
        "S2": {
            "S2": {
                "property": "PRODUCT_ID", "match": "S2"
            },
            "L2A": {
                "property": "PRODUCT_ID", "match": "L2A"
            },
            "L1C": {
                "property": "PRODUCT_ID", "match": "L1C"
            }
        },
        "L8": {
            "L8": {
                "property": "LANDSAT_ID", "match": "LC08"
            },
            "L8SR": {
                "property": "LANDSAT_ID", "match": "L1TP"
            }
        }
    }
    if not isinstance(mode, str):
        raise TypeError("Image Verification Failed @ type check: mode must be a str")
    if not isinstance(image, ee.Image):
        raise TypeError("Image Verification Failed @ type check: image must be an ee.Image")

    try:
        if mode in CONFIG.getSensors():
            sat = CONFIG.getSatfromSensor(sensor=mode)
        elif mode in CONFIG.getSatellites():
            sat = mode
        else:
            raise ValueError("@ mode ID check: Invalid mode.")

        checkField = mapper[sat][mode]
        # noinspection PyUnresolvedReferences
        ID = ee.String(image.get(checkField["property"]))
        if ID.getInfo() is None:
            return False

        # noinspection PyUnresolvedReferences
        flag = True if (ID.match(checkField["match"]).getInfo()) else False
        return flag

    except ValueError as e:
        raise ValueError(f"Image Verification Failed {e}")
    except Exception as e:
        raise apexception.EERuntimeError(f"Image Verification Failed @ EERuntime: {e}")


def verifyCollection(imageCol: ee.ImageCollection,
                     mode: str,
                     *args, **kwargs):
    """ A function that verifies an ImageCollection according to a given mode.

    The function accepts a valid Sensor and Satellite IDs as mode of verification.\n
    For Satellite IDs -> function evaluates for any valid ImageCollection associated with the Satellite.\n
    For Sensor IDs -> function evaluates only for the specified Sensor Data Product Collections.

    Keyword Args:
        imageCol:   The Image collection that needs to be verified.
        mode:       The mode in which to verify. Accepts satellite and sensor IDs.
    Returns:
       A bool representing the verification.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if mode is invalid.
        EERuntimeError: if verification runtime fails.

    Examples:
        *Verifying Sentinel-2 Collections:*
    ``>> flag = verifyCollection(imageCol=imageCol, mode="S2")``

        *Verifying Sentinel-2 L2A Collections:*
    ``>> flag = verifyCollection(imageCol=imageCol, mode="L2A")``

        *Verifying Landsat-8 Collections:*
    ``>> flag = verifyCollection(imageCol=imageCol, mode="L8")``

    References:
        *Navigate to the Image Properties section of any dataset in the Earth Engine Catalog:*\n
    https://developers.google.com/earth-engine/datasets/catalog/
    """
    mapper = {
        "S2": {
            "S2": {
                "property": "product_tags", "match": "msi"
            },
            "L2A": {
                "property": "product_tags", "match": "reflectance"
            },
            "L1C": {
                "property": "product_tags", "match": "radiance"
            }
        },
        "L8": {
            "L8": {
                "property": "product_tags", "match": "lc08"
            },
            "L8SR": {
                "property": "product_tags", "match": "l8sr"
            }
        }
    }
    if not isinstance(mode, str):
        raise TypeError("Collection Verification Failed @ type check: mode must be a str")
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError("Collection Verification Failed @ type check: imageCol must be an ee.ImageCollection")

    try:
        if mode in CONFIG.getSensors():
            sat = CONFIG.getSatfromSensor(sensor=mode)
        elif mode in CONFIG.getSatellites():
            sat = mode
        else:
            raise ValueError("@ mode ID check: Invalid mode.")

        checkField = mapper[sat][mode]
        # noinspection PyUnresolvedReferences
        tagString = ee.List(imageCol.get(checkField["property"])).join("-")
        flag = True if (tagString.match(checkField["match"]).getInfo()) else False

        return flag

    except ValueError as e:
        raise ValueError(f"Collection Verification Failed {e}")
    except Exception as e:
        raise apexception.EERuntimeError(f"Collection Verification Failed @ EERuntime: {e}")


def genCollection(sensor: str,
                  geometry: ee.Geometry,
                  daterange: DateRange,
                  cloudCover: int = None,
                  *args, **kwargs):
    """ A function that generates and filters an ImageCollection.

    The function generates an ImageCollection for a given sensor and filters it spatially and temporally.\n
    Accepts an ee.Geometry for spatial bounding and a 2 Date objects in a list for temporal bounding.
    The Dates are inclusive at both the start and the end of the daterange.\n
    Option to filter for Tile Cloudy Pixel Percentage, with a threshold integer above which all tiles are filtered out.

    Keyword Args:
        sensor:         The sensor ID for which to filter a collection.
        geometry:       The ee.Geometry along which to spatially bound.
        daterange:      A tuple of Dates containing a Start(incl) and an End(incl) date by which to temporally bound.
        cloudCover:     The threshold value for Cloudy Pixel Percentage.
    Returns:
        An ImageCollection that has been filtered by all the specified parameter.
    Raises:
        TypeError:      if parameter type check fails.
        EERuntimeError: if generation and filtering runtime fails.

    Examples:
        *Generating a Sentinel-2 L2A Collection:*
    ``>> imageCol = genCollection(sensor="L2A", geometry=aoi, daterange=[start, end])``\n
    where aoi is an ee.Geometry, start and end are Date objects.

        *Generating a Landsat-8 SR Collection with under 5% Cloud Cover:*
    ``>> imageCol = genCollection(sensor="L8SR", geometry=aoi, daterange=[start, end], cloudCover=5)``\n
    where aoi is an ee.Geometry, start and end are Date objects.

    References:
        Google Earth Engine Datasets: https://developers.google.com/earth-engine/datasets \n
    Any new datasets need to be added to the SensorMap configuration or can be filtered manually using the above code.
    """
    if sensor not in CONFIG.getSensors():
        raise ValueError("ImageCollection Generation Failed @ type check: Invalid sensor ID")

    if not isinstance(geometry, ee.Geometry):
        raise TypeError("ImageCollection Generation Failed @ type check: geo must be an ee.Geometry")

    if not isinstance(daterange[0], Date) or not (daterange[1], Date):
        raise TypeError("ImageCollection Generation Failed @ type check: daterange must be a list of Date objects")

    if cloudCover is not None:
        if isinstance(cloudCover, int):
            raise TypeError("ImageCollection Generation Failed @ type check: cloudCover must be an integer")

    try:
        collection = CONFIG.getGEECollection(sensor)
        startDate = daterange[0].eeDate
        endDate = daterange[1].nextDay().eeDate

        imageCol = ee.ImageCollection(collection).filterBounds(geometry).filterDate(startDate, endDate)

        # TODO: cloudCover is too specific for L2A. Implement dynamic property changing.
        if cloudCover is not None:
            imageCol = imageCol.filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', cloudCover)

        return imageCol

    except Exception as e:
        raise apexception.EERuntimeError(f"ImageCollection Generation Failed @ Runtime: {e}")


def extractImage(imageCol: ee.ImageCollection,
                 index: int = -1,
                 date: Date = None,
                 *args, **kwargs):
    """ A function that extracts an Image from an Image Collection.

    The function accepts either given a positional index as an integer or a Date object.\n
    For positional index -> the function treats the ImageCollection like an array and returns the Image
    at the passed positional index value.\n
    For Date object -> the function filter the ImageCollection for DateRange between the passed Date
    and the next Date, returns all Images available in the collection on the specified Date as a list.\n
    The Date mode takes precedence over the positional index mode.\n
    If no parameters are passed, the last Image in the collection (index = -1) is returned by default.

    Keyword Args:
        imageCol:   The ImageCollection from which the Image or Collection is to be extracted.
        index:      The positional index of the Image in the ImageCollection. Defaults to -1 (last)
        date:       A Date object with the date for which to retrieve an Image.
    Returns:
        An Image or a list of Images extracted from an ImageCollection depending on whether index or date was used.
    Raises:
        TypeError:      if parameter type check fails.
        EERuntimeError: if extraction runtime fails.
        EEEmptyCollectionError: if Date mode filtering returns an empty collection

    Examples:
        *Extracting an Image with a positional index:*
    ``>> image = extractImage(image=image, index=3)``\n

        *Extracting an Image with a Date:*
    ``>> imageList = extractImage(image=image, date=randomDate)``\n
    where randomDate is a Date object.
    """
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError("Image Extraction Failed @ type check: imageCol must be an ee.ImageCollection")

    if not isinstance(index, int):
        raise TypeError("Image Extraction Failed @ type check: index must be an int")

    if date is not None:
        if not isinstance(date, Date):
            raise TypeError("Image Extraction Failed @ type check: date must be a Date object")

        try:
            images = []
            imageCol = imageCol.filterDate(date.eeDate, date.nextDay().eeDate)
            if imageCol.size().getInfo() == 0:
                raise apexception.EEEmptyCollectionError(f"@ Collection Date Filtering: No Image on {date.ISOString}")

            # TODO: Implement with ee Iterate
            imageList = imageCol.toList(imageCol.size())
            for i in range(0, imageCol.size().getInfo()):
                image = ee.Image(imageList.get(i))
                images.append(image)

            return images

        except apexception.EEEmptyCollectionError as e:
            raise apexception.EEEmptyCollectionError(f"Image Extraction Failed {e}")
        except Exception as e:
            raise apexception.EERuntimeError(f"Image Extraction Failed @ Date Extraction: {e}")

    else:
        try:
            # noinspection PyUnresolvedReferences
            imageList = imageCol.toList(imageCol.size())
            image = ee.Image(imageList.get(index))
            # TODO: Implement out of bound check

            return image

        except Exception as e:
            raise apexception.EERuntimeError(f"Image Extraction Failed @ Index Extraction: {e}")


# noinspection PyUnresolvedReferences
def fixMetadata(image: ee.Image,
                sensor: str,
                aqDate: Date,
                precision: str = None,
                footprint: ee.Geometry = None,
                *args, **kwargs):
    """ A function that rebuilds Image metadata.

    The function restores the properties and associations of an Image for a specified Sensor ID.\n
    This function is intended to be used to rebuild Mosaic and Index images after their
    respective transformations which lead to them losing all properties.\n
    Accepts a Sensor ID used to assign an Image ID, a Date object that is assigned as the
    acquisition date of the Image. Additionally also accepts a Geometry which is assigned as the
    Image footprint and precision string which sets the type precision of each pixel in the Image.\n
    Pass rebuild metadata parameters by extracting them from the original image(before transformation).

    Keyword Args:
        image:          The image for which to rebuild metadata.
        sensor:         The sensor for which to add a corresponding generic ID string.
        aqDate:         The date as a Date object to be added to system:time_start.
        precision:      The datatype to cast all pixel values. Choose from double, float and int.
        footprint:      The AoI to add to system:footprint. Do Not Use for Mosaic Images.
    Returns:
        An Image with rebuild metadata and properties.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if invalid parameter values are passed.
        EERuntimeError: if metadata generation or image rebuild runtimes fail.
        NotImplementedError:    if Sensor ID is valid but not implemented internally in the function.

    Examples:
        *Fixing a Sentinel-2 L2A Image:*
    ``>> newImage = fixMetadata(image=image, sensor="L2A", aqDate=aqDate)``

        *Fixing a Sentinel-2 L2A Image, setting a pixelType and a footprint:*
    ``>> newImage = fixMetadata(image=image, sensor="L2A", aqDate=aqDate, precision="float", footprint=aoi)``
    """
    mapper = {
        "S2": {
            "L2A": {
                "idKey": "PRODUCT_ID",
                "idValue": "S2X_MSIL2A"
            },
            "L1C": {
                "idKey": "PRODUCT_ID",
                "idValue": "S2X_MSIL1C"
            }
        },
        "L8": {
            "L8SR": {
                "idKey": "LANDSAT_ID",
                "idValue": "LC08_L1TP"
            }
        }
    }
    if not isinstance(image, ee.Image):
        raise TypeError("Image Metadata Rebuild Failed @ type check: image must be an ee.Image")

    if isinstance(sensor, str):
        if sensor not in CONFIG.getSensors():
            raise ValueError("Image Metadata Rebuild Failed @ Sensor ID check: Invalid Sensor ID")
    else:
        raise TypeError("Image Metadata Rebuild Failed @ type check: sensor must be a str")

    if not isinstance(aqDate, Date):
        raise TypeError("Image Metadata Rebuild Failed @ type check: aqDate must be a Date object")

    sat = CONFIG.getSatfromSensor(sensor=sensor)
    checkField = mapper[sat][sensor]
    if checkField is None:
        raise NotImplementedError(f"Image Metadata Rebuild Failed @ Build Assign: Sensor {sensor} not Implemented.")

    try:
        aqDate = aqDate.epochMS

        aoi = None
        if footprint is not None:
            if not isinstance(footprint, ee.Geometry):
                raise TypeError("@ type check: footprint must be an ee.Geometry")

            aoi = footprint

        if precision is not None:
            if not isinstance(precision, str):
                raise TypeError("@ type check: precision must be a str")

            if precision not in ["double", "float", "int"]:
                raise ValueError(f"@ precision check: Invalid precision '{precision}' specified")

            if precision == "double":
                image = image.double()
            elif precision == "float":
                image = image.float()
            elif precision == "int":
                image = image.int()
            else:
                raise ValueError(f"@ precision setting: Invalid precision '{precision}' specified")

    except ValueError as e:
        raise ValueError(f"Image Metadata Rebuild Failed {e}")
    except TypeError as e:
        raise TypeError(f"Image Metadata Rebuild Failed {e}")
    except Exception as e:
        raise EERuntimeError(f"Image Metadata Rebuild Failed @ Metadata Generation: {e}")

    try:
        image = image.set({
            "system:time_start": aqDate,
            'system:footprint': aoi,
            checkField["idKey"]: checkField["idValue"],
        })

        return image

    except Exception as e:
        raise EERuntimeError(f"Image Metadata Rebuild Failed @ Image Rebuilding: {e}")


def generateMosaicImage(imageCol: ee.ImageCollection,
                        sensor: str,
                        date: Date,
                        *args, **kwargs):
    """ A function that generates a mosaic Image from an ImageCollection for a given Date.

    The function generates an Image that is a mosaic of all available Images for a given date
    in the ImageCollection provided. The metadata of the new Image is rebuilt with sensor ID provided.

    Keyword Args:
        imageCol:   The ImageCollection containing th Images to mosaic.
        date:       The Date for which to generate a mosaic Image.
        sensor:     The sensor with respect to which to rebuild metadata.
    Returns:
        A mosaic Image.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if invalid parameter values are passed.
        EERuntimeError: if mosaic runtime fail.

    Examples:
        *Generating a mosaic Sentinel-2 L2A Image:*
    ``>> mosImage = genMosaicImage(imageCol=imageCol, date=date, sensor="L2A")``
    """
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError("Mosaic Image Generation Failed @ type check: imageCol mst be an ee.ImageCollection")

    if not isinstance(date, Date):
        raise TypeError("Mosaic Image Generation Failed @ type check: date must be a Date object")

    if isinstance(sensor, str):
        if sensor not in CONFIG.getSensors():
            raise ValueError("Mosaic Image Generation Failed @ Sensor ID check: Invalid Sensor ID")
    else:
        raise TypeError("Mosaic Image Generation Failed @ type check: sensor must be a str")

    try:
        imageList = extractImage(imageCol=imageCol, date=date)

        # noinspection PyUnresolvedReferences
        mosImage = ee.ImageCollection(imageList).mosaic()
        mosImage = fixMetadata(image=mosImage, sensor=sensor, aqDate=date)

        return mosImage

    except Exception as e:
        raise apexception.EERuntimeError(f"Mosaic Image Generation Failed @ Runtime: {e}")


def generateMosaicCollection(imageCol: ee.ImageCollection,
                             sensor: str,
                             *args, **kwargs):
    """ A function that generates an ImageCollection of unique acquisitions.

    The function generates an ImageCollection which contains a collection of
    mosaic Images for each date in a datelist containing ISO dateStrings which
    is generated from all the unique acquisition dates in the ImageCollection.

    Keyword Args:
        imageCol:       The ImageCollection for which to generate mosaic Images.
        sensor:         The sensor ID for which to rebuild metadata.
    Returns:
        An ImageCollection of mosaic Images.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if invalid parameter values are passed.
        EERuntimeError: if mosaic iteration runtime fail.

    Examples:
        *Generating a mosaic Sentinel-2 L2A Image:*
    ``>> mosCol = genMosaicCollection(imageCol=imageCol, sensor="L2A")``
    """
    mapper = {
        "S2": {
            "L2A": {
                "tags": ['msi', 'reflectance']
            },
            "L1C": {
                "tags": ['msi', 'reflectance']
            }
        },
        "L8": {
            "L8SR": {
                "tags": ['lc08', 'l8sr']
            }
        }
    }
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError("Mosaic Collection Generation Failed @ type check: imageCol must be an ee.ImageCollection")

    if isinstance(sensor, str):
        if sensor not in CONFIG.getSensors():
            raise ValueError("Mosaic Collection Generation Failed @ Sensor ID check: Invalid Sensor ID")
    else:
        raise TypeError("Mosaic Collection Generation Failed @ type check: sensor must be a str")

    try:
        sat = CONFIG.getSatfromSensor(sensor=sensor)
        dateList = temporal.generateDateList(imageCol=imageCol)

        mosaicList = []
        for date in dateList:
            date = Date(date)
            mosaicImage = generateMosaicImage(imageCol=imageCol, date=date, sensor=sensor)
            mosaicList.append(mosaicImage)

        count = len(mosaicList)
        mosaicCol = ee.ImageCollection(mosaicList).set({"product_tags": mapper[sat][sensor]["tags"]})

        return mosaicCol, dateList, count

    except Exception as e:
        raise apexception.EERuntimeError(f"Mosaic Collection Generation Failed @ Runtime: {e}")
