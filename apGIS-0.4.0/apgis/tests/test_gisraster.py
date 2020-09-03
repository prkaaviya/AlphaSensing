"""
Test Module for gisraster.py

Tests all functions in module.

Author: AntPod Designs Pvt Ltd.
"""
import unittest
import rasterio
from geopandas import read_file, GeoDataFrame

from apgis.gisgeodf import makeGridDF
from apgis.gisraster import *
import apgis.apjsonio as jsonio
from numpy import ndarray
import apgis.apexception as apexception


class TestRaster(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """doc"""
        cls.testReference = jsonio.jsonRead("testdata/testdata.json")['testData']
        cls.geopath = cls.testReference['gisgeodf']['data']['Common']['filepath']
        cls.df = read_file(cls.geopath)
        cls.ioFiles = cls.testReference['apjsonio']['data']
        cls.rasData = cls.testReference['gisraster']['data']

    def test_init(self):
        # Pass Tests
        tifpath = self.rasData["tif"]
        for tif in tifpath:
            r1 = Raster(GeoTIFF=tif)
            self.assertIsInstance(r1.raster, rasterio.DatasetReader)

        # Fail Test - Nonexistent File
        ghostpath = self.rasData["ghostTif"]
        for tif in ghostpath:
            with self.assertRaises(FileNotFoundError):
                r1 = Raster(GeoTIFF=tif)

        # Fail Test - Invalid Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(apexception.FileTypeError):
                r1 = Raster(GeoTIFF=nonjson)

    def test_getWindow(self):
        # Pass Tests
        tifpath = self.rasData["tif"]
        for tif in tifpath:
            r1 = Raster(GeoTIFF=tif)
            self.assertIsInstance(r1.raster, rasterio.DatasetReader)
            window = r1.getWindow(geoDF=self.df)
            # noinspection PyUnresolvedReferences
            self.assertIsInstance(window, rasterio.windows.Window)

        # Fail Test - Nonexistent File
        ghostpath = self.rasData["ghostTif"]
        for tif in ghostpath:
            with self.assertRaises(FileNotFoundError):
                r1 = Raster(GeoTIFF=tif)
                window = r1.getWindow(geoDF=self.df)

        # Fail Test - Invalid Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(apexception.FileTypeError):
                r1 = Raster(GeoTIFF=nonjson)
                window = r1.getWindow(geoDF=self.df)

    # noinspection PyUnresolvedReferences
    def test_clip(self):
        # Pass Tests
        tifpath = self.rasData["tif"]
        indexes = self.rasData["indexint"]
        for index, tif in zip(indexes, tifpath):
            r1 = Raster(tif)
            self.assertIsInstance(r1.raster, rasterio.DatasetReader)
            clipping, window = r1.clip(geoDF=self.df, index=index)
            self.assertIsInstance(window, rasterio.windows.Window)
            self.assertIsInstance(clipping, ndarray)

        # Fail Test - Nonexistent File
        ghostpath = self.rasData["ghostTif"]
        for index, tif in zip(indexes, ghostpath):
            with self.assertRaises(FileNotFoundError):
                r1 = Raster(GeoTIFF=tif)
                self.assertIsInstance(r1.raster, rasterio.DatasetReader)
                clipping, window = r1.clip(geoDF=self.df, index=index)

        # Fail Test - Invalid Format
        for index, nonjson in zip(indexes, self.ioFiles["NonJSON"]):
            with self.assertRaises(apexception.FileTypeError):
                r1 = Raster(GeoTIFF=nonjson)
                clipping, window = r1.clip(geoDF=self.df, index=index)

    def test_assignMean(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        tifpath = self.rasData["tif"]
        outpath = self.rasData["outGeoDF"]

        # Pass Tests
        for outTif, inTif in zip(outpath, tifpath):
            r1 = Raster(GeoTIFF=inTif)
            self.assertIsInstance(r1.raster, rasterio.DatasetReader)
            rasterDF = makeGridDF(self.geopath)
            meanDF = r1.assignMean(geoDF=rasterDF)
            self.assertIsInstance(meanDF, GeoDataFrame)
            outGeo = read_file(filename=outTif)
            self.assertIsInstance(outGeo, GeoDataFrame)
            self.assertTrue(meanDF.columns.equals(outGeo.columns))

        # Fail Test - Nonexistent File
        ghostpath = self.rasData["ghostTif"]
        for tif in ghostpath:
            with self.assertRaises(FileNotFoundError):
                r1 = Raster(GeoTIFF=tif)
                self.assertIsInstance(r1.raster, rasterio.DatasetReader)
                rasterMean = r1.assignMean(self.df)

        # Fail Test - Invalid Format
        for nonjson in self.ioFiles["NonJSON"]:
            with self.assertRaises(apexception.FileTypeError):
                r1 = Raster(GeoTIFF=nonjson)
                rasterMean = r1.assignMean(self.df)


if __name__ == '__main__':
    unittest.main()
