"""
Module for index generation and bandmath functions.

Library of top-level functions to perform bandmath for Image and
generate remote sensing indices such as NDVI, NDWI and EVI.
Additionally contains functions to generate indices an d rebuild the metadata
of the subsequent image and to generate range masks for an index image.

Methods: Sentinel-2 Bandmath Methods, Landsat-8 Bandmath Methods, generateIndex, generateIndexMasks.

Author: AntPod Designs Pvt Ltd.
"""
import ee

import apgis.geebase as gee
import apgis.apexception as apexception

from apgis.apdate import Date
from apgis.apconfig import Config

CONFIG = Config()


# noinspection PyUnresolvedReferences
def calculateNDVI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDVI = (NIR - RED) / (NIR + RED)
    """
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi


def calculateSAVI_S2(image: ee.Image):
    """ A function to calculate the *Soil Adjusted Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        SAVI = ((NIR - RED) / (NIR + RED + SCF)) * (1 + SBCF)
    *SBCF: Soil Brightness Correction Factor* = ``0.428``
    """
    savi = image.expression("((NIR-RED)/(NIR+RED+SBCF))*(1+SBCF)", {"NIR": image.select('B8'),
                                                                    "RED": image.select('B4'),
                                                                    "SBCF": 0.428})
    savi = savi.rename('SAVI')
    return savi


def calculateAVI_S2(image: ee.Image):
    """ A function to calculate the *Advanced Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        AVI = (NIR * (1 - RED) * (NIR - RED)) ** (1/3)
    """
    avi = image.expression("(NIR*(1-RED)*(NIR-RED))", {"NIR": image.select('B8'),
                                                       "RED": image.select('B4')})
    avi = avi.cbrt().rename('AVI')
    return avi


def calculateEVI_S2(image: ee.Image):
    """ A function to calculate the *Enhanced Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        EVI = 2.5 * (NIR - RED) / (NIR + (6 * RED) - (7.5 * BLUE) + 1)
    """
    evi = image.expression("(2.5*(NIR-RED))/(NIR+(6*RED)-(7.5*BLUE)+1)", {"NIR": image.select('B8'),
                                                                          "RED": image.select('B4'),
                                                                          "BLUE": image.select('B2')})
    evi = evi.rename('EVI')
    return evi


def calculateARVI_S2(image: ee.Image):
    """ A function to calculate the *Atmospherically Resistant Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        ARVI = NIR - RED - (0.106 * (RED - BLUE)) / (NIR + RED - (0.106 * (RED-BLUE)))
    """
    arvi = image.expression("(NIR-RED-(0.106*(RED-BLUE)))/(NIR+RED-(0.106*(RED-BLUE)))",
                            {"NIR": image.select('B8'),
                             "RED": image.select('B4'),
                             "BLUE": image.select('B2')})
    arvi = arvi.rename('ARVI')
    return arvi


# noinspection PyUnresolvedReferences
def calculateGNDVI_S2(image: ee.Image):
    """ A function to calculate the *Green Normalized Difference Vegetation Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        GNDVI = (NIR - GREEN) / (NIR + GREEN)
    """
    gndvi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    return gndvi


# noinspection PyUnresolvedReferences
def calculateNDCI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Chlorophyll Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDCI = (REDEDGE - RED) / (REDEDGE + RED)
    """
    ndci = image.normalizedDifference(['B5', 'B4']).rename('NDCI')
    return ndci


# noinspection PyUnresolvedReferences
def calculateNPCRI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Pigment Chlorophyll Ratio Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NPCRI = (RED - BLUE) / (RED + BLUE)
    """
    npcri = image.normalizedDifference(['B4', 'B2']).rename('NPCRI')
    return npcri


def calculatePSRI_S2(image: ee.Image):
    """ A function to calculate the *Plant Senescence Reflectance Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        PSRI = (RED - BLUE) / REDEDGE
    """
    psri = image.expression("(RED-BLUE)/REDGE", {"RED": image.select('B4'),
                                                 "BLUE": image.select('B2'),
                                                 "REDGE": image.select('B6')})
    psri = psri.rename('PSRI')
    return psri


def calculateBSI_S2(image: ee.Image):
    """ A function to calculate the *Bare Soil Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function. \n
        BSI = ((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))
    """
    bsi = image.expression("((SWIR+RED)-(NIR+BLUE))/((SWIR+RED)+(NIR+BLUE))", {"RED": image.select('B4'),
                                                                               "BLUE": image.select('B2'),
                                                                               "NIR": image.select('B8'),
                                                                               "SWIR": image.select('B11')})
    bsi = bsi.rename('BSI')
    return bsi


# noinspection PyUnresolvedReferences
def calculateNDWI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Water Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDWI = (NIR - GREEN) / (NIR + GREEN)
    """
    ndwi = image.normalizedDifference(['B8', 'B3']).rename('NDWI')
    return ndwi


# noinspection PyUnresolvedReferences
def calculateNDMI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Moisture Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDMI = (NIR - SWIR) / (NIR + SWIR)
    """
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
    return ndmi


# noinspection PyUnresolvedReferences
def calculateNDGI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Glacier Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDGI = (RED - GREEN) / (RED - GREEN)
    """
    ndgi = image.normalizedDifference(['B3', 'B4']).rename('NDGI')
    return ndgi


# noinspection PyUnresolvedReferences
def calculateNDSI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Difference Snow Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDSI = (GREEN - SWIR) / (GREEN - SWIR)
    """
    ndsi = image.normalizedDifference(['B3', 'B11']).rename('NDSI')
    return ndsi


# noinspection PyUnresolvedReferences
def calculateNBRI_S2(image: ee.Image):
    """ A function to calculate the *Normalized Burn Ratio Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NBRI = (NIR - SWIR) / (NIR - SWIR)
    """
    nbri = image.normalizedDifference(['B8', 'B12']).rename('NBRI')
    return nbri


def calculateSI_S2(image: ee.Image):
    """ A function to calculate the *Shadow Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function.\n
        SI = ((1 - RED) * (1 - GREEN) * (1 -BLUE)) ** (1/3)
    """
    si = image.expression("(1-RED)*(1-BLUE)*(1-GREEN)", {"RED": image.select('B4'),
                                                         "GREEN": image.select('B3'),
                                                         "BLUE": image.select('B2')})
    si = si.cbrt().rename('SI')
    return si


def calculateMCARI_S2(image: ee.Image):
    """ A function to calculate the *Modified Chlorophyll Absorption Reflectance Index*
    for Sentinel-2 MSI Acquisitions. \n
    Calculated using an expression function.\n
        MCARI = ((REDEDGE - RED) - (0.2 * (REDEDGE - GREEN))) * (REDEDGE / RED)
    """
    mcari = image.expression("((REDGE-RED)-(0.2*(REDGE-GREEN)))*(REDGE/RED)", {"REDGE": image.select('B5'),
                                                                               "RED": image.select('B4'),
                                                                               "GREEN": image.select('B3')})
    mcari = mcari.rename('MCARI')
    return mcari


# noinspection PyUnresolvedReferences
def calculateNDVI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Difference Vegetation Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDVI = (NIR - RED) / (NIR + RED)
    """
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
    return ndvi


def calculateSAVI_L8(image: ee.Image):
    """ A function to calculate the *Soil Adjusted Vegetation Index*
    for Landsat OLI Acquisitions. \n
    Calculated using an expression function. \n
        SAVI = ((NIR - RED) / (NIR + RED + SCF)) * (1 + SBCF)
    *SBCF: Soil Brightness Correction Factor* = ``0.428``
    """
    savi = image.expression("((NIR-RED)/(NIR+RED+SBCF))*(1+SBCF)", {"NIR": image.select('B5'),
                                                                    "RED": image.select('B4'),
                                                                    "SBCF": 0.428})
    savi = savi.rename('SAVI')
    return savi


def calculateAVI_L8(image: ee.Image):
    """ A function to calculate the *Advanced Vegetation Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using an expression function. \n
        AVI = (NIR * (1 - RED) * (NIR - RED)) ** (1/3)
    """
    avi = image.expression("(NIR*(1-RED)*(NIR-RED))", {"NIR": image.select('B5'),
                                                       "RED": image.select('B4')})
    avi = avi.cbrt().rename('AVI')
    return avi


def calculateEVI_L8(image: ee.Image):
    """ A function to calculate the *Enhanced Vegetation Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using an expression function. \n
        EVI = 2.5 * (NIR - RED) / (NIR + (6 * RED) - (7.5 * BLUE) + 1)
    """
    evi = image.expression("(2.5*(NIR-RED))/(NIR+(6*RED)-(7.5*BLUE)+1)", {"NIR": image.select('B5'),
                                                                          "RED": image.select('B4'),
                                                                          "BLUE": image.select('B2')})
    evi = evi.rename('EVI')
    return evi


def calculateARVI_L8(image: ee.Image):
    """ A function to calculate the *Atmospherically Resistant Vegetation Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using an expression function. \n
        ARVI = NIR - RED - (0.106 * (RED - BLUE)) / (NIR + RED - (0.106 * (RED-BLUE)))
    """
    arvi = image.expression("(NIR-RED-(0.106*(RED-BLUE)))/(NIR+RED-(0.106*(RED-BLUE)))",
                            {"NIR": image.select('B5'),
                             "RED": image.select('B4'),
                             "BLUE": image.select('B2')})
    arvi = arvi.rename('ARVI')
    return arvi


# noinspection PyUnresolvedReferences
def calculateGNDVI_L8(image: ee.Image):
    """ A function to calculate the *Green Normalized Difference Vegetation Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        GNDVI = (NIR - GREEN) / (NIR + GREEN)
    """
    gndvi = image.normalizedDifference(['B5', 'B3']).rename('GNDVI')
    return gndvi


# noinspection PyUnresolvedReferences
def calculateNPCRI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Pigment Chlorophyll Ratio Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NPCRI = (RED - BLUE) / (RED + BLUE)
    """
    npcri = image.normalizedDifference(['B4', 'B2']).rename('NPCRI')
    return npcri


def calculateBSI_L8(image: ee.Image):
    """ A function to calculate the *Bare Soil Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using an expression function. \n
        BSI = ((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))
    """
    bsi = image.expression("((SWIR+RED)-(NIR+BLUE))/((SWIR+RED)+(NIR+BLUE))", {"RED": image.select('B4'),
                                                                               "BLUE": image.select('B2'),
                                                                               "NIR": image.select('B5'),
                                                                               "SWIR": image.select('B6')})
    bsi = bsi.rename('BSI')
    return bsi


# noinspection PyUnresolvedReferences
def calculateNDWI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Difference Water Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDWI = (NIR - GREEN) / (NIR + GREEN)
    """
    ndwi = image.normalizedDifference(['B5', 'B3']).rename('NDWI')
    return ndwi


# noinspection PyUnresolvedReferences
def calculateNDMI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Difference Moisture Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDMI = (NIR - SWIR) / (NIR + SWIR)
    """
    ndmi = image.normalizedDifference(['B5', 'B6']).rename('NDMI')
    return ndmi


# noinspection PyUnresolvedReferences
def calculateNDGI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Difference Glacier Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDGI = (RED - GREEN) / (RED - GREEN)
    """
    ndgi = image.normalizedDifference(['B3', 'B4']).rename('NDGI')
    return ndgi


# noinspection PyUnresolvedReferences
def calculateNDSI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Difference Snow Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NDSI = (GREEN - SWIR) / (GREEN - SWIR)
    """
    ndsi = image.normalizedDifference(['B3', 'B6']).rename('NDSI')
    return ndsi


# noinspection PyUnresolvedReferences
def calculateNBRI_L8(image: ee.Image):
    """ A function to calculate the *Normalized Burn Ratio Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using a normalized difference function. \n
        NBRI = (NIR - SWIR) / (NIR - SWIR)
    """
    nbri = image.normalizedDifference(['B5', 'B7']).rename('NBRI')
    return nbri


def calculateSI_L8(image: ee.Image):
    """ A function to calculate the *Shadow Index*
    for Landsat-8 OLI Acquisitions. \n
    Calculated using an expression function.\n
        SI = ((1 - RED) * (1 - GREEN) * (1 -BLUE)) ** (1/3)
    """
    si = image.expression("(1-RED)*(1-BLUE)*(1-GREEN)", {"RED": image.select('B4'),
                                                         "GREEN": image.select('B3'),
                                                         "BLUE": image.select('B2')})
    si = si.cbrt().rename('SI')
    return si


INDEX_MAP = {
    "S2": {
        "NDVI": calculateNDVI_S2,
        "SAVI": calculateSAVI_S2,
        "AVI": calculateAVI_S2,
        "EVI": calculateEVI_S2,
        "ARVI": calculateARVI_S2,
        "GNDVI": calculateGNDVI_S2,
        "NDCI": calculateNDCI_S2,
        "NPCRI": calculateNPCRI_S2,
        "PSRI": calculatePSRI_S2,
        "BSI": calculateBSI_S2,
        "NDWI": calculateNDWI_S2,
        "NDMI": calculateNDMI_S2,
        "NDGI": calculateNDGI_S2,
        "NDSI": calculateNDSI_S2,
        "NBRI": calculateNBRI_S2,
        "SI": calculateSI_S2,
        "MCARI": calculateMCARI_S2
    },
    "L8": {
        "NDVI": calculateNDVI_L8,
        "SAVI": calculateSAVI_L8,
        "AVI": calculateAVI_L8,
        "EVI": calculateEVI_L8,
        "ARVI": calculateARVI_L8,
        "GNDVI": calculateGNDVI_L8,
        "NPCRI": calculateNPCRI_L8,
        "BSI": calculateBSI_L8,
        "NDWI": calculateNDWI_L8,
        "NDMI": calculateNDMI_L8,
        "NDGI": calculateNDGI_L8,
        "NDSI": calculateNDSI_L8,
        "NBRI": calculateNBRI_L8,
        "SI": calculateSI_L8,
    }
}


def generateIndex(image: ee.Image,
                  index: str,
                  sensor: str):
    """ A function that generates an index out of an Image.

    The function generates a bandmath index from an Image based on the Index ID and Sensor ID provided.\n
    The resultant Image has it's metadata rebuilt based on the image used to perform the bandmath and only
    contains just one band named by the Index ID provided.

    Keyword Args:
        image:      The Image on which to perform bandmath and retrieve and Index Image.
        index:      The Index ID to calculate.
        sensor:     The Sensor ID of the Image.
    Returns:
        An Image that contains the Index as the only band in it.
    Raises:
        TypeError:      if parameter type check fails.
        ValueError:     if invalid parameter values are passed.
        EERuntimeError: if bandmath or rebuild runtimes fail.
        NotImplementedError:    if index is not possible for sensor.

    Examples:
        *Generating a mosaic Sentinel-2 L2A Image:*
    ``>> mosCol = genMosaicCollection(imageCol=imageCol, sensor="L2A")``
    """
    if isinstance(sensor, str):
        if sensor not in CONFIG.getSensors():
            raise ValueError("Index Generation Failed @ Sensor ID check: Invalid Sensor ID")
    else:
        raise TypeError("Index Generation Failed @ type check: sensor must be a str")

    if index not in CONFIG.getSensorProducts(sensor):
        raise NotImplementedError(f"Index Generation Failed @ Index Check: {index} is not possible for {sensor}")

    if not gee.verifyImage(image=image, mode=sensor):
        raise ValueError(f"Index Generation Failed @ image must be an Image of {sensor}")

    try:
        sat = CONFIG.getSatfromSensor(sensor)
        indexImage = INDEX_MAP[sat][index](image)

    except Exception as e:
        raise apexception.EERuntimeError(f"Index Generation Failed @ Bandmath Runtime: {e}")

    try:
        # noinspection PyUnresolvedReferences
        indexImage = gee.fixMetadata(image=indexImage, sensor=sensor, aqDate=Date(image.date()), precision="float")
        return indexImage

    except Exception as e:
        raise apexception.EERuntimeError(f"Index Generation Failed @ Rebuild Runtime: {e}")


def generateIndexMasks():
    """
    def genNDVIMasks(image):
    """""" 
    Generates a masked ee.ImageCollection that contains individual images.
    Each containing the pixel values between the following values [-1, 0.25, 0.33, 0.4, 0.5, 1]

    Args:
        image:  (ee.Image) The image to generate masks for
    Returns:
        ee.ImageCollection
    """"""
        if not isinstance(image, ee.Image):
            print("The image must be an ee.Image")
            return

        values = [-1, 0.25, 0.33, 0.4, 0.5, 1]
        maskedImgCol = genRangeMasks(image, values)
        return maskedImgCol
    """
    # TODO: Implement Index Masks
    raise NotImplementedError("Method Not Available!")
