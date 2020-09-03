"""
Test Module for geetemporal.py

Tests the module geetemporal and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import warnings
import ee

import apgis
from apgis import apjsonio as jsonio
import apgis.geetemporal as temporal
import apgis.geebase as gee

from apgis.apdate import Date
from apgis.apconfig import Config
CONFIG = Config()


class TestGeetemporal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")["testData"]
        cls.testData = cls.testReference["geebase"]["data"]["setup"]
        cls.tempData = cls.testReference["geetemporal"]["data"]

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        apgis.eeInitialize()

        cls.Tests = []
        for test in cls.testData:
            sdate, edate = Date(test['startDate']), Date(test['endDate'])
            daterange = (sdate, edate)

            if test['geoType'] == "Polygon":
                aoi = ee.Geometry.Polygon(test['aoi'])
            elif test['geoType'] == "Point":
                aoi = ee.Geometry.Point(test['aoi'])
            else:
                raise AssertionError("Invalid Test")

            for sensor in list(test['sensors'].keys()):
                col = gee.genCollection(sensor=sensor, geometry=aoi, daterange=daterange)
                image = col.first()
                testConf = {
                    "collection": col,
                    "image": image,
                    "sensor": sensor,
                    "sat": CONFIG.getSatfromSensor(sensor=sensor),
                    "daterange": daterange,
                    "testdata": test['sensors'][sensor]
                }
                cls.Tests.append(testConf)

    def test_generateDateSet2(self):
        # Pass Tests
        dateset = self.tempData["Dateset"]
        for date, test in zip(dateset, self.Tests):
            datesetImage = temporal.generateDateSet(image=test["image"], sat=test["sat"])
            self.assertTrue(datesetImage, date)

        # Fail Tests - Invalid Satellite
        nonsat = self.tempData["Invalid Sat"]
        for sat, test in zip(nonsat, self.Tests):
            with self.assertRaises(ValueError):
                dateset = temporal.generateDateSet(image=test["image"], sat=sat)

    def test_generateDateList(self):
        datelist = self.tempData["Datelist"]
        for date, test in zip(datelist, self.Tests):
            datesetCol = temporal.generateDateList(imageCol=test["collection"])
            self.assertTrue(datesetCol, date)


if __name__ == '__main__':
    unittest.main()
