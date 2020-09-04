"""
Class module that implements the class **Raster**.

The Raster class loads a GeoTIFF and parses metadata from its name.
Contains methods to plot, clip, retrieve window from a GeoTIFF.
Additionally contains a method to assign means into a GeoDF
from the the Raster.

Author: AntPod Designs Pvt Ltd.
"""
import os
import warnings
import rasterio as rio

import apgis.gisgeodf as geodf
import apgis.apexception as apexception

from apgis.apconfig import Config

CONFIG = Config()

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Raster:
    """
    Class for Raster Manipulations.

    The Raster class loads a GeoTIFF and parses metadata from its name.
    Contains methods to plot, clip, retrieve window from a GeoTIFF.
    Additionally contains a method to assign means into a GeoDF
    from the the Raster.

    Class Attributes:
        - ``GeoTIFF:``          The name of the GeoTIFF to be initialised as a Raster.
        - ``raster:``           The DatasetReader representing the GeoTIFF.
        - ``sensor:``           The Sensor ID of the GeoTIFF.
        - ``product:``          The Product ID of the GeoTIFF.
        - ``day:``              The acquisition day of the GeoTIFF.
        - ``month:``            The acquisition month of the GeoTIFF.
        - ``year:``             The acquisition year of the GeoTIFF.
        - ``dateString:``       The acquisition DateString (YYYY-MM-DD) of the GeoTIFF.
        - ``bandCount:``        The number of bands in the GeoTIFF.

    Class Methods:
        - ``show:``             A method to plot a Raster.
        - ``getWindow:``        A method to create a rectangular subset with a GeoDF.
        - ``clip:``             A method to clip a Raster according to a GeoDF.
        - ``assignMean:``       A method to assign mean values of a product into a GeoDF.
    """

    def __init__(self, GeoTIFF: str):
        """ Constructs a *Raster* object.\n

        Holds the name of the GeoTIFF as primary attribute along with the metadata
        extracted from it's name. Loads the corresponding GeoTIFF as a DatasetReader
        and stores it as an attribute. Accepts a GeoTIFF name as part of a URI.\n
        Yields a *Raster* object.

        Keyword Args:
            GeoTIFF:            A filepath to a GeoTIFF image.
        Raises:
            TypeError:          if GeoTIFF is not a string.
            FileTypeError:      if GeoTIFF is not GeoTIFF file ending with .tif.
            FileNotFoundError:  if GeoTIFF does not exist.
            RasterError:        if raster loading fails.
            AttributeError:     if metadata generation fails.

        Examples:
            *Initialising a Raster object:*
        ``>> raster = Raster(GeoTIFF="sample.tif")``
         """
        if not isinstance(GeoTIFF, str):
            raise TypeError("Raster Object Construction Failed @ type check: "
                            "GeoTIFF must be a str")

        if not GeoTIFF.endswith('.tif'):
            raise apexception.FileTypeError("Raster Object Construction Failed @ type check: "
                                            "GeoTIFF must end with a .tif extension")

        if not os.path.isfile(GeoTIFF):
            raise FileNotFoundError("Raster Object Construction Failed @ file check: "
                                    "GeoTIFF image not found")

        try:
            self.GeoTIFF = GeoTIFF
            self.raster = rio.open(self.GeoTIFF, "r")

        except Exception as e:
            raise apexception.RasterError(f"Raster Object Construction Failed @ raster read: {e}")

        try:
            metadataList = GeoTIFF.split('.')[0].split('-')
            self.sensor = metadataList[-5]
            self.product = metadataList[-4]
            self.day = metadataList[-1]
            self.month = metadataList[-2]
            self.year = metadataList[-3]
            self.dateString = '-'.join(metadataList[-3:-1])
            self.bandCount = self.raster.count

        except Exception as e:
            raise AttributeError(f"Raster Object Construction Failed @ metadata generation: {e}")

    def show(self, indexName: str,
             cmap: str = 'RdYlGn'):
        """ A method that plots a DatasetReader object.

        Keyword Args:
            indexName:      A string Product ID.
            cmap:           The visualization colormap.
        Raises:
            TypeError:      if parameter type checks fails.
            KeyError:       if sensor check fails.
            RasterError:    if plot runtime fails.

        Examples:
            *Plotting a raster*
        ``>> raster = Raster(GeoTIFF="sample.tif")``\n
        ``>> raster.show(indexName="NDVI", cmap="summer")``

        References:
            *Colormap Reference:*
        https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html

            *Antpod Product IDs:*
        Documentation unavailable at this moment. Currently under development as of version 0.3.0.

        Notes:
             Works best for NDVI as of 0.3.0.
        """
        import matplotlib.pyplot as plt
        from rasterio import plot

        if not isinstance(indexName, str):
            raise TypeError("Raster Plot Failed @ type check: index must be a string")

        if not isinstance(cmap, str):
            raise TypeError("Raster Plot Failed @ type check: cmap must be a string")
        else:
            if str not in plt.colormaps():
                raise TypeError("Raster Plot Failed @ type check: cmap must be a valid colormap string")

        sensorProducts = CONFIG.getSensorProducts(sensor=self.sensor)

        if self.product in sensorProducts.keys():
            productBands = sensorProducts[self.product]
        else:
            raise KeyError(f"Raster Plot Failed @ sensor check: "
                           f"{self.product} is not supported for this {self.sensor}")
        try:
            band = productBands.index(indexName)
            plotIndex = self.raster.read(int(band + 1))
            plot.show(plotIndex, cmap=cmap, title=str(indexName))

        except Exception as e:
            raise apexception.RasterError(f"Raster Plot Failed @ plot runtime: {e}")

    def getWindow(self, geoDF: geodf.gpd.GeoDataFrame):
        """ A method that creates a GeoDataFrame window.

        Accepts a GeoDataFrame and returns a Window that contains
        rectangular subset of DatasetReader object according to the
        bounding box of GeoDataFrame.

        Keyword Args:
            geoDF:          A GeoDataFrame with a geometry column.
        Returns:
            A Window object that stores the overlapping contents of raster and GeoDF.
        Raises:
            TypeError:      if geoDF is not GeoDataFrame.
            DataFrameError: if dataframe read fails.
            RasterError:    if raster windowing fails.

        Examples:
            *Creating Raster Window:*
        ``>> raster = Raster(GeoTIFF="sample.tif")``\n
        ``>> window = raster.getWindow(geoDF=geodf)``
        """
        if not isinstance(geoDF, geodf.gpd.GeoDataFrame):
            raise TypeError("Raster Windowing Failed @ type check: geoDF must be a GeoDataFrame")

        try:
            geoBBOX = geoDF.total_bounds

        except Exception as e:
            raise apexception.DataFrameError(f"Raster Windowing Failed @ bound retrieval: {e}")

        try:
            window = self.raster.window(*geoBBOX)
            return window

        except Exception as e:
            raise apexception.RasterError(f"Raster Windowing Failed @ window runtime: {e}")

    def clip(self, geoDF: geodf.gpd.GeoDataFrame,
             index: int):
        """
        A method that clips a DatasetReader object.

        Accepts a GeoDataFrame and the index which is an integer representation of
        the raster band that clips the Raster object's band according to the extent
        of the bounding box of GeoDataFrame by generating the Window for the GeoDataFrame.\n

        The returned objects are:
        window:     A Window object that stores the overlapping contents of raster and GeoDF.
        clipping:   A numpy array of the DatasetReader object adjusted according to the window
                    provided by GeoDataFrame boundaries.

        Keyword Args:
            geoDF:      A GeoDataFrame with a geometry column.
            index:      An integer to read the corresponding index of DatasetReader object.
        Returns:
            a clipped numpy array and a Window object.
        Raises:
            TypeError:      if parameter type check fails.
            ValueError:     if bandCount check fails.
            RasterError:    if clipping fails.

        Examples:
            *Clipping a Raster*
        ``>> raster = Raster(GeoTIFF="sample.tif")``\n
        ``>> clipping, window = raster(argName=arg)``
        """
        if not isinstance(geoDF, geodf.gpd.GeoDataFrame):
            raise TypeError("Raster Clipping Failed @ type check: geoDF must be a GeoDataFrame")

        if not isinstance(index, int):
            raise TypeError("Raster Clipping Failed @ type check: index must be an integer")
        else:
            if index not in range(1, self.bandCount + 1):
                raise ValueError("Raster Clipping Failed @ bandCount check: index not available in the raster")

        try:
            window = self.getWindow(geoDF)
            clipping = self.raster.read(index, window=window)
            return clipping, window

        except Exception as e:
            raise apexception.RasterError(f"Raster Clipping Failed @ clip runtime: {e}")

    def assignMean(self, geoDF: geodf.gpd.GeoDataFrame):
        """
        A method that assigns mean value of products corresponding to the grids in GeoDataFrame.

        Keyword Args:
            geoDF:          A GeoDataFrame with a geometry column.
        Returns:
            A GeoDataFrame with a geometry column with new mean index values of the sensorProduct
        Raises:
            TypeError:      if geoDF is not a GeoDataFrame.
            ValueError:     if bandCount check fails.
            RasterError:    if mean assignment fails.
            DataFrameError: if geometry relocation fails.

        Examples:
            *Assigning Mean*
        ``>> raster = Raster(GeoTIFF="sample.tif")``\n
        ``>> meanDF = raster.assignMean(geoDF=geodf)``
        """
        import rasterstats

        if not isinstance(geoDF, geodf.gpd.GeoDataFrame):
            raise TypeError("Raster Mean Assignment Failed @ type check: "
                            "geoDF must be a GeoDataFrame")

        productList = CONFIG.getSensorProducts(self.sensor)[self.product]

        if len(productList) != self.bandCount:
            raise ValueError("Raster Mean Assignment Failed @ bandCount check: "
                             "length of productList and raster bands do not match")

        try:
            meanValues = ['mean' + x for x in productList]

            for index in range(1, self.bandCount + 1):
                clipping, window = self.clip(geoDF, index)
                transform = self.raster.window_transform(window)
                stats = rasterstats.zonal_stats(geoDF.geometry, clipping, nodata=-999, affine=transform)
                for i, stat in enumerate(stats, start=0):
                    try:
                        geoDF.loc[i, meanValues[index - 1]] = stat['mean']
                    except Exception as e:
                        raise KeyError(f"column spanning error - {e}")

        except Exception as e:
            raise apexception.RasterError(f"Raster Mean Assignment Failed @ mean calculation: {e}")

        try:
            geo = geoDF['geometry']
            geoDF.drop(labels=['geometry'], axis=1, inplace=True)
            geoDF.insert(len(geoDF.columns), 'geometry', geo)

            return geoDF

        except Exception as e:
            raise apexception.DataFrameError(f"Raster Mean Assignment Failed @ GeoDataFrame geometry relocation: {e}")
