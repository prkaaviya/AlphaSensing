"""
Version: v0.4.0

The apGIS package is library of modules that represents the primary codebase
for all GIS Applications and Containers that run on the AntPod platform.
It contains modules for Cloud interfaces, JSON I/O, Geocoding apart from the
primary Earth Engine API library.

Author: AntPod Designs Pvt Ltd.
"""
import ee

import apgis.apjsonio as jsonio
import apgis.apconversion as conversion
import apgis.apexception as apexception

import apgis.geebase as gee
import apgis.geespatial as spatial
import apgis.geetemporal as temporal
import apgis.geeindex as index
import apgis.geemask as mask
from apgis.geeexport import Export

from apgis.apcloud import FirebaseStorage
from apgis.apconfig import Config
from apgis.apdate import Date
from apgis.apfield import Field
from apgis.apgeojson import GeoJSON
from apgis.aprequestlist import RequestList


def eeInitialize(internalConfig: bool = False) -> None:
    """ Authenticates Earth Engine and initializes an EE Session

    Accepts a flag internalConfig to specify whether to use the internal OAuth2 credentials
    which are stored in the following directories depending on the OS:

    * Windows - ``%User%/.config/earthengine/credentials``
    * MacOSX -  ``$HOME/.config/earthengine/credentials``
    * Linux -   ``$HOME/.config/earthengine/credentials``

    If the credentials file containing the refresh token is not found, an OAuth2 Authentication
    flow will prompt you to complete a sign up with a regular Google Earth Engine verified account
    or a GSuite Account which belongs to a group that has been authorized to use Earth Engine.

    Google Drive Exports from the Earth Engine Batch System require the internalConfig to be set
    and the exports automatically go to the account that the credentials are associated with.
    If Google Drive Exports are attempted with a Service Account Authentication, the exports
    disappear into the ether.

    The eeServiceKeys are fetched from a Firebase Storage bucket and the deleted after initialization.
    """
    if internalConfig:
        # noinspection PyBroadException
        try:
            ee.Initialize()
        except:
            ee.Authenticate()
            ee.Initialize()

    else:
        try:
            fStorage = FirebaseStorage(bucket="antpod-apgis")
            fStorage.downloadFolder(remoteFolder="ee-auth", localFolder="eeKeys")
            fStorage.closeApp()

        except Exception as e:
            raise apexception.FirebaseError(f"Earth Engine Initialisation Failed @ Firebase Pull: {e}")

        try:
            import os
            keyDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "eeKeys/ee-auth")

            serviceAccountID = jsonio.jsonRead(os.path.join(keyDir, "eeserviceacc.json"))['eeServiceAccount']
            credentials = ee.ServiceAccountCredentials(serviceAccountID, os.path.join(keyDir, "eeservicekey.json"))

            ee.Initialize(credentials=credentials)

        except Exception as e:
            raise apexception.EERuntimeError(f"Earth Engine Initialisation Failed @ EE Authentication: {e}")

        try:
            import shutil
            shutil.rmtree(os.path.join(os.path.dirname(os.path.realpath(__file__)), "eeKeys"))

        except Exception as e:
            raise EnvironmentError(f"Earth Initialisation Succeeded but cleanup failed: {e}")
