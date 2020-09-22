"""
Class module that implements the class *Field*.

The Field class creates an object that takes a GeoJSON object and creates a
user centric object that represent a farm or field.
Contains a GeoJSON dictionary and relevant attributes for handling exports
and additionally contains geocoding information like address data.
Also contains methods to extract common geographic transformations in
local and Earth Engine formats.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import os
import pathlib
import typing
pathString = typing.Union[str, pathlib.Path]

import apgis.apjsonio as jsonio
import apgis.apexception as apexception

from apgis.apcloud import FirebaseStorage
from apgis.apgeojson import GeoJSON
from apgis.apconfig import Config

CONFIG = Config()

from geopy.geocoders import Nominatim


class Field:
    """
    *Class for Field object that represents a farm/field.*

    **Class Attributes:**\n
    - ``geojson:``      A GeoJSON object.

    - ``feature:``      A dictionary that holds the feature and its properties from the GeoJSON.
    - ``geometry:``     A dictionary that holds the geometry field data.
    - ``geoType:``      A string representing the type of Geometry.
    - ``coordinates:``      A list of coordinates that represent the geometry of the farm.

    - ``collectionProperties:``     A dictionary of properties of the FeatureCollection.
    - ``featureProperties:``        A dictionary of properties within the singular feature attribute.

    - ``userData:``     A dictionary that contains the userData field of the GeoJSON.
    - ``apfieldID:``        A string that represents the internal field ID reference.
    - ``geography:``        A dictionary of geographic properties for the field.
    - ``request``       A dictionary of request parameters that are attached to a farm.

    - ``centroid:``     A list that contains the coordinates of the geometry centroid.
    - ``AOI:``      A list of coordinates for the absolute bounds of the field.
    - ``ROI:``      A list of coordinates for the polygon bounding box of the field.
    - ``ROIBox:``       A list of coordinates for the rectangular bounding box of the field.

    - ``eeROI:``        An ee.Geometry for the bounding box of the field.
    - ``eeAOI:``        An ee.Geometry for the absolute bounds of the field.

    - ``geocode:``      A dictionary that contains the address field of the Nominatim geocode lookup.

    The Field class creates an object that takes a GeoJSON object and creates a user
    administrative object that represent a farm or field.
    Contains a GeoJSON dictionary and relevant attributes for handling exports
    and additionally contains geocoding information like address data.
    Also contains methods to extract common geographic transformations in
    local and Earth Engine formats to retrieve Earth Engine Geometry objects of its AoI and RoI.
    Geocoding is obtained from the Nominatim OSM Database.

    Only allows GeoJSONs that contain not more than one feature.

    Accepts a local filename, a remote filename or a GeoJSON object.
    If remote filename, Pulls a remote resource from a cloud bucket of test/sample GeoJSON
    files and instantiates it as a GeoJSON object and uses it to construct the Field object.
    The resource is then removed.\n
    If local filename, file is read and parsed as a GeoJSON object and uses it to construct the Field object.\n
    If GeoJSON, uses it to construct the Field object.

    References:
         Some references to related topics:\n
    *Nominatim Open-Source Geocoding:*\n
    https://nominatim.org/

    *Refer to the AntPod UserToken and AuthToken Documentation.*\n
    Documentation unavailable at this moment. Currently under development as of version 0.3.0.
    """

    def __init__(self, geojson: GeoJSON = None,
                 remotefile: str = None,
                 localfile: pathString = None,
                 *args, **kwargs):
        """ **Constructor Method**\n
        Yields a ``Field`` object.

        Creates an administrative object from a GeoJSON object and geocodes the geometry
        with address information. Also holds some additional information relevant to the
        field geometry, its bounding box and so on.\n
        Yields a *Field* object.

        Precedence of parameter acceptance:
            GeoJSON object > local GeoJSON file > remote GeoJSON file.

        Args:
            geojson:        A GeoJSON object from which to build the Resource object.
            remotefile:     A GeoJSON file that exists remotely in the sample-fields
                            folder of the antpod-apgis bucket.
            localfile:      A GeoJSON file that exists locally.
        Raises:
            TypeError:      Occurs if the geojson is not a GeoJSON object
            ValueError:     Occurs if the antpod field is None.
            GeoJSONError:   Occurs if the attribute generation fails
            GeoCodingError: Occurs if geocoding api call fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising a Field object with a GeoJSON:*\n
        ``>> GEO = GeoJSON(file="sample.geojson")``\n
        ``>> field = Field(geojson=GEO)``

        *Initialising a Field object with a local file:*\n
        ``>> field = Field(localfile="sample.geojson")``

        *Initialising a Field object with a remote file:*\n
        ``>> field = Field(remotefile="remote.geojson")``

        Notes:
            Use Field.showRemotes() to see a list of available remote resources.
        """
        try:
            geojsonObj = None

            if geojson:
                if not isinstance(geojson, GeoJSON):
                    raise TypeError("@ GeoJSON type check: geojson must be a GeoJSON object")

                geojsonObj = geojson

            elif localfile:
                if not os.path.isfile(localfile):
                    raise FileNotFoundError(f"@ Local File Read: {localfile} not found")

                geojsonObj = GeoJSON(geoDictionary=jsonio.geojsonRead(localfile))

            elif remotefile:
                if not isinstance(remotefile, str):
                    raise TypeError(f"@ Remote File Read: {remotefile} must be a string")

                geojsonObj = self.__getRemoteFile__(remotefile=remotefile)

            else:
                raise RuntimeError

            self.__generateAttributes__(geojsonObj=geojsonObj)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Field Construction Failed {e}")
        except apexception.FirebaseError as e:
            raise apexception.FirebaseError(f"Field Construction Failed @ Firebase pull: {e}")
        except apexception.FieldError as e:
            raise apexception.FieldError(f"Field Construction Failed {e}")
        except RuntimeError:
            raise apexception.FieldError(f"Field Construction Failed @ Construction: No valid keyword args passed")
        except Exception as e:
            raise apexception.FieldError(f"Field Construction Failed @ Construction : {e}")

    def __generateAttributes__(self, geojsonObj):
        try:
            self.geojson = geojsonObj

            if self.geojson.featureCount != 1:
                raise apexception.FieldError("Too many or Null features")

            self.feature = self.geojson.features[0]
            self.geometry = self.feature['geometry']

            self.geoType = self.geometry['type']
            if self.geoType not in ["Point", "Polygon"]:
                raise apexception.FieldError("Not a Point or Polygon Geometry")

            self.coordinates = self.geometry['coordinates']
            if self.geoType == 'Polygon':
                self.coordinates = self.coordinates[0]

            self.featureProperties = self.feature['properties']

            self.collectionProperties = self.geojson.properties
            if not self.collectionProperties:
                raise apexception.FieldError("Empty Collection Properties")

            self.userData = self.collectionProperties.get('userData')
            if not self.userData:
                raise apexception.FieldError("Empty userData field")

            self.apfieldID = self.userData.get('apFieldID')
            if not self.apfieldID:
                raise apexception.FieldError("No apFieldID")

            self.geography = self.collectionProperties.get('geography')
            self.geography = self.geography if self.geography != {} else None

            self.request = self.collectionProperties.get('request')
            self.request = self.request if self.request != {} else None

        except apexception.FieldError as e:
            raise apexception.FieldError(f"@ Attribute Validation: {e}")
        except Exception as e:
            raise apexception.FieldError(f"@ Attribute Generation: {e}")

    @classmethod
    def __getRemoteFile__(cls, remotefile: str = None):
        try:
            if remotefile not in CONFIG.configData['remoteResources']['sample-fields']:
                raise FileNotFoundError(f"@ Remote File Read: {remotefile} does not exist remotely"
                                        f" or {remotefile} is not available to be remotely pulled")

            resource = os.path.join(os.path.dirname(os.path.realpath(__file__)), remotefile)

            try:
                fStorage = FirebaseStorage(bucket="antpod-apgis")
                fStorage.downloadBlob(remoteName=f"sample-fields/{remotefile}", localName=resource)
                fStorage.closeApp()

            except Exception as e:
                raise apexception.FirebaseError(e)

            if not os.path.isfile(resource):
                raise FileNotFoundError(f"@ Remote File Read: {remotefile} download failed")

            geojsonData = jsonio.geojsonRead(resource)
            geojsonObj = GeoJSON(geoDictionary=geojsonData)

            os.remove(resource)

            return geojsonObj

        except apexception.FirebaseError as e:
            raise apexception.FirebaseError(e)
        except FileNotFoundError as e:
            raise FileNotFoundError(e)

    @classmethod
    def showRemotes(cls):
        """ *A classmethod that returns a list of available remote resources from the internal configuration.* """
        for i, resource in enumerate(CONFIG.configData['remoteResources']['sample-fields'], start=1):
            print(f"{i}.{resource}")

    @property
    def centroid(self):
        """ Centroid of the Field Geometry.\n
        *[Longitude, Latitude]*. """
        if self.geoType == 'Point':
            return self.coordinates

        box = self.ROIBox

        longitude = round((box[0] + box[2]) / 2, 7)
        latitude = round((box[1] + box[3]) / 2, 7)

        return [longitude, latitude]

    @property
    def AOI(self):
        """ Absolute Bounds of the Field Geometry. """
        return self.coordinates

    @property
    def ROIBox(self):
        """ Rectangular Bounding Box of the Field Geometry.\n
        *[minLongitude, minLatitude, maxLongitude, maxLatitude].* """
        if self.geoType == 'Point':
            return None

        longitudes, latitudes = [], []
        for coordinate in self.coordinates:
            x, y = coordinate
            longitudes.append(x)
            latitudes.append(y)

        return [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]

    @property
    def ROI(self):
        """ Polygon Bounding Box of the Field Geometry.\n
        *[[BottomLeftCorner], [TopLeftCorner], [TopRightCorner], [BottomRightCorner]].* """
        if self.geoType == 'Point':
            return None

        box = self.ROIBox
        blCorner = [box[0], box[1]]
        tlCorner = [box[0], box[3]]
        trCorner = [box[2], box[3]]
        brCorner = [box[2], box[1]]

        return [blCorner, tlCorner, trCorner, brCorner]

    @property
    def eeROI(self, buffer: int = None):
        """ Earth Engine Geometry object representing the bounding box geometry.\n
        Option to apply a buffer in metres. 100m for Point Geometries if not specified."""
        import ee

        try:
            if self.geoType == "Polygon":
                roi = (ee.Geometry.Polygon(self.ROI)
                       if (not buffer) else
                       ee.Geometry.Polygon(self.ROI).buffer(buffer))
                return roi

            if self.geoType == "Point":
                roi = (ee.Geometry.Point(self.AOI).buffer(100)
                       if (not buffer) else
                       ee.Geometry.Point(self.AOI).buffer(buffer))
                return roi

        except Exception as e:
            raise apexception.EERuntimeError(f"Earth Engine ROI Generation Failed: {e}")

    @property
    def eeAOI(self):
        """ Earth Engine Geometry object representing the absolute bounds geometry. """
        import ee

        try:
            aoi = (ee.Geometry.Polygon(self.AOI)
                   if (self.geoType == "Polygon") else
                   ee.Geometry.Point(self.AOI))
            return aoi

        except Exception as e:
            raise apexception.EERuntimeError(f"Earth Engine AOI Generation Failed: {e}")

    @property
    def geoCode(self):
        """ Nominatim Geocoding Information. Returns the address field of the reverse GeoCode lookup. """
        try:
            geoCoder = Nominatim(user_agent="antpodGIS-FieldGeoCoder")
            centroid = str(self.centroid[::-1])[1:-2]
            geocode = geoCoder.reverse(centroid).raw
            return geocode['address']

        except Exception as e:
            raise apexception.GeoCodingError(f"GeoCoding lookup failed: {e}")
