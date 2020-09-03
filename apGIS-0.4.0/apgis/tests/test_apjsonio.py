"""
Test Module for apjsonio.py

Tests all functions in module.

Author: AntPod Designs Pvt Ltd.
"""
import os
import unittest
import apgis.apjsonio as jsonio
from apgis.apexception import FileTypeError


class TestJSONIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apjsonio']
        cls.testData = cls.testReference['data']

    def test_jsonRead(self):
        # Pass Tests
        for test in self.testData['JSONfiles']:
            testJSON = jsonio.jsonRead(test['filepath'])
            self.assertEqual(testJSON['properties']['testText'], test['testText'])

        # Fails Tests: Invalid format
        for test in self.testData['NonJSON']:
            with self.assertRaises(FileTypeError):
                testJSON = jsonio.jsonRead(test)

        # Fails Tests: Missing files
        for test in self.testData['ghostJSON']:
            with self.assertRaises(FileNotFoundError):
                testJSON = jsonio.jsonRead(test)

    def test_jsonWrite(self):
        # Pass Tests
        for test in self.testData['JSONdata']:
            jsonio.jsonWrite(test['filedata'], test['filename'])
            self.assertTrue(os.path.isfile(test['filepath']))

            dataCheck = jsonio.jsonRead(test['filepath'])['properties']['testText']
            self.assertEqual(dataCheck, test['filetest'])
            os.remove(test['filepath'])

        # Fail Tests: Non dictionary data
        for test in self.testData['BadData']:
            with self.assertRaises(TypeError):
                jsonio.jsonWrite(test, "testfile")

    def test_geojsonRead(self):
        # Pass Tests
        for test in self.testData['GeoJSONfiles']:
            testGeoJSON = jsonio.geojsonRead(test['filepath'])['features'][0]['properties']
            self.assertEqual(testGeoJSON['testText'], test['testText'])

        # Fails Tests: Invalid format
        for test in self.testData['NonJSON']:
            with self.assertRaises(FileTypeError):
                testJSON = jsonio.geojsonRead(test)

        # Fails Tests: Missing files
        for test in self.testData['ghostGeoJSON']:
            with self.assertRaises(FileNotFoundError):
                testJSON = jsonio.geojsonRead(test)

    def test_geojsonWrite(self):
        # Not Implemented
        for test in self.testData['ghostGeoJSON']:
            with self.assertRaises(NotImplementedError):
                jsonio.geojsonWrite({}, test)

    def test_topojsonRead(self):
        # Not Implemented
        with self.assertRaises(NotImplementedError):
            jsonio.topojsonRead()

    def test_topojsonWrite(self):
        # Not Implemented
        with self.assertRaises(NotImplementedError):
            jsonio.topojsonWrite()


if __name__ == '__main__':
    unittest.main()
