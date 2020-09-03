"""
Module for Custom Exception Library.

Library that contains simple custom Exceptions for common errors across the codebase.
Includes more specific exceptions for Earth Engine and File I/O handling.

Exceptions: EERunTimeError, JSONError, FileTypeError, GeometryError, ConfigError.

Author: AntPod Designs Pvt Ltd.
"""


class VersionError(Exception):
    """ An exception for an error that occurs when version locking fails."""
    pass


class EERuntimeError(Exception):
    """ An exception for an error that occurs during Earth Engine API calls."""
    pass


class EEEmptyCollectionError(Exception):
    """ An exception for an error that occurs during Earth Engine API calls."""
    pass


class EEExportError(Exception):
    """ An exception for an error that occurs during Earth Engine Export processes."""
    pass


class JSONError(Exception):
    """ An exception for an error that occurs during the parsing of a JSON operations."""
    pass


class GeoJSONError(Exception):
    """ An exception for an error that occurs during the parsing of a JSON and related formats."""
    pass


class FileTypeError(Exception):
    """ An exception for an error that occurs when a file is of the wrong extension."""
    pass


class GeoCodingError(Exception):
    """ An exception for an error that occurs during a geocoding process. """
    pass


class GeometryError(Exception):
    """ An exception for an error that occurs when geometry operations fail."""
    pass


class ConfigError(Exception):
    """ An exception for an error that occurs while reading Config objects."""
    pass


class DataFrameError(Exception):
    """ An exception for an error that occurs while dealing with DataFrames."""
    pass


class RasterError(Exception):
    """ An exception for an error that occurs while dealing with Rasters."""
    pass


class CRSError(Exception):
    """ An exception for an error with CRS - Coordinate Reference Systems."""
    pass


class FirebaseError(Exception):
    """ An exception for an error that occurs with Firebase sessions"""
    pass


class DriveError(Exception):
    """ An exception for an error that occurs with Google Drive sessions"""
    pass


class CloudStorageError(Exception):
    """ An exception for an error that occurs with Cloud Storage sessions"""
    pass


class FireStoreError(Exception):
    """ An exception for an error that occurs with FireStore sessions"""
    pass
