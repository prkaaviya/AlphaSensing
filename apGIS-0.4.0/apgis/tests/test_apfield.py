"""
Test Module for apgeojson.py

Tests the class GeoJSON and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import warnings
import apgis
import apgis.apjsonio as jsonio
from apgis.apgeojson import GeoJSON
from apgis.apfield import Field


class TestField(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReferenceField = jsonio.jsonRead("testdata/testdata.json")['testData']['apfield']
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apgeojson']
        cls.testData = cls.testReference['data']

    def test_init(self):
        for test in self.testData['GeoJSONfiles']:
            testGeo = GeoJSON(file=test['filepath'])
            testField = Field(geojson=testGeo)

            self.assertEqual(testField.apfield, test['apfield'])
            self.assertEqual(testField.geometry, test['feature']['geometry'])
            self.assertEqual(testField.geoType, test['feature']['geometry']['type'])
            self.assertEqual(testField.centroid, test['centroid'])

            self.assertEqual(testField.aoi, test['coordinates'])
            self.assertEqual(testField.roi, test['polyBBOX'])
            self.assertEqual(testField.roibox, test['rectBBOX'])

            self.assertEqual(testField.address, test['address'])

            warnings.filterwarnings("ignore", category=DeprecationWarning)
            apgis.eeInitialize()

            self.assertEqual(testField.eeROI.getInfo(), test['eeROI'])
            self.assertEqual(testField.eeAOI.getInfo(), test['eeAOI'])


if __name__ == '__main__':
    unittest.main()
