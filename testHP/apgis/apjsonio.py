"""
Module for a JSON I/O library.

Library of top-level functions to read, parse and write JSON and related formats
such as GeoJSON and TopoJSON files.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import os
import json
import geojson
import pathlib

import apgis.apexception as apexception

import typing
pathString = typing.Union[str, pathlib.Path]

JSON_EXT = ".json"
GEOJSON_EXT = ".geojson"


def jsonRead(filename: pathString) -> dict:
    """ *A function that reads a JSON file.*

    The function accepts the path to a JSON file which it reads and parses
    into a python dictionary. Accepts only an existing valid .JSON file.
    Uses json.load() to read JSON files.

    Args:
        filename:       A pathlike string to a JSON file to be read.
    Returns:
        dict:       A dictionary containing the contents of the JSON.
    Raises:
        TypeError:      Occurs if the filename is not a pathlike string.
        FileTypeError:      Occurs if the file is not a JSON file.
        FileNotFoundError:      Occurs if the file cannot be found at the specified location.
        JSONError:      Occurs if JSON reading fails.

    Examples:
        Some example uses of this method are:\n
    *Reading a JSON:*\n
    ``>> data = jsonRead(filename: "./sample.json")``
    """
    if not isinstance(filename, str):
        raise TypeError("JSON Read Failed @ pathString check: filename must be a pathLike string")

    if not filename.endswith(JSON_EXT):
        raise apexception.FileTypeError(f"JSON Read Failed @ filetype check: {filename} must be a .json file")

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"JSON Read Failed @ isfile check: {filename} could not be found")

    try:
        with open(filename) as jsonFile:
            jsonData = json.load(jsonFile)

        return dict(jsonData)

    except Exception as e:
        raise apexception.JSONError(f"JSON Read Failed @ JSON loading: {e}")


def jsonWrite(dictData: dict,
              filename: pathString) -> None:
    """ *A function that writes a JSON file.*

    The function accepts a python dictionary to write to a JSON and the path to write it to.
    Adds a '.json' extension to the filename if it doesn't already end with one.
    Uses json.dump() to write the dictionary into a JSON file.

    Args:
        dictData:   A dictionary containing the contents to be written into a JSON.
        filename:   A pathlike string to a JSON file to be read.
    Returns:
        None
    Raises:
        TypeError:  Occurs if the dictData is not a dictionary or if the filename is not a pathlike string.
        JSONError:  Occurs if JSON writing fails.

    Examples:
        Some example uses of this method are:\n
    *Writing a JSON:*\n
    ``>> jsonWriter(dictData: data, filename: "./output.json")``
    """
    if not isinstance(dictData, dict):
        raise TypeError("JSON Write Failed @ dict check: dictData must be a dictionary")

    if not isinstance(filename, str):
        raise TypeError("JSON Write Failed @ pathString check: filename must be a pathLike string")

    try:
        if not filename.endswith(JSON_EXT):
            filename = filename + JSON_EXT

        with open(filename, "w") as filePointer:
            json.dump(dictData, filePointer)

        return None

    except Exception as e:
        raise apexception.JSONError(f"JSON Write Failed @ JSON dumping: {e}")


def geojsonRead(filename: pathString) -> dict:
    """ *A function that reads a GeoJSON file.*

    The function accepts the path to a GeoJSON file which it reads and parses
    into a python dictionary. Accepts only an existing valid .GEOJSON file.
    Uses geojson.load() to read GeoJSON files.

    Args:
        filename:       A pathlike string to a GeoJSON file to be read.
    Returns:
        A dictionary containing the contents of the GeoJSON.
    Raises:
        TypeError:      Occurs if the filename is not a pathlike string.
        FileTypeError:      Occurs if the file is not a GeoJSON file.
        FileNotFoundError:  Occurs if the file cannot be found at the specified location.
        JSONError:      Occurs if GeoJSON reading fails.

    Examples:
        Some example uses of this method are:\n
    *Reading a GeoJSON:*\n
    ``>> data = geojsonRead(filename: "./sample.geojson")``
    """
    if not isinstance(filename, str):
        raise TypeError("GeoJSON Read Failed @ pathString check: filename must be a pathLike string")

    if not filename.endswith(GEOJSON_EXT):
        raise apexception.FileTypeError(f"GeoJSON Read Failed @ filetype check: {filename} must be a .geojson file")

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"GeoJSON Read Failed @ isfile check: {filename} could not be found")

    try:
        with open(filename) as geojsonFile:
            geojsonData = geojson.load(geojsonFile)

        return dict(geojsonData)

    except Exception as e:
        raise apexception.GeoJSONError(f"GeoJSON Read Failed @ GeoJSON loading: {e}")


def geojsonWrite(dictData: dict,
                 filename: pathString):
    """ Function implementation currently in progress. """
    # TODO: Implement GeoJSON Write Capabilities.
    raise NotImplementedError("Function is currently unavailable: GeoJSON Write")


def topojsonRead():
    """ Function implementation currently in progress. """
    # TODO: Implement TopoJSON Read Capabilities.
    raise NotImplementedError("Function is currently unavailable: TopoJSON Read")


def topojsonWrite():
    """ Function implementation currently in progress. """
    # TODO: Implement TopoJSON Write Capabilities.
    raise NotImplementedError("Function is currently unavailable: TopoJSON Write")
