"""
Test Module for aprequestlist.py

Tests the class RequestList and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import apgis.apjsonio as jsonio
from apgis.aprequestlist import RequestList


class TestRequestList(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['aprequestlist']
        cls.sensorProducts = jsonio.jsonRead("testdata/testdata.json")['testData']['apconfig']['data']['SensorProducts']
        cls.testData = cls.testReference['data']

    def test_init(self):
        # Pass Tests
        for test in self.testReference['init']:
            testList = RequestList(productList=test['reqList'], sensor=test['sensor'])
            self.assertEqual(testList.products, test['reqList'])
            self.assertEqual(testList.sat, test['sat'])
            self.assertEqual(testList.sensor, test['sensor'])
            self.assertEqual(testList.reqBands, test['reqBands'])
            self.assertEqual(testList.sensorProducts, self.sensorProducts[testList.sensor])

        # Fail Tests: Invalid Parameters
        for test in self.testReference['BADINIT']:
            with self.assertRaises(ValueError):
                testList = RequestList(productList=test[0], sensor=test[1])


if __name__ == '__main__':
    unittest.main()
