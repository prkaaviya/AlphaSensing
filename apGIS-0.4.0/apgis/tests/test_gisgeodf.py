"""
Test Module for gisgeodf.py

Tests all functions in module.

Author: AntPod Designs Pvt Ltd.
"""
import os
import glob
import unittest
from geopandas import read_file, GeoDataFrame
from apgis.gisgeodf import *
import apgis.apjsonio as jsonio
import apgis.apexception as apexception


class TestGeoDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']
        cls.gisData = cls.testReference['gisgeodf']['data']
        cls.ioFiles = cls.testReference['apjsonio']['data']

        cls.path = cls.gisData['Common']['filepath']
        cls.df = read_file(cls.path)

    def test_createGrid(self):
        # Pass Tests
        testfile = self.gisData["Grid"]
        for test in testfile:
            inGeo = read_file(test["inpath"])
            self.assertIsInstance(inGeo, GeoDataFrame)
            gridGeo = createGrid(geoDF=inGeo, spacing=test["spacing"])
            outGeo = read_file(test["createpath"])
            self.assertTrue(gridGeo.all().equals(outGeo.all()))

        # Fail Test - Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(ValueError):
                inputdf = read_file(nonjson)
                # gridGeo = createGrid(geoDF=inputdf)

    def test_setCRS(self):
        # Pass Tests
        for crsPair in self.gisData["GoodCRS"]:
            geo = setCRS(geoDF=self.df, crsString=crsPair[0])
            self.assertEqual(geo.crs, crsPair[1])

        # Fail Test - CRS
        for crsValue in self.gisData["BadCRS"]:
            with self.assertRaises(apexception.CRSError):
                geo = setCRS(geoDF=self.df, crsString=crsValue)

        # Fail Test - Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(ValueError):
                inputdf = read_file(nonjson)
                # gridGeo = setCRS(geoDF=inputdf)

    def test_overlayGrid(self):
        # Pass Tests
        testfile = self.gisData["Grid"]
        for test in testfile:
            inGeo = read_file(test["inpath"])
            self.assertIsInstance(inGeo, GeoDataFrame)
            gridGeo = overlayGrid(geoDF=inGeo, spacing=test["spacing"])
            outGeo = read_file(test["overlaypath"])
            self.assertTrue(gridGeo.all().equals(outGeo.all()))

        # Fail Test - CRS
        for crsValue in self.gisData["BadCRS"]:
            with self.assertRaises(apexception.CRSError):
                geo = overlayGrid(geoDF=self.df, crsString=crsValue)

        # Fail Test - Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(ValueError):
                inputdf = read_file(nonjson)
                # gridGeo = overlayGrid(geoDF=inputdf)

    def test_makeGridDF(self):
        # Pass Tests
        testfile = self.gisData["Grid"]
        for test in testfile:
            gridGeo = makeGridDF(geojson=test["inpath"])
            self.assertIsInstance(gridGeo, GeoDataFrame)
            outGeo = read_file(test["makepath"])
            self.assertTrue(gridGeo.columns.equals(outGeo.columns))

        # Fail Test - CRS
        for crsValue in self.gisData["BadCRS"]:
            with self.assertRaises(apexception.DataFrameError):
                geo = makeGridDF(geojson=self.path, crsString=crsValue)

        # Fail Test - Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(apexception.FileTypeError):
                # inputdf = read_file(nonjson)
                gridGeo = makeGridDF(geojson=nonjson)

    def test_insertColumns(self):
        # Pass Tests
        testfile = self.gisData["Grid"]
        for test in testfile:
            gridGeo = makeGridDF(geojson=test["inpath"])
            self.assertIsInstance(gridGeo, GeoDataFrame)
            col = test["insertcolumns"]
            gridGeo = insertColumns(geoDF=gridGeo, columnData=col)
            outGeo = read_file(test["insertpath"])
            self.assertTrue(gridGeo.columns.equals(outGeo.columns))

        # Fail Test - Column Type
        failTestColumn = self.gisData['BadColumns']["notdict"]
        for test in failTestColumn:
            with self.assertRaises(TypeError):
                outGeo = insertColumns(self.df, test)

    def test_dropColumns(self):
        # Pass Tests
        testfile = self.gisData["Grid"]
        for test in testfile:
            thisdf = read_file(test["insertpath"])
            self.assertIsInstance(thisdf, GeoDataFrame)
            col = list(test["insertcolumns"].keys())
            gridGeo = dropColumns(geoDF=thisdf, columnList=col).columns
            outGeo = read_file(test["makepath"]).columns
            self.assertTrue(gridGeo.equals(outGeo))

        # Fail Test - Non-Existent Column
        failTestColumn = self.gisData['BadColumns']["notfound"]
        for test in failTestColumn:
            with self.assertRaises(TypeError):
                outGeo = dropColumns(self.df, test)

        # Fail Test - Column Type
        failTestNonColumn = self.gisData['BadColumns']["invalidtype"]
        for test in failTestNonColumn:
            with self.assertRaises(TypeError):
                outGeo = dropColumns(self.df, test)

    def test_exportGeoDF(self):
        # Pass Tests
        testfile = self.gisData["Export"]
        for test in testfile:
            thisdf = self.df
            exportGeoDF(geoDF=thisdf, fileName=test["filename"], fileFormat=test["type"])
            path = glob.glob(test["filename"]+'*')
            for rem in path:
                self.assertTrue(os.path.isfile(rem))
                os.remove(rem)

        # Fail Test - Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(NotImplementedError):
                nonformat = nonjson.split('.')[-1]
                outGeo = exportGeoDF(geoDF=self.df, fileName='output', fileFormat=nonformat)


if __name__ == '__main__':
    unittest.main()
