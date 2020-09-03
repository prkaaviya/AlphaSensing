"""
Module for temporal manipulation functions.

Library of top-level function to generate temporal data and perform
manipulation on them. Contains functions to generate DateSets and DateLists.

Methods: generateDateSet, generateDateList.

Author: AntPod Designs Pvt Ltd.
"""
import ee

import apgis.geebase as gee
import apgis.apexception as apexception

from apgis.apdate import Date
from apgis.apconfig import Config

CONFIG = Config()


def generateDateSet(image: ee.Image,
                    sat: str,
                    *args, **kwargs):
    """ A function that generates the dateSet for images.

    The function retrieves a DateSet from an Image.
    The DateSet is a dictionary with the following specs:

    Keys in the returned dictionary are:
        - acqDate - Date of image acquisition.
        - genDate - Date of image generation.

    Image passed into the function must be associated with a
    valid satellite ID which must also be passed in.

    Keyword Args:
        image:      The image from which to retrieve datetime data.
        sat:        The satellite ID of the image.
    Returns:
        A dictionary of Date objects with string keys.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if Sat ID is invalid.
        EERuntimeError: if dateset generation runtime fails.

    Examples:
        *Generating a dateSet for a Sentinel-2 Image:*
    ``>> dateSet = Temporal.getDateSet(image=image, sat="S2")``\n

        *Generating a dateSet for a Landsat-8 Image:*
    ``>> dateSet = Temporal.getDateSet(image=image, sat="L8")``\n
    """
    mapper = {
        "S2": {
            "genField": "GENERATION_TIME"
        },
        "L8": {
            "genField": "LEVEL1_PRODUCTION_DATE"
        }
    }
    if not isinstance(image, ee.Image):
        raise TypeError(f"DateSet Generation Failed @ type check: image must be an ee.Image")

    if isinstance(sat, str):
        if sat not in CONFIG.getSatellites():
            raise ValueError("DateSet Generation Failed @ Sat ID check: Invalid Sat ID")
    else:
        raise TypeError("DateSet Generation Failed @ type check: sat must be a str")

    if not gee.verifyImage(image=image, mode=sat):
        raise ValueError(f"DateSet Generation Failed @ type check: image must be an Image of {sat}")

    try:
        checkField = mapper[sat]["genField"]

        # noinspection PyUnresolvedReferences
        acquisitionTime = image.date()
        if not isinstance(acquisitionTime, ee.Date):
            raise apexception.EERuntimeError("@ Acquisition Time Retrieval: "
                                             "acquisitionTime didn't turn up as an ee.Date")

        generationTime = int(image.get(checkField).getInfo())
        if generationTime is None:
            raise apexception.EERuntimeError("@ Generation Time Retrieval: generationTime turned up None")

        dateSet = {
            "acqDate": Date(acquisitionTime),
            "genDate": Date(generationTime)
        }

        return dateSet

    except apexception.EERuntimeError as e:
        raise apexception.EERuntimeError(f"DateSet Generation Failed {e}")
    except Exception as e:
        raise apexception.EERuntimeError(f"DateSet Generation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def generateDateList(imageCol: ee.ImageCollection, *args, **kwargs):
    """ A function that generates a list of ISO dateStings.

    The function generates a list of ISO Strings that represent
    the unique acquisition dates within an ImageCollection.\n
    Duplicate occurrences caused by adjacent acquisitions over a shared AoI are dropped
    favouring the first of any duplicates temporally.

    Keyword Args:
        imageCol:   The ImageCollection for which to generate a datelist.
    Returns:
        A list of ISO dateStrings.
    Raises:
        TypeError:      if parameter type check fails.
        EERuntimeError: if ee iteration runtime fails.
        RuntimeError:   if duplicate cleanup runtime fails.

    Examples:
        *Generating a datelist for any Collection:*
    ``>> dateList = Temporal.genDateList(imageCol=imageCol)``\n
    """
    if not isinstance(imageCol, ee.ImageCollection):
        raise TypeError("Datelist Generation Failed @ type check: imageCol must be an ee.ImageCollection")

    # noinspection PyUnresolvedReferences
    def algoIterateCollection(image, newList):
        """ An iteration algorithm that collect dates from each Image in an ImageCollection. """
        dtString = ee.String(image.date().format())
        newList = ee.List(newList).add(dtString).sort()
        return newList

    # noinspection PyUnresolvedReferences
    def algoIterateList(dtString, newList):
        """ An iteration algorithm that collects key-value pairs from an ISO datestring and returns
        a list containing lists that hold a date-time pair. """
        keyValues = ee.String(dtString).split("T")
        key = keyValues.get(0)
        val = keyValues.get(1)
        pairList = ee.List([key, val])
        newList = ee.List(newList).add(pairList)
        return newList

    try:
        dateList = ee.List(imageCol.iterate(algoIterateCollection, ee.List([])))
        datePair = ee.List(dateList.iterate(algoIterateList, ee.List([]))).getInfo()

    except Exception as e:
        raise apexception.EERuntimeError(f"Datelist Generation Failed @ EE Iteration Runtime: {e}")

    try:
        dateList = []
        for date, time in dict(datePair).items():
            dateList.append(date + "T" + time)

        return dateList

    except Exception as e:
        raise RuntimeError(f"Datelist Generation Failed @ Duplicate Cleanup Runtime: {e}")
