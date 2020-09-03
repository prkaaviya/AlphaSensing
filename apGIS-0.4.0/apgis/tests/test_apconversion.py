"""
Test Module for apconversion.py

Tests all functions in module.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import apgis.apjsonio as jsonio
import apgis.apconversion as conversion


class TestConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apconversion']
        cls.testData = cls.testReference['data']

    def test_areaUnitConversion(self):
        passTests = self.testReference['areaUnitConversion']['PASS']
        failTests = self.testReference['areaUnitConversion']['FAIL']

        # Pass Tests
        for conversionPair, testList in passTests.items():
            units = conversionPair.split("-")
            for test in testList:
                testArea = conversion.areaUnitConversion(test[0], units[0], units[1])
                self.assertEqual(testArea, test[1])

        # Fail Tests: non int/float values OR non str units
        failTestTYPE = failTests['BADTYPE']
        for test in failTestTYPE:
            with self.assertRaises(TypeError):
                testArea = conversion.areaUnitConversion(test[0], test[1], test[2])

        # Fail Tests: invalid units
        failTestUNIT = failTests['BADUNIT']
        for test in failTestUNIT:
            with self.assertRaises(ValueError):
                testArea = conversion.areaUnitConversion(test[0], test[1], test[2])

        # Fail Tests: unimplemented conversion pairs
        failTestUNIT = failTests['BADPAIR']
        for test in failTestUNIT:
            with self.assertRaises(NotImplementedError):
                testArea = conversion.areaUnitConversion(test[0], test[1], test[2])


if __name__ == '__main__':
    unittest.main()
