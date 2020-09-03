"""
Test Module for geespatial.py

Tests the module geespatial and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import ee
from apgis import apjsonio as jsonio
import apgis.geespatial as spatial
import apgis
import warnings


class TestGeespatial(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")["testData"]["geespatial"]["data"]
        cls.geoTest = cls.testReference["Geometry"]
        cls.units = cls.testReference["Units"]

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        apgis.eeInitialize()

    def test_getArea(self):
        # Pass Tests
        for test in self.geoTest:
            if test['geotype'] == "Polygon":
                aoi = ee.Geometry.Polygon(test['aoi'])

                areaList = test["area"]
                for area, unit in zip(areaList, self.units):
                    self.assertTrue(spatial.getArea(geometry=aoi, unit=unit), area)

        # Fail Tests - Unit
        invalid = self.testReference["Invalid Units"]
        for test in self.geoTest:
            if test['geotype'] == "Polygon":
                aoi = ee.Geometry.Polygon(test['aoi'])
                for unit in invalid:
                    with self.assertRaises(ValueError):
                        area = spatial.getArea(geometry=aoi, unit=unit)

        # Fail Tests - Geometry
        invalidGeo = self.testReference["Invalid Geometry"]
        for test in invalidGeo:
            for unit in self.units:
                with self.assertRaises(TypeError):
                    area = spatial.getArea(geometry=test, unit=unit)


if __name__ == '__main__':
    unittest.main()
