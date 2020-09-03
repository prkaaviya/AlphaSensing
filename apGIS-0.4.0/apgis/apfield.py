"""
Class module that implements the class **Field**.

The Field class creates an object that takes a GeoJSON object and creates a
user centric object that represent a farm or field. Contains the relevant attributes
for handling exports and additionally contains geocoding information like address data.

Author: AntPod Designs Pvt Ltd.
"""
from geopy.geocoders import Nominatim

from apgis.apgeojson import GeoJSON
import apgis.apexception as apexception


class Field:
    """
    Class for Field object that represents a farm/field.

    The Field class creates an object that takes a GeoJSON object and creates a user
    administrative centric object that represent a farm or field. Contains the relevant
    attributes for handling exports and additionally contains geocoding information like
    address data which includes everything from village/county data to country codes.
    Geocoding is obtained from the Nominatim OSM Database.

    Accepts a GeoJSON object and creates its geocoding information. Additionally contains
    property methods to retrieve Earth Engine Geometry objects of its AoI and RoI.

    Class Attributes:
        - ``apfield:``      A dictionary that contains the antpod field of the GeoJSON.
        - ``apfieldID:``    A string that represents the internal field ID reference.

        - ``geometry:``     A list of coordinates that represent the geometry of the farm.
        - ``geoType:``      A string representing the type of Geometry.
        - ``centroid:``     A list that contains the coordinates of the geometry centroid.

        - ``aoi:``          A list of coordinates for the absolute bounds of the field.
        - ``roi:``          A list of coordinates for the polygon bbox of the field.
        - ``roibox:``       A list of coordinates for the rectangular bbox of the field.

        - ``eeROI:``        An ee.Geometry for the bounding box of the field.
        - ``eeAOI:``        An ee.Geometry for the absolute bounds of the field.

        - ``geocode:``          A dictionary that contains the entire result of the geocode lookup.
        - ``address:``          A dictionary that contains the entire geocoded address of the field.
        - ``suburb:``           A string that represents the suburb of the field
        - ``village:``          A string that represents the village of the field
        - ``state_district:``   A string that represents the state district of the field
        - ``state:``            A string that represents the state of the field
        - ``postcode:``         A string that represents the postal code of the field
        - ``country:``          A string that represents the country of the field
        - ``country_code:``     A string that represents the country code of the field

    References:
        *Nominatim Open-Source Geocoding:*
    https://nominatim.org/

        *Refer to the AntPod UserToken and AuthToken Documentation.*
    Documentation unavailable at this moment. Currently under development as of version 0.3.0.
    """

    def __init__(self, geojson: GeoJSON):
        """ Constructs a *Field* object.\n

        Creates an administrative object from a GeoJSON object and geocodes the geometry
        with address information. Also holds some additional information relevant to the
        field geometry, its bounding box and so on.\n
        Yields a *Field* object.

        Keyword Args:
            geojson:        The GeoJSON object from which to build the Field object.
        Raises:
            TypeError:      if geojson is not a GeoJSON object
            ValueError:     if antpod field is None.
            GeoJSONError:   if attribute generation fails
            GeoCodingError: if geocoding api call fails.

        Examples:
            *Initialising a Field object:*
        ``>> GEO = GeoJSON(file="sample.geojson")``\n
        ``>> field = Field(geojson=GEO)``
        """
        if not isinstance(geojson, GeoJSON):
            raise TypeError("Field Construction Failed @ type check: geojson must be a GeoJSON object")

        self.apfield = geojson.antpod
        if not self.apfield:
            raise ValueError("Field Construction Failed @ apfield check: empty antpod field in GeoJSON")

        try:
            self.apfieldID = self.apfield.get('apFieldID')

            self.geometry = geojson.geometry
            self.geoType = geojson.geoType
            self.centroid = geojson.centroid

            self.aoi = geojson.coordinates
            self.roi = geojson.polygonBBOX
            self.roibox = geojson.rectangleBBOX

        except Exception as e:
            raise apexception.GeoJSONError(f"Field Construction Failed @ Attribute generation: {e}")

        try:
            self.__geocode__()

        except Exception as e:
            raise apexception.GeoCodingError(f"Field Construction Failed @ Geocoding: {e}")

    def __geocode__(self):
        """ gg"""
        try:
            geoCoder = Nominatim(user_agent="antpodGIS-FieldConstructor")
            centroid = str(self.centroid[::-1])[1:-2]
            self.geocode = geoCoder.reverse(centroid).raw

        except Exception as e:
            raise apexception.GeoCodingError("Geocoding lookup failed")

        try:
            self.address = self.geocode.get('address')
            self.suburb = self.address.get('suburb')
            self.village = self.address.get('village')
            self.county = self.address.get('county')
            self.state_district = self.address.get('state_district')
            self.state = self.address.get('state')
            self.postcode = self.address.get('postcode')
            self.country = self.address.get('country')
            self.country_code = self.address.get('country_code')

        except Exception as e:
            raise apexception.GeoCodingError("Geocode attribute generation failed")

    @property
    def eeROI(self, buffer: int = None):
        """ Earth Engine Geometry object representing the bounding box geometry.\n
        Option to apply a buffer in metres. 100m for Point Geometries if not specified."""
        import ee

        try:
            if self.geoType == "Polygon":
                roi = (ee.Geometry.Polygon(self.roi)
                       if (not buffer) else
                       ee.Geometry.Polygon(self.roi).buffer(buffer))
                return roi

            if self.geoType == "Point":
                roi = (ee.Geometry.Point(self.aoi).buffer(100)
                       if (not buffer) else
                       ee.Geometry.Point(self.aoi).buffer(buffer))
                return roi

        except Exception as e:
            raise apexception.EERuntimeError(f"Earth Engine ROI Generation Failed: {e}")

    @property
    def eeAOI(self):
        """ Earth Engine Geometry object representing the absolute bounds geometry. """
        import ee

        try:
            aoi = (ee.Geometry.Polygon(self.aoi)
                   if (self.geoType == "Polygon") else
                   ee.Geometry.Point(self.aoi))
            return aoi

        except Exception as e:
            raise apexception.EERuntimeError(f"Earth Engine AOI Generation Failed: {e}")
