"""
apGIS Python Package
Version: v0.4.3

The apGIS package is library of modules that represents the primary codebase
for all GIS Applications and Containers that run on the AntPod platform.
Contains modules for GCP Client library interfaces, JSON I/O, Nominatim OSM
Geocoding and most importantly the Earth Engine Python API library.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
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
    """ *Authenticates and initializes an Earth Engine session.*

    Accepts a flag internalConfig to specify whether to use the internal OAuth2 credentials.

    If internalConfig is not set, Earth Engine Service Account Keys are fetched from a Firebase
    Cloud Storage bucket and deleted upon session initialization.
    This method is recommended for all production deployments.

    If internalConfig is set, the credentials file containing the refresh token for an OAuth2
    flow is used to authenticate the Earth Engine Session. The credentials file is stored on
    one of the following paths depending on the Operating System.

    *Windows*\n
    ``%User%/.config/earthengine/credentials``\n
    *MacOS and Linux*\n
    ``$HOME/.config/earthengine/credentials``\n

    If the credentials file is not found, an OAuth2 Authentication flow will prompt you to
    complete a sign up with a Google Earth Engine verified account or a GSuite Account which
    belongs to a domain group that has been authorized to use Earth Engine.
    This method is recommended if intended for local development and testing only.
    The only exception to this recommendation is if the need arises to use the Google Drive
    Export functionality on the Earth Engine Batch system. This functionality will not work
    on a Service Account authenticated system and all exports will disappear into the ether.
    If used with the internalConfig, the Drive Exports go to the account associated with the
    OAuth2 credentials file.

    Args:
        internalConfig:     A bool that is used to determine whether or not use the internal OAuth2
                            credentials for Earth Engine.
    Raises:
        FirebaseError:      Occurs if the Firebase pull fails.
        EERuntimeError:     Occurs if the Earth Engine initialization fails.
        EnvironmentError:   Occurs if the environment cleanup fails.
    """
    if internalConfig:
        try:
            ee.Initialize()

        except ee.EEException:
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
