"""
Class module that implements the class *GeoJSON*.

The GeoJSON class reads and parses a GeoJSON file or dictionary into an object that
holds all its properties and feature data.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import pathlib

import apgis.apexception as apexception
import apgis.apjsonio as jsonio

import typing
pathString = typing.Union[str, pathlib.Path]


class GeoJSON:
    """
    *Class for GeoJSON object to wrap its geometry and attributes.*

    **Class Attributes:**\n
    - ``geojson:``      A dictionary that holds the entire parsed GeoJSON data.
    - ``features:``     A list of dictionaries that holds all the features from the GeoJSON.
    - ``featureCount:`` An integer number of features in the features list.

    - ``properties:``   A dictionary that holds the property field of the FeatureCollection.
    - ``request:``      A dictionary that holds the request field of the FeatureCollection.

    The GeoJSON class reads parses a GeoJSON file or dictionary into an object that
    holds all its properties and feature data.

    Accepts either a GeoJSON filepath or a dictionary that contains the GeoJSON data.
    The dictionary must comply with the RFC 7496 GeoJSON Format Convention(See References)
    and is validated before being parsed.

    References:
        Some references to related topics:\n
    *RFC 7496 GeoJSON Format:*\n
    https://tools.ietf.org/html/rfc7946

    *Generate a custom GeoJSON:*\n
    https://geojson.io/
    """

    def __init__(self, file: pathString = None, geoDictionary: dict = None):
        """ **Constructor Method**\n
        Yields a ``GeoJSON`` object.

        Parses and wraps a GeoJSON into an object which contains all its attributes.\n
        Accepts either a filepath to a GeoJSON file or a dictionary that contains its data.
        If file is passed, geoDictionary is ignored. The argument passed into the constructor
        must be compliant with the RFC 7496 GeoJSON format.\n
        Yields a *GeoJSON* object.

        Args:
            file:       The GeoJSON file from which to build the object.
            geoDictionary:  A dictionary that contains parsed GeoJSON data.
        Raises:
            TypeError:      Occurs if the geoDictionary is not a dictionary.
            GeoJSONError:   Occurs if the GeoJSON validation or construction fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising with a GeoJSON file:*\n
        ``>> geojson = GeoJSON(file="sample.geojson")``

        *Initialising with a GeoJSON dictionary:*\n
        ``>> geoDict = jsonio.geojsonRead("sample.geojson")``\n
        ``>> geojson = GeoJSON(geoDictionary=geoDict)``
        """
        if file:
            geoDictionary = jsonio.geojsonRead(filename=file)

        if not isinstance(geoDictionary, dict):
            raise TypeError("GeoJSON Construction Failed @ type check: geoDictionary must be a dictionary")

        try:
            self.__validateGeoDict__(geoDictionary)

        except Exception as e:
            raise apexception.GeoJSONError(f"GeoJSON Construction Failed @ GeoJSON Validation Failed: {e}")

        try:
            geojsonData = geoDictionary

            self.geoData = geojsonData
            self.features = self.geoData['features']
            self.featureCount = len(self.features)

            self.properties = self.geoData.get('properties')
            self.request = self.geoData.get('request')

        except Exception as e:
            raise apexception.GeoJSONError(f"GeoJSON Construction Failed @ Attribute Generation: {e}")

    @staticmethod
    def __validateGeoDict__(geoDict: dict):
        """ *Validates a GeoJSON dictionary to be compliant with the RFC7496 GeoJSON standard.* """
        if geoDict['type'] != 'FeatureCollection':
            raise ValueError("type is not a FeatureCollection")

        if not isinstance(geoDict['features'], list):
            raise ValueError("features is not a list")

        if len(geoDict['features']) == 0:
            raise ValueError("empty feature list")

        for i, feature in enumerate(geoDict['features'], start=0):
            if feature['type'] != 'Feature':
                raise ValueError(f"feature {i} is not of type Feature")

            if not isinstance(feature['properties'], dict):
                raise ValueError(f"feature {i} properties are not in a dictionary")

            if not isinstance(feature['geometry'], dict):
                raise ValueError(f"feature {i} geometry are not in a dictionary")

            if not isinstance(feature['geometry']['coordinates'], list):
                raise ValueError(f"feature {i} coordinates are not in a list")

    def __repr__(self):
        """ Represents a *GeoJSON* object. """
        return f"GeoJSON Object [Feature Count: {self.featureCount}, Properties: {self.properties}]"

    def __str__(self):
        """ String representation of a *GeoJSON* object. """
        return f"{self.geoData}"
