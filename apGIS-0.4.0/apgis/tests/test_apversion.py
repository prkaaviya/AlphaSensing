"""
Test Module for apversion.py

Tests the class Version and its methods.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import apgis.apjsonio as jsonio
from apgis.apexception import VersionError
import apgis.apversion as version


class TestVersion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']['apversion']
        cls.testData = cls.testReference['data']

    def test_init(self):
        # Pass Tests
        for test in self.testData['VersionTags']:
            testVersion = version.Version(test['tag'])

            self.assertEqual(testVersion.major, test['major'])
            self.assertEqual(testVersion.minor, test['minor'])
            self.assertEqual(testVersion.patch, test['patch'])
            self.assertEqual(testVersion.channel, test['channel'])
            self.assertEqual(testVersion.version, test['numericVersion'])
            self.assertEqual(testVersion.fullVersion, test['fullVersion'])

        # Fail Tests: Bad Version Tags
        for test in self.testData['BadVersionTags']:
            with self.assertRaises(VersionError):
                testVersion = version.Version(test)

    def test_eq(self):
        testTags = self.testData['VersionTags']

        # Check for Equality
        for test in testTags:
            testVersionFirst = version.Version(test['tag'])
            testVersionSecond = version.Version(test['tag'])
            self.assertEqual(testVersionFirst, testVersionSecond)

        # Check for Inequality
        for test1, test2 in zip(testTags, testTags[1:]):
            testVersionFirst = version.Version(test1['tag'])
            testVersionSecond = version.Version(test2['tag'])
            self.assertNotEqual(testVersionFirst, testVersionSecond)

    def test_repr(self):
        for test in self.testData['VersionTags']:
            testVersion = version.Version(test['tag'])
            self.assertEqual(testVersion.fullVersion, test['fullVersion'])

    def test_getVersionLock(self):
        self.assertEqual(version.getVersionLock(), version.Version(self.testReference['version']))

    def test_getInitVersion(self):
        self.assertEqual(version.getInitVersion(), version.Version(self.testReference['version']))

    def test_getConfigVersion(self):
        self.assertEqual(version.getConfigVersion(), version.Version(self.testReference['version']))


if __name__ == '__main__':
    unittest.main()
