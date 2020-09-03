"""
Test Module for geebase.py

Tests the module geebase and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import ee
import unittest
import warnings

import apgis
import apgis.geebase as gee
from apgis import apjsonio as jsonio
from apgis.apdate import Date
from apgis.apconfig import Config

CONFIG = Config()


class TestGeebase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")["testData"]['geebase']["data"]
        cls.testData = cls.testReference["setup"]

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

    def test_verifyImage(self):
        # Pass Tests
        for test in self.Tests:
            self.assertTrue(gee.verifyImage(image=test['image'], mode=test['sensor']))
            self.assertTrue(gee.verifyImage(image=test['image'], mode=test['sat']))

        # Fail Tests - Invalid Mode
        modes = self.testReference["Invalid Mode"]
        for mode, test in zip(modes, self.Tests):
            with self.assertRaises(ValueError):
                exist = gee.verifyImage(image=test['image'], mode=mode)

    def test_verifyCollection(self):
        # Pass Tests
        for test in self.Tests:
            self.assertTrue(gee.verifyCollection(imageCol=test['collection'], mode=test['sensor']))
            self.assertTrue(gee.verifyCollection(imageCol=test['collection'], mode=test['sat']))

        # Fail Tests - Invalid Mode
        modes = self.testReference["Invalid Mode"]
        for mode, test in zip(modes, self.Tests):
            with self.assertRaises(ValueError):
                exist = gee.verifyCollection(imageCol=test['collection'], mode=mode)

    def test_geeCollection(self):
        """ Tested in class setup"""
        pass

    # noinspection PyTypeChecker
    def test_extractImage(self):
        # Pass Tests
        for test in self.Tests:
            # Index Tests
            indexTest = test['testdata']['indexTest']

            self.assertEqual(gee.extractImage(imageCol=test['collection'],
                                              index=indexTest[0]).get('system:id').getInfo(), indexTest[1])
            # Date Tests
            dateTest = test['testdata']['dateTest']
            if not dateTest:
                continue

            exDate = Date(dateTest['date'])
            dateList = gee.extractImage(imageCol=test['collection'], date=exDate)

            for image, pid in zip(dateList, dateTest['pids']):
                self.assertEqual(image.get('system:id').getInfo(), pid)

    # noinspection PyTypeChecker
    def test_generateMosaicImage(self):
        for test in self.Tests:
            mosTest = test['testdata']['mosImage']
            if not mosTest:
                continue

            mosDate = Date(mosTest['date'])
            image = gee.generateMosaicImage(imageCol=test['collection'], sensor=test['sensor'], date=mosDate)

            self.assertEqual(image.get(mosTest['idProp']).getInfo(), mosTest['idString'])
            self.assertEqual(image.date().getInfo(), mosTest['eeDate'])

    # noinspection PyTypeChecker
    def test_generateMosaicCollection(self):
        for test in self.Tests:
            mosTest = test['testdata']['mosCol']
            if not mosTest:
                continue

            mosaicCol, dateList, count = gee.generateMosaicCollection(imageCol=test['collection'],
                                                                      sensor=test['sensor'])
            self.assertIsInstance(mosaicCol, ee.ImageCollection)
            self.assertTrue(gee.verifyCollection(imageCol=mosaicCol, mode=test['sensor']))


if __name__ == '__main__':
    unittest.main()
