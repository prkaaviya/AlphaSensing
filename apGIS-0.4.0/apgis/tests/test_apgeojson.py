"""
Test Module for apgeojson.py

Tests the class GeoJSON and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import apgis.apjsonio as jsonio
from apgis.apgeojson import GeoJSON


class TestGeoJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apgeojson']
        cls.testData = cls.testReference['data']

    def test_init_File(self):
        for test in self.testData['GeoJSONfiles']:
            geojson = GeoJSON(file=test['filepath'])
            self.assertEqual(geojson.feature, test['feature'])
            self.assertEqual(geojson.geometry, test['feature']['geometry'])
            self.assertEqual(geojson.properties, test['feature']['properties'])
            self.assertEqual(geojson.geoType, test['feature']['geometry']['type'])
            self.assertEqual(geojson.coordinates, test['coordinates'])

            self.assertEqual(geojson.rectangleBBOX, test['rectBBOX'])
            self.assertEqual(geojson.polygonBBOX, test['polyBBOX'])
            self.assertEqual(geojson.centroid, test['centroid'])

    def test_init_Dict(self):
        for test in self.testData['GeoJSONfiles']:
            geojsonDict = jsonio.geojsonRead(filename=test['filepath'])
            geojson = GeoJSON(geoDictionary=geojsonDict)
            self.assertEqual(geojson.feature, test['feature'])
            self.assertEqual(geojson.geometry, test['feature']['geometry'])
            self.assertEqual(geojson.properties, test['feature']['properties'])
            self.assertEqual(geojson.geoType, test['feature']['geometry']['type'])
            self.assertEqual(geojson.coordinates, test['coordinates'])

            self.assertEqual(geojson.rectangleBBOX, test['rectBBOX'])
            self.assertEqual(geojson.polygonBBOX, test['polyBBOX'])
            self.assertEqual(geojson.centroid, test['centroid'])


if __name__ == '__main__':
    unittest.main()
