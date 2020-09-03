"""
Class module that implements the class **GeoJSON**.

The GeoJSON class reads and parses a GeoJSON file or dictionary into an object that
holds all its properties and geometry data. Additionally contains property methods
for common geometric attributes like bounding box and centroid.

Author: AntPod Designs Pvt Ltd.
"""
import pathlib

import apgis.apexception as apexception
import apgis.apjsonio as jsonio

import typing
pathString = typing.Union[str, pathlib.Path]


class GeoJSON:
    """
    Class for GeoJSON object to wrap its geometry and attributes.

    The GeoJSON class reads parses a GeoJSON file or dictionary into an object that
    holds all its properties and geometry data. Additionally contains property methods
    for common geometric attributes like bounding box and centroid.

    Accepts either a GeoJSON filepath or a dictionary that contains the GeoJSON data.
    The dictionary must comply with the RFC 7496 GeoJSON Format Convention(See References)
    and is validated before being parsed.

    GeoJSON cannot contain multiple features and only supports Polygon and Point Geometry.
    The Antpod GIS Platform does not support multiple features and other geometry types as of v0.3.0.

    Class Attributes:
        - ``geojson:``      A dictionary that holds the entire parsed GeoJSON data.
        - ``feature:``      A dictionary that holds the entire first (and only) feature data.
        - ``properties:``   A dictionary that holds the property field of the first (and only) feature.
        - ``antpod:``       A dictionary that holds the 'antpod' property field. None if GeoJSON doesnt have it.
        - ``request:``      A dictionary that holds the 'request' property field. None if GeoJSON doesnt have it.

        - ``geometry:``     A dictionary that holds the geometry field data
        - ``geoType:``      A string that represents the type of geometry. Point or Polygon
        - ``coordinates:``  A list that contains the coordinates of the geometry.

        - ``rectangleBBOX:`` A list of coordinates that represent the rectangular bbox of the geometry.
        - ``polygonBBOX:``   A list of coordinates that represent the polygon bbox of the geometry.
        - ``centroid:``      A list that contains the coordinates of the geometry centroid.

    References:
        *RFC 7496 GeoJSON Format:*
    https://tools.ietf.org/html/rfc7946

        *Generate a custom GeoJSON:*
    https://geojson.io/
    """

    def __init__(self, file: pathString = None, geoDictionary: dict = None):
        """ Constructs a *GeoJSON* object.\n

        Parses and wraps a GeoJSON into an object which contains all its attributes.\n
        Accepts either a filepath to a GeoJSON file or a dictionary that contains its data.
        If file is passed, geoDict is ignored. The argument passed into the constructor
        must be compliant with the RFC 7496 GeoJSON format.\n
        Yields a *GeoJSON* object.

        Keyword Args:
            file:           The GeoJSON file from which to build the object.
            geoDictionary:  A dictionary that contains parsed GeoJSON data.
        Raises:
            TypeError:      if geoDict is not a dictionary.
            GeoJSONError:   if GeoJSON validation or construction fails.

        Examples:
            *Initialising with a GeoJSON file:*
        ``>> geojson = GeoJSON(file="sample.geojson")``

            *Initialising with a GeoJSON dictionary:*
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

            self.geojson = geojsonData
            self.feature = self.geojson['features'][0]

            self.properties = self.feature['properties']

            # Used dict.get(key) so attribute contains
            # a None object rather raising a Key Error
            self.antpod = self.properties.get('antpod')
            self.request = self.properties.get('request')

            self.geometry = self.feature['geometry']
            self.geoType = self.geometry['type']

            self.coordinates = self.geometry['coordinates']
            if self.geoType == 'Polygon':
                self.coordinates = self.coordinates[0]

        except Exception as e:
            raise apexception.GeoJSONError(f"GeoJSON Construction Failed @ Attribute Generation: {e}")

    @staticmethod
    def __validateGeoDict__(geoDict: dict):
        """gg"""
        if not isinstance(geoDict['features'], list):
            raise ValueError("features is not a list")

        if geoDict['type'] == 'FeatureCollection':
            if len(geoDict['features']) != 1:
                raise ValueError("multiple/empty features")
        else:
            raise ValueError("type is not a FeatureCollection")

        feature = geoDict['features'][0]
        if not feature['type'] == 'Feature':
            raise ValueError("type of feature is not Feature")

        if not isinstance(feature['properties'], dict):
            raise ValueError("properties is not a dictionary")

        if not isinstance(feature['geometry'], dict):
            raise ValueError("geometry is not a dictionary")

        if feature['geometry']['type'] not in ['Point', 'Polygon']:
            raise ValueError("geometry type is not Point or Polygon")

        if not isinstance(feature['geometry']['coordinates'], list):
            raise ValueError("coordinates is not a list")

    def __repr__(self):
        """ Represents a *GeoJSON* object. """
        return f"{self.coordinates}"

    def __str__(self):
        """ String representation of a *GeoJSON* object. """
        return f"GeoJSON: {self.geoType} Geometry centered at {self.centroid}"

    @property
    def rectangleBBOX(self):
        """ Rectangular Bounding Box of the Geometry.\n
        [minLongitude, minLatitude, maxLongitude, maxLatitude]. """
        if self.geoType == 'Point':
            return None

        longitudes, latitudes = [], []
        for coordinate in self.coordinates:
            x, y = coordinate
            longitudes.append(x)
            latitudes.append(y)

        return [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]

    @property
    def polygonBBOX(self):
        """ Polygon Bounding Box of the Geometry.\n
        [[BottomLeftCorner], [TopLeftCorner], [TopRightCorner], [BottomRightCorner]]. """
        if self.geoType == 'Point':
            return None

        box = self.rectangleBBOX
        blCorner = [box[0], box[1]]
        tlCorner = [box[0], box[3]]
        trCorner = [box[2], box[3]]
        brCorner = [box[2], box[1]]

        return [blCorner, tlCorner, trCorner, brCorner]

    @property
    def centroid(self):
        """ Centroid of the Geometry.\n
        [Longitude, Latitude]. """
        if self.geoType == 'Point':
            return self.coordinates

        box = self.rectangleBBOX

        longitude = round((box[0]+box[2])/2, 7)
        latitude = round((box[1]+box[3])/2, 7)
        return [longitude, latitude]
