"""
Module for GeoDataFrame Manipulations.

Library of top-level function to manipulate GeoPandas GeoDataFrames.
Contains functions to modify column data, set CRS and to create a
Square grid DataFrame and to overlay it into another GeoDataFrame.

Methods: setCRS, createGrid, overlayGrid, makeGridDF, insertColumns,
dropColumns, exportGeoDF.

Author: AntPod Designs Pvt Ltd.
"""
import geopandas as gpd

import apgis.apexception as apexception


def setCRS(geoDF: gpd.GeoDataFrame,
           crsString: str = "EPSG:4326"):
    """ A function that sets the CRS(Coordinate Reference System) of a GeoDataFrame.

    The function accepts an EPSG CRS string along with GeoDataFrame and sets the CRS of
    the GeoDataFrame to the specified EPSG CRS String.\n
    Accepts a formatted CRS Strings as well just the EPSG number as a numeric string.
    Defaults to "EPSG:4326".

    Keyword Args:
        geoDF:      A GeoDataFrame with a geometry column which needs it CRS changed.
        crsString:  An EPSG CRS String.
    Returns:
        A GeoDataFrame with a geometry column with a CRS set to a specified crsString.
    Raises:
        TypeError:  if parameters type check fails.
        CRSError:   if CRS set runtime fails.

    Examples:
        *Setting CRS tp EPSG:4326*
    ``>> geoDF4326 = setCRS(geoDF=geodf)``

        *Setting CRS tp EPSG:3857*
    ``>> geoDF3857 = setCRS(geoDF=geodf, crsString="3857")``

        *Setting CRS tp EPSG:32642*
    ``>> geoDF3857 = setCRS(geoDF=geodf, crsString="EPSG:32642")``

    References:
        *Standard EPSG Strings:*
    https://spatialreference.org/ref/epsg/
    """
    # import fiona
    # from pyproj import CRS

    if not isinstance(crsString, str):
        raise TypeError("GeoDF CRS Set Failed @ type check: crsString must be a string")

    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("GeoDF CRS Set Failed @ type check: geoDF must be a GeoDataFrame")

    try:
        crsString = crsString.upper()
        if not crsString.startswith("EPSG:"):
            if crsString.isnumeric():
                newCRS = f"EPSG:{crsString}"
            else:
                raise ValueError("Invalid crsString format")
        else:
            newCRS = crsString

        # crsProj = CRS(newCRS)
        # geoDF.crs = fiona.crs.from_epsg(crsProj)
        geoDF.crs = newCRS
        # geoDF = geoDF.set_crs(newCRS, allow_override=True)

        return geoDF

    except Exception as e:
        raise apexception.CRSError(f"GeoDF CRS Set Failed @ crs set runtime: {e}")


def createGrid(geoDF: gpd.GeoDataFrame, spacing: float = 0.0005):
    """ A function that creates a 2D square grid as a GeoDataFrame.

    The function creates a GeoDataFrame with a 2D Square Grid of a specified spacing.\n
    Spacing defaults to 0.0005 degrees.

    Keyword Args:
        geoDF:          A GeoDataFrame to use as reference to create the grid.
        spacing:        The spacing of the square grid.
    Returns:
        A GeoDataFrame with a list of Polygons as grids.
    Raises:
        TypeError:      if geoDF is not a GeoDataFrame.
        DataFrameError: if grid build runtime fails.

    Examples:
        *Creating a grid of 0.0010 degrees*
    ``>> grid = createGrid(geoDF=geodf, spacing=0.0010)``

    Notes:
        bbox = [longmin, latmin, longmax, latmax] #bbox format\n
        bbox = User.boi (once we interconnect User from GEE files)\n
        ymin, xmin, ymax, xmax = bbox[0], bbox[1], bbox[2], bbox[3]\n
    """
    import numpy as np
    from shapely.geometry import Polygon

    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("Grid Generation Failed @ type check: geoDF must be a GeoDataFrame")

    try:
        xmin, ymin, xmax, ymax = geoDF.total_bounds

        rows = int(np.ceil((ymax - ymin) / spacing))
        cols = int(np.ceil((xmax - xmin) / spacing))

        xLeftOrigin = xmin
        xRightOrigin = xmin + spacing
        yTopOrigin = ymax
        yBottomOrigin = ymax - spacing

    except Exception as e:
        raise apexception.DataFrameError(f"Grid Generation Failed @ dataframe limit check: {e}")

    try:
        polygons = []
        for col in range(cols):
            yTop, yBottom = yTopOrigin, yBottomOrigin
            for row in range(rows):
                polygons.append(Polygon([(xLeftOrigin, yTop), (xRightOrigin, yTop),
                                         (xRightOrigin, yBottom), (xLeftOrigin, yBottom)]))
                yTop -= spacing
                yBottom -= spacing

            xLeftOrigin += spacing
            xRightOrigin += spacing

    except Exception as e:
        raise apexception.DataFrameError(f"Grid Generation Failed @ grid generation runtime: {e}")

    try:
        gridDF = gpd.GeoDataFrame({'geometry': polygons})
        setCRS(gridDF, "EPSG:4326")
        return gridDF

    except Exception as e:
        raise apexception.DataFrameError(f"Grid Generation Failed @ grid GeoDataFrame runtime: {e}")


def overlayGrid(geoDF: gpd.GeoDataFrame,
                crsString: str = "EPSG:4326",
                spacing: float = 0.0005):
    """ A function that overlays a 2D square grid onto a GeoDataFrame.

    Keyword Args:
        geoDF:      A GeoDataFrame on which to overlay a square grid
        spacing:    The spacing of the square grid. Defaults to 0.0005 degrees.
        crsString:  An EPSG CRS String.
    Returns:
        A GeoDataFrame that has been overlaid with a square grid.
    Raises:
        TypeError:      if geoDF is not a GeoDataFrame.
        CRSError:       if crs check or crs set runtime fails.
        DataFrameError: if grid generation or overlay runtime fails.

    Examples:
        *Overlaying a grid of 0.0004 degrees*
    ``>> grid = overlayGrid(geoDF=geodf, crsString="EPSG:4326", spacing=0.0004)``
    """
    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("Grid Overlay Failed @ type check: geoDF must be a GeoDataFrame")

    crsString = crsString.upper()
    if not crsString.startswith("EPSG:"):
        if crsString.isnumeric():
            crsString = f"EPSG:{crsString}"
        else:
            raise apexception.CRSError("Grid Overlay Failed @ crs check: Invalid crsString format")

    try:
        gridDF = createGrid(geoDF=geoDF, spacing=spacing)
    except Exception as e:
        raise apexception.DataFrameError(f"Grid Overlay Failed @ grid generation runtime: {e}")

    try:
        setCRS(geoDF, crsString=crsString)
        setCRS(gridDF, crsString=crsString)

    except Exception as e:
        raise apexception.CRSError(f"Grid Overlay Failed @ crs set runtime: {e}")

    try:
        geoDF = gpd.overlay(gridDF, geoDF)
        return geoDF

    except Exception as e:
        raise apexception.DataFrameError(f"Grid Overlay Failed @ overlay runtime: {e}")


def makeGridDF(geojson: str,
               crsString: str = "EPSG:4326",
               spacing: float = 0.0005):
    """ A function that creates gridDF file from a GeoJSON file.

    The function generates a gridDF from a GeoJSON file, a
    crs string and grid spacing value.\n
    Option to set spacing of square grid. Defaults to 0.0005 degrees.\n
    Option to set CRS of gridDF. Must be a valid EPSG String.\n
    Defaults to ``EPSG:4326``

    Keyword Args:
        geojson:        The path with the name of the GeoJSON file. Must be a valid GeoJSON.
        crsString:      An EPSG CRS String.
        spacing:        The spacing of the square grid.
    Returns:
        A GeoDataFrame that has been overlaid with a square grid in the specified CRS.
    Raises:
        FileTypeError:  if file is not geojson.
        TypeError:      if crs string is not a string.
        CRSError:       if crs check fails.
        DataFrameError: if gridDF generation runtime fails.

    Examples:
        *Generating a GridDF from a GeoJSON*
    ``>> gridDF = makeGridDF(geojson="sample.geojson", crsString:"EPSG:3857", spacing=0.0003)``
    """
    # import os

    if not geojson.endswith(".geojson"):
        raise apexception.FileTypeError("GridDF Generation Failed @ file check: "
                                        "geojson string must contain path to a GeoJSON file")

    # TODO: Exception not working in test_makeGridDF()
    # if geojson not in os.listdir():
    #     raise FileNotFoundError("GridDF Generation Failed @ file check:
    #                              Could not locate the GeoJSON in the path specified.")

    if not isinstance(crsString, str):
        raise TypeError("GridDF Generation Failed @ type check: crsString must be a string")

    try:
        crsString = crsString.upper()
        if not crsString.startswith("EPSG:"):
            if crsString.isnumeric():
                newCRS = f"EPSG:{crsString}"
            else:
                raise ValueError("Invalid crsString format")
        else:
            newCRS = crsString

    except Exception as e:
        raise apexception.CRSError(f"GridDF Generation Failed @ crs check: {e}")

    try:
        geoDF = gpd.read_file(geojson)
        gridDF = overlayGrid(geoDF=geoDF, crsString=newCRS, spacing=spacing)

        return gridDF

    except Exception as e:
        raise apexception.DataFrameError(f"GridDF Generation Failed @ gridDF generation runtime: {e}")


def insertColumns(geoDF: gpd.GeoDataFrame,
                  columnData: dict):
    """ A function that inserts new columns into a GeoDataFrame.\n

    The function adds a column/list of columns into a GeoDataFrame.
    New columns and their initialisation values are expected in a dictionary
    with keys representing the new column names and values representing
    the default value of the corresponding column.

    Keyword Args:
        geoDF:          A GeoDataFrame in which to insert new columns.
        columnData:     A dictionary containing new columns names and their initialisation values.
    Returns:
        A GeoDataFrame with new columns added.
    Raises:
        TypeError:      if parameter type check fails.
        DataFrameError: if insertion runtime fails.

    Examples:
        *Inserting a column*
    ``>> newDF = insertColumns(geoDF=geodf, columnData={"mean": 0.5, "max":0.8})``
    """
    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("GeoDF Column Insertion Failed @ type check: geoDF must be a GeoDataFrame")

    if not isinstance(columnData, dict):
        raise TypeError("GeoDF Column Insertion Failed @ type check: columnData must be a dictionary")

    try:
        for colName, colValue in columnData.items():
            geoDF.insert(len(geoDF.columns), colName, colValue)

        geo = geoDF['geometry']
        geoDF.drop(labels=['geometry'], axis=1, inplace=True)
        geoDF.insert(len(geoDF.columns), 'geometry', geo)

        return geoDF

    except Exception as e:
        raise apexception.DataFrameError(f"GeoDF Column Insertion Failed @ column insertion: {e}")


def dropColumns(geoDF: gpd.GeoDataFrame,
                columnList: list):
    """ A function that drops columns from a GeoDataFrame.\n

    The function drops a column/list of columns from a GeoDataFrame.
    Columns that need to be dropped are expected in a list that
    contains the column names as strings.

    Keyword Args:
        geoDF:          A GeoDataFrame in which to drop columns.
        columnList:     A list of column names that need to be dropped.
    Returns:
        A GeoDataFrame with columns dropped.
    Raises:
        TypeError:      if parameter type check fails.
        DataFrameError: if drop runtime fails.

    Examples:
        *Dropping a column*
    ``>> newDF = dropColumns(geoDF=geodf, columnData=["mean", "max"])``
    """
    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("GeoDF Column Drop Failed @ type check: geoDF must be a GeoDataFrame")

    if not isinstance(columnList, list):
        raise TypeError("GeoDF Column Drop Failed @ type check: columnList must be a list")

    try:
        for colName in columnList:
            geoDF = geoDF.drop([colName], axis=1)

        return geoDF

    except Exception as e:
        raise apexception.DataFrameError(f"GeoDF Column Drop Failed @ column dropping: {e}")


def exportGeoDF(geoDF: gpd.GeoDataFrame,
                fileName: str,
                fileFormat: str):
    """ A function that exports a GeoDataFrame.

    The function exports a GeoDataFrame into to a specified file
    format with a specified file name.\n
    Available file formats:
        - GeoJSON
        - Shapefile

    Keyword Args:
        geoDF:          A GeoDataFrame that need to be written to an external file.
        fileName:       A filename to use for the exported file.
        fileFormat:     The file format in which to export the GeoDataFrame.
    Raises:
        TypeError:      if parameter type check fails.
        IOError:        if export fails.
        NotImplementedError:    if unsupported file format is chosen.

    Examples:
        *Example Description*
    ``>> var = codeExample(argName=arg)``
    """
    availableFormats = {
        "GeoJSON": "geojson",
        "Shapefile": "shp"
    }

    if not isinstance(geoDF, gpd.GeoDataFrame):
        raise TypeError("GeoDF Export Failed @ type check: geoDF must be a GeoDataFrame")

    if not isinstance(fileName, str):
        raise TypeError("GeoDF Export Failed @ type check: fileName must be a string")

    if isinstance(fileFormat, str):
        if fileFormat not in availableFormats:
            raise NotImplementedError("GeoDF Export Failed @ export format check: fileFormat is not supported")
    else:
        raise TypeError("GeoDF Export Failed @ type check: fileFormat must be a string")

    try:
        file = ".".join([fileName, availableFormats[fileFormat]])
        geoDF.to_file(file, driver=fileFormat)

    except Exception as e:
        raise IOError(f"GeoDF Export Failed @ file writing: {e}")
