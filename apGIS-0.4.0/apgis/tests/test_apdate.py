"""
Test Module for apdate.py

Tests the class Date and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import ee
import unittest
import warnings
import apgis
import apgis.geebase as gee
import apgis.apjsonio as jsonio
from apgis.apdate import Date


class TestDate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=ResourceWarning)

        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apdate']
        cls.testData = cls.testReference['data']
        cls.testDates = cls.testData['Dates'] + cls.testData['eeDates']

        apgis.eeInitialize()

        testSetup = cls.testData['eeDates']
        cls.testImages = []
        for test in testSetup:
            for sensor in test['ee']['sensor']:
                sDate = Date(test['dateString'])
                filterDates = (sDate, sDate.nextDay())
                filterAoI = ee.Geometry.Polygon(test['ee']['aoi'])

                eeImage = gee.genCollection(sensor=sensor, geometry=filterAoI, daterange=filterDates).first()
                testImage = {
                    "sensor": sensor,
                    "image": eeImage,
                    "data": test
                }
                cls.testImages.append(testImage)

    def test_init_eeDate(self):
        # Pass Tests
        for test in self.testDates:
            eeDate = ee.Date(test['isoString'])
            testDate = Date(eeDate)

            self.assertIsInstance(testDate.eeDate, ee.Date)
            self.assertEqual(testDate.year, test['year'])
            self.assertEqual(testDate.month, test['month'])
            self.assertEqual(testDate.day, test['day'])
            self.assertEqual(testDate.dateString, test['dateString'])
            self.assertEqual(testDate.timeString, test['timeString'])
            self.assertEqual(testDate.ISOString, test['isoString'])
            self.assertEqual(testDate.epochMS, test['epochMS'])

        # Fail Tests
        for test in self.testData['BadDates']:
            with self.assertRaises(RuntimeError):
                eeDate = ee.Date(test)
                testDate = Date(eeDate)

    def test_init_eeImage(self):
        # Pass Tests
        for test in self.testImages:
            testDate = Date(test['image'])

            self.assertIsInstance(testDate.eeDate, ee.Date)
            self.assertEqual(testDate.year, test['data']['year'])
            self.assertEqual(testDate.month, test['data']['month'])
            self.assertEqual(testDate.day, test['data']['day'])
            self.assertEqual(testDate.dateString, test['data']['dateString'])
            self.assertEqual(testDate.timeString, test['data']['timeString'])
            self.assertEqual(testDate.ISOString, test['data']['isoString'])
            self.assertEqual(testDate.epochMS, test['data']['epochMS'])

    def test_init_ISOString(self):
        # Pass Tests
        for test in self.testDates:
            testDate = Date(test['isoString'])

            self.assertIsInstance(testDate.eeDate, ee.Date)
            self.assertEqual(testDate.year, test['year'])
            self.assertEqual(testDate.month, test['month'])
            self.assertEqual(testDate.day, test['day'])
            self.assertEqual(testDate.dateString, test['dateString'])
            self.assertEqual(testDate.timeString, test['timeString'])
            self.assertEqual(testDate.ISOString, test['isoString'])
            self.assertEqual(testDate.epochMS, test['epochMS'])

        # Fail Tests
        for test in self.testData['BadDates']:
            with self.assertRaises(RuntimeError):
                testDate = Date(test)

    def test_init_EpochMS(self):
        for test in self.testDates:
            testDate = Date(test['epochMS'])

            self.assertIsInstance(testDate.eeDate, ee.Date)
            self.assertEqual(testDate.year, test['year'])
            self.assertEqual(testDate.month, test['month'])
            self.assertEqual(testDate.day, test['day'])
            self.assertEqual(testDate.dateString, test['dateString'])
            self.assertEqual(testDate.timeString, test['timeString'])
            self.assertEqual(testDate.ISOString, test['isoString'])
            self.assertEqual(testDate.epochMS, test['epochMS'])

        # Fail Tests
        for test in self.testData['BadDates']:
            with self.assertRaises(RuntimeError):
                testDate = Date(test)

    def test_advanceDelta(self):
        for test in self.testDates:
            # Pass Tests: eeDate mode
            testDate = Date(ee.Date(test['isoString']))
            for deltaUnit, deltaData in test['deltas'].items():
                if deltaData[0]:
                    self.assertEqual(testDate.advanceDelta(deltaData[1], deltaUnit).ISOString, deltaData[2])

            # Pass Tests: ISOString mode
            testDate = Date(test['isoString'])
            for deltaUnit, deltaData in test['deltas'].items():
                if deltaData[0]:
                    self.assertEqual(testDate.advanceDelta(deltaData[1], deltaUnit).ISOString, deltaData[2])

            # Pass Tests: epochMS mode
            testDate = Date(test['epochMS'])
            for deltaUnit, deltaData in test['deltas'].items():
                if deltaData[0]:
                    self.assertEqual(testDate.advanceDelta(deltaData[1], deltaUnit).ISOString, deltaData[2])

        # Pass Tests: eeImage mode
        for test in self.testImages:
            testDate = Date(test['image'])
            for deltaUnit, deltaData in test['data']['deltas'].items():
                if deltaData[0]:
                    self.assertEqual(testDate.advanceDelta(deltaData[1], deltaUnit).ISOString, deltaData[2])

    def test_nextDay(self):
        for test in self.testDates:
            # Pass Tests: eeDate mode
            testDate = Date(ee.Date(test['isoString']))
            self.assertEqual(testDate.nextDay().ISOString, test['nextDay'])

            # Pass Tests: ISOString mode
            testDate = Date(test['isoString'])
            self.assertEqual(testDate.nextDay().ISOString, test['nextDay'])

            # Pass Tests: epochMS mode
            testDate = Date(test['epochMS'])
            self.assertEqual(testDate.nextDay().ISOString, test['nextDay'])

        # Pass Tests: eeImage mode
        for test in self.testImages:
            testDate = Date(test['image'])
            self.assertEqual(testDate.nextDay().ISOString, test['data']['nextDay'])


if __name__ == '__main__':
    unittest.main()
