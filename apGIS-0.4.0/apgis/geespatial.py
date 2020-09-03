"""
Module for geospatial manipulation functions.

Library of top-level functions to manipulate geospatial data on Earth Engine.

Methods: getArea.

Author: AntPod Designs Pvt Ltd.
"""
import ee

import apgis.apexception as apexception
import apgis.apconversion as conversion


def getArea(geometry: ee.Geometry,
            unit: str = "SQM"):
    """ A function that calculates the area of an ee.Geometry.

    The function calculates area with a 5% error margin.
    Area is calculated in unit of choice. Defaults to SQM.\n
    Options for units are:
        - Square Kilometres - "SQKM".
        - Square Metres - "SQM".
        - Square Feet - "SQFT".
        - Square Yards - "SQYARD".
        - Square Miles - "SQMILE".
        - Hectares - "HA".
        - Acres - "ACRE".

    Args:
        geometry:       The geometry for which to find area.
        unit:           The unit in which to calculate area. Defaults to sq.KM.
    Returns:
        The area of the geometry as a float.
    Raises:
        TypeError:      if geometry is not a ee.Geometry.
        ValueError      if unit is not valid.
        EERuntimeError: if area retrieval runtime fails.

    Examples:
        *Calculating area in Square Metres:*
    ``>> area = getArea(geometry=geo)``

        *Calculating area in Hectares:*
    ``>> area = getArea(geometry=geo, unit="HA")``
    """
    units = ["SQKM", "SQM", "SQFT", "SQMILE", "SQYARD", "HA", "ACRE"]

    if not isinstance(geometry, ee.Geometry):
        raise TypeError("Area Calculation Failed @ type check: geometry must be an ee.Geometry")

    if unit not in units:
        raise ValueError(f"Area Calculation Failed @ unit check: {unit} not supported")

    try:
        Area = geometry.area(5).getInfo()
        Area = conversion.areaUnitConversion(Area, convertFrom="SQM", convertTo=unit)
        Area = round(Area, 3)

        return Area

    except Exception as e:
        raise apexception.EERuntimeError(f"Area Calculation Failed @ Runtime: {e}")
