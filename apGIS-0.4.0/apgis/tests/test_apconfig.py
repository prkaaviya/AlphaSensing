"""
Test Module for apconfig.py

Tests the class Config and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import apgis.apjsonio as jsonio
from apgis.apconfig import Config


class TestConfigMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apconfig']
        cls.testData = cls.testReference['data']
        cls.CONFIG = Config()

    def test_getSatellites(self):
        self.assertEqual(self.CONFIG.getSatellites(), self.testData['SatIDs'])

    def test_getSensors(self):
        self.assertEqual(self.CONFIG.getSensors(), self.testData['SensorIDs'])

    def test_getSatfromSensor(self):
        # Pass Tests
        for test in self.testData['SatSensorPairs']:
            self.assertEqual(self.CONFIG.getSatfromSensor(test['Sensor']), test['Sat'])

        # Fail Test: Bad Sensor ID Test
        for test in self.testData['BadIDs']:
            with self.assertRaises(ValueError):
                self.CONFIG.getSatfromSensor(test)

    def test_getSensorProducts(self):
        # Pass Tests
        for testSensor, testCheck in self.testData['SensorProducts'].items():
            self.assertEqual(self.CONFIG.getSensorProducts(testSensor), testCheck)

        # Fail Test: Bad Sensor ID Test
        for test in self.testData['BadIDs']:
            with self.assertRaises(ValueError):
                self.CONFIG.getSensorProducts(test)

    def test_getSatRevisitTime(self):
        # Pass Tests
        for testSat, testCheck in self.testData['RevisitTime'].items():
            self.assertEqual(self.CONFIG.getSatRevisitTime(testSat), testCheck)

        # Fail Test: Bad Sat ID Test
        for test in self.testData['BadIDs']:
            with self.assertRaises(ValueError):
                self.CONFIG.getSatRevisitTime(test)

    def test_getGEECollection(self):
        # Pass Tests
        for testSensor, testCheck in self.testData['GEECollections'].items():
            self.assertEqual(self.CONFIG.getGEECollection(testSensor), testCheck)

        # Fail Test: Bad Sensor ID Test
        for test in self.testData['BadIDs']:
            with self.assertRaises(ValueError):
                self.CONFIG.getGEECollection(test)


if __name__ == '__main__':
    unittest.main()
