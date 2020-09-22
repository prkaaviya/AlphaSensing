"""
Module for unit conversions and data structure transformations.

Library of top-level functions that convert units between each other
and also contain methods to convert multiple file formats.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
from typing import Union
# TODO: Integrate units library


def areaUnitConversion(area: Union[int, float],
                       convertFrom: str,
                       convertTo: str) -> float:
    """ *A function that converts area units.*

    The function accepts an area value and two strings to represent the unit to convert from
    and convert to. Values are rounded to 4 decimal places.\n
    The unit strings must be one of the following:\n
    - **SQM**:      Square Metres
    - **SQKM**:     Square Kilometres
    - **SQFT**:     Square Feet
    - **SQYARD**:   Square Yard
    - **SQMILE**:   Square Mile
    - **ACRE**:     Acres
    - **HA**:       Hectares

    Args:
        area:       An integer or float area value that needs to be calculated.
        convertFrom:    A string representing the unit of the area value.
        convertTo:      A string representing the unit to convert to.
    Returns:
        float:      A float area value in the converted unit.
    Raises:
        TypeError:      if unit string is of the wrong type.
        ValueError:     if unit strings are not in the list of supported units.
        NotImplementedError:    if unit conversion pair is not implemented in areaConversionMap.
        ArithmeticError:        if conversion arithmetic fails.

    Examples:
        Some example uses of this class are:\n
    *Converting SQKM to SQFT:*\n
    ``>> sqftArea = areaUnitConversion(area=56, convertFrom="SQKM", convertTo="SQFT")``

    *Converting SQM to SQYARD:*\n
    ``>> sqmArea = areaUnitConversion(area=8456.67, convertFrom="SQM", convertTo="SQYARD")``
    """
    areaConversionMap = {
        "SQM": {
            "SQM": 1,
            "SQKM": 0.000001,
            "SQFT": 10.76391041671,
            "SQYARD": 1.1959900463011,
            "SQMILE": 0.000000386102158,
            "ACRE": 0.00024710538146717,
            "HA": 0.0001
        },
        "SQKM": {
            "SQM": 1000000,
            "SQKM": 1,
            "SQFT": 10763910.41671,
            "SQYARD": 1195990.05,
            "SQMILE": 0.386102,
            "ACRE": 247.105,
            "HA": 100
        },
        "SQFT": {
            "SQM": None,
            "SQKM": None,
            "SQFT": 1,
            "SQYARD": None,
            "SQMILE": None,
            "ACRE": None,
            "HA": None
        },
        "SQYARD": {
            "SQM": None,
            "SQKM": None,
            "SQFT": None,
            "SQYARD": 1,
            "SQMILE": None,
            "ACRE": None,
            "HA": None
        },
        "SQMILE": {
            "SQM": None,
            "SQKM": None,
            "SQFT": None,
            "SQYARD": None,
            "SQMILE": 1,
            "ACRE": None,
            "HA": None
        },
        "ACRE": {
            "SQM": None,
            "SQKM": None,
            "SQFT": None,
            "SQYARD": None,
            "SQMILE": None,
            "ACRE": 1,
            "HA": None
        },
        "HA": {
            "SQM": None,
            "SQKM": None,
            "SQFT": None,
            "SQYARD": None,
            "SQMILE": None,
            "ACRE": None,
            "HA": 1
        }
    }
    if not isinstance(area, (float, int)):
        raise TypeError("Area Conversion Failed @ area type check: area must be float or int")

    if isinstance(convertFrom, str):
        if convertFrom not in list(areaConversionMap.keys()):
            raise ValueError(f"Area Conversion Failed @ conversion unit check: {convertFrom} is not a supported format")
    else:
        raise TypeError("Area Conversion Failed @ conversion unit check: convertFrom must be a string")

    if isinstance(convertTo, str):
        if convertTo not in list(areaConversionMap.keys()):
            raise ValueError(f"Area Conversion Failed @ conversion unit check: {convertTo} is not a supported format")
    else:
        raise TypeError("Area Conversion Failed @ conversion unit check: convertTo must be a string")

    conversion = areaConversionMap[convertFrom][convertTo]
    if conversion is None:
        raise NotImplementedError("Area Conversion Failed @ conversion value determination: "
                                  f"conversion pair {convertFrom}->{convertTo} not available")
    try:
        return float(round(conversion * area, 4))

    except Exception as e:
        raise ArithmeticError(f"Area Conversion Failed @ area unit conversion: {e}")
