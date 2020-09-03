"""
Class module that implements the class **Resource**.

The Resource class creates an object that contains the essential parameters for request handling.
Contains a GeoJSON dictionary and a Field object that collectively hold all the information that
is required to be preprocessed to handle a GeoJSON request.

Author: AntPod Designs Pvt Ltd.
"""
import os
import pathlib
import apgis.apjsonio as jsonio
import apgis.apexception as apexception

from apgis.apcloud import FirebaseStorage
from apgis.apgeojson import GeoJSON
from apgis.apfield import Field
from apgis.apconfig import Config

import typing
pathString = typing.Union[str, pathlib.Path]

CONFIG = Config()


class Resource:
    """
    Class to create an object for GeoJSON related processing.

    The Resource class creates an object that contains the essential parameters for request handling.
    Contains a GeoJSON dictionary and a Field object that collectively hold all the information that
    is required to be preprocessed to handle a GeoJSON request.

    Accepts a local filename, a remote filename or a GeoJSON object.
    If remote filename, Pulls a remote resource from a cloud bucket of test/sample GeoJSON files and
    instantiates it as a GeoJSON object and as a Field object. The resource is then removed.
    If local filename, file is read and parsed as a GeoJSON object and a Field object.
    If GeoJSON is, generates a Field analog and instantiates the object.

    Class Attributes:
        - ``geojson:``      A GeoJSON object.
        - ``field:``        A Field object.

    Class Methods:
        - ``showAvailable:``      a classmethod that prints a list of available remote resources.
    """
    def __init__(self, geojson: GeoJSON = None, remotefile: str = None, localfile: pathString = None):
        """ Constructs a *Resource* object.\n

        Creates an object that holds a GeoJSON and a Field object that collectively represent the
        geometric and administrative properties of a 'resource'.\n

        Accepts a local filename, a remote filename or a GeoJSON object.
        If remote filename, Pulls a remote resource from a cloud bucket of test/sample GeoJSON files and
        instantiates it as a GeoJSON object and as a Field object. The resource is then removed.
        If local filename, file is read and parsed as a GeoJSON object and a Field object.
        If GeoJSON is, generates a Field analog and instantiates the object.\n
        Yields a *Resource* object.

        Precedence of parameter acceptance:
            GeoJSON object > local GeoJSON file > remote GeoJSON file.

        Keyword Args:
            geojson:        A GeoJSON object from which to build the Resource object.
            remotefile:     A GeoJSON file that exists remotely in the sample-fields
                            folder of the antpod-apgis bucket.
            localfile:      A GeoJSON file that exists locally.
        Raises:
            FileNotFoundError:  if file cannot be located.
            FirebaseError:      if Firebase subsystem fails.
            GeoJSONError:       if GeoJSON build fails.
            AttributeError:     if attribute generation fails

        Examples:
            *Initialising a Resource object with a GeoJSON:*
        ``>> GEO = GeoJSON(file="sample.geojson")``\n
        ``>> resource = Resource(geojson=GEO)``

            *Initialising a Resource object with a local file:*
        ``>> resource = Resource(localfile="sample.geojson")``

            *Initialising a Resource object with a remote file:*
        ``>> resource = Resource(remotefile="remote.geojson")``

        Notes:
            Use Resource.showAvailable() to see a list of available remote resources.
        """
        try:
            geojsonObj = None

            if geojson:
                geojsonObj = geojson

            elif localfile:
                if not os.path.isfile(localfile):
                    raise FileNotFoundError(f"@ Local File Read: {localfile} not found")
                geojsonData = jsonio.geojsonRead(localfile)
                geojsonObj = GeoJSON(geoDictionary=geojsonData)

            elif remotefile:
                if remotefile not in CONFIG.config['remoteResources']['sample-fields']:
                    raise FileNotFoundError(f"@ Remote File Read: {remotefile} does not exist remotely or "
                                            f"{remotefile} is not available to be remotely pulled")
                    
                resource = os.path.join(os.path.dirname(os.path.realpath(__file__)), remotefile)
                try:
                    fStorage = FirebaseStorage(bucket="antpod-apgis")
                    fStorage.downloadBlob(remoteName=f"sample-fields/{remotefile}", localName=resource)
                    fStorage.closeApp()

                except Exception as e:
                    raise apexception.FirebaseError(f"@ Firebase pull: {e}")

                
                if not os.path.isfile(resource):
                    raise FileNotFoundError(f"@ Remote File Read: {remotefile} download failed")

                geojsonData = jsonio.geojsonRead(resource)
                geojsonObj = GeoJSON(geoDictionary=geojsonData)

                os.remove(resource)

        except apexception.FirebaseError as e:
            raise apexception.FirebaseError(f"Resource Construction Failed {e}")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Resource Construction Failed {e}")
        except Exception as e:
            raise apexception.GeoJSONError(f"Resource Construction Failed @ GeoJSON setup: {e}")

        try:
            self.geojson = geojsonObj if remotefile else geojson
            self.field = Field(geojson=self.geojson)

        except Exception as e:
            raise AttributeError(f"Resource Construction Failed @ attribute generation: {e}")

    @classmethod
    def showAvailable(cls):
        """ A classmethod that returns a list of available remote resources from the internal configuration. """
        for i, resource in enumerate(CONFIG.config['remoteResources']['sample-fields'], start=1):
            print(f"{i}.{resource}")
