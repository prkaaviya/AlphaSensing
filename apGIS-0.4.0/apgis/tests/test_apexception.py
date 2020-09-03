"""
Test Module for apexception.py

Tests all custom Exceptions.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
from apgis.apexception import *


class TestException(unittest.TestCase):
    def test_VersionError(self):
        with self.assertRaises(VersionError):
            raise VersionError

    def test_EERuntimeError(self):
        with self.assertRaises(EERuntimeError):
            raise EERuntimeError

    def test_EEEmptyCollectionError(self):
        with self.assertRaises(EEEmptyCollectionError):
            raise EEEmptyCollectionError

    def test_EEExportError(self):
        with self.assertRaises(EEExportError):
            raise EEExportError

    def test_JSONError(self):
        with self.assertRaises(JSONError):
            raise JSONError

    def test_GeoJSONError(self):
        with self.assertRaises(GeoJSONError):
            raise GeoJSONError

    def test_GeoCodingError(self):
        with self.assertRaises(GeoCodingError):
            raise GeoCodingError

    def test_FileTypeError(self):
        with self.assertRaises(FileTypeError):
            raise FileTypeError

    def test_GeometryError(self):
        with self.assertRaises(GeometryError):
            raise GeometryError

    def test_ConfigError(self):
        with self.assertRaises(ConfigError):
            raise ConfigError

    def test_DataFrameError(self):
        with self.assertRaises(DataFrameError):
            raise DataFrameError

    def test_CRSError(self):
        with self.assertRaises(CRSError):
            raise CRSError

    def test_FirebaseError(self):
        with self.assertRaises(FirebaseError):
            raise FirebaseError

    def test_DriveError(self):
        with self.assertRaises(DriveError):
            raise DriveError

    def test_CloudStorageError(self):
        with self.assertRaises(CloudStorageError):
            raise CloudStorageError

    def test_FireStoreError(self):
        with self.assertRaises(FireStoreError):
            raise FireStoreError


if __name__ == '__main__':
    unittest.main()
