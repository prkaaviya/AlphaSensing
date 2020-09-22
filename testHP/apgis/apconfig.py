"""
Class module that implements the class *Config*.

The Config class generates an object that contains methods to extract configuration information
such as Sensor, Sat and Product IDs for several functions across the codebase that require this data.\n
It also contains mapping and validity check information for some functions to replace global constants.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import os

import apgis.apjsonio as jsonio
import apgis.apversion as version
import apgis.apexception as apexception

DATA_PRODUCTS = "Data Products"


class Config:
    """
    *Class for Satellite, Sensor and Product configuration extraction from the configmap.json.*

    **Class Methods:**\n
    - ``getSatellites:``       *A method that returns all Satellite IDs.*
    - ``getSensors:``          *A method that returns all Sensor IDs.*
    - ``getSatfromSensors:``   *A method that returns the Satellite ID for a Sensor ID.*
    - ``getSensorProducts:``   *A method that returns all the Products for a Sensor ID.*
    - ``getRevisitTime:``      *A method that returns the revisit time in days for a Satellite ID.*
    - ``getGEECollection:``    *A method that returns the GEE Collection ID for a Sensor ID.*

    **Class Attributes:**\n
    - ``configmap:``            *A dictionary that contains the parsed configmap.json file.*

    The Config class generates an object that contains methods to extract configuration information
    such as Sensor, Sat and Product IDs for several functions across the codebase that require this data.\n
    It also contains mapping and validity check information for some functions to replace global constants.

    References:
        *Refer to the apGIS Config JSON Documentation:*
    Documentation unavailable at this moment. Currently under development as of version 0.3.0.
    """
    # TODO: Update documentation reference ^^

    def __init__(self):
        """ **Constructor Method**\n
        Yields a ``Config`` object.

        Creates an object with a reference to a configData file and methods to access special
        properties of the configData file.The configData.json must exist in the same folder as
        this module and have the version tag as the versionlock.txt file.

        Raises:
            FileNotImplementedError: Occurs if the config.json cannot be found.

        Examples:
            Some example uses of this class are:\n
        *Initialising a ConfigMap object:*\n
        ``>> configData = Config()``
        """
        try:
            self.configData = jsonio.jsonRead(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           'meta/config.json'))
            if not version.checkInternalVersion():
                raise apexception.VersionError("configData Version mismatch")

        except FileNotFoundError as e:
            raise FileNotFoundError("Config Construction Failed @ JSON read: configData.json not found")
        except apexception.VersionError as e:
            raise apexception.VersionError(f"Config Construction Failed @ Config Version Check: {e}")
        except Exception as e:
            raise apexception.JSONError(f"Config Construction Failed @ JSON read: {e}")

    def getSatellites(self) -> list:
        """ *A method that returns all Satellite IDs.*

        The method extracts all available Satellite IDs from config.json and
        returns it as a list of Satellite ID strings.

        Returns:
            list:       A list of strings containing all the valid Satellite IDs.
        Raises:
            ConfigError:    Occurs if extracting Satellite IDs fails.

        Examples:
            Some example uses of this method are:\n
        *Extracting Satellite IDs:*\n
        ``>> configData = Config()``\n
        ``>> satIDs = configData.getSatellites()``
        """
        try:
            satellites = list(self.configData["satellites"].keys())
            return satellites

        except Exception as e:
            raise apexception.ConfigError(f"Satellite IDs Extraction Failed: {e}")

    def getSensors(self) -> list:
        """ *A method that returns all Sensor IDs.*

        The method extracts all available Sensor IDs from configData.json and
        returns it as a list of Sensor ID strings.

        Returns:
            list:       A list of strings containing all the valid Sensor IDs.
        Raises:
            ConfigError:    Occurs if extracting Sensor IDs fails.

        Examples:
            Some example uses of this method are:\n
        *Extracting Satellite IDs:*\n
        ``>> configData = Config()``\n
        ``>> satIDs = configData.getSatellites()``
        """
        try:
            satellites = self.getSatellites()

            sensors = []
            for sat in satellites:
                sensor = list(self.configData["satellites"][sat][DATA_PRODUCTS].keys())
                for sen in sensor:
                    sensors.append(sen)

            return sensors

        except Exception as e:
            raise apexception.ConfigError(f"Sensor IDs Extraction Failed: {e}")

    def getSatfromSensor(self, sensor: str) -> str:
        """ *A method that finds the Sat ID for a given a Sensor ID.*

        The method searched the configData.json file and finds the corresponding Satellite ID
        for a given Sensor ID and returns it as a string.

        Args:
            sensor:     The Sensor ID for which to find the corresponding Satellite ID.
        Returns:
            str:        A string containing the Satellite ID.
        Raises:
            ValueError:     Occurs if the sensor is not a valid Sensor ID.
            ConfigError:    Occurs if finding Satellite ID failed.

        Examples:
            Some example uses of this method are:\n
        *Extracting Satellite ID for "L2A":*\n
        ``>> configData = Config()``\n
        ``>> satIDs = configData.getSatfromSensor("L2A")``

        *Extracting Satellite ID for "L8SR":*\n
        ``>> configData = Config()``\n
        ``>> satIDs = configData.getSatfromSensor("L8SR")``
        """
        if sensor not in self.getSensors():
            raise ValueError("Satellite ID Lookup Failed @ Sensor ID check: Invalid Sensor ID")

        try:
            satellites = self.getSatellites()
            for sat in satellites:
                if sensor in list(self.configData["satellites"][sat][DATA_PRODUCTS].keys()):
                    return str(sat)

        except Exception as e:
            raise apexception.ConfigError(f"Satellite ID Lookup Failed @ Sensor ID lookup: {e}")

    def getSensorProducts(self, sensor: str) -> dict:
        """ *A method that extracts the Product IDs for a given Sensor ID.*

        The method extracts all the Product IDs associated with a Sensor ID and
        returns a dictionary that contains the Product ID and their
        constituent bands as a list of strings as key-value pairs.

        Args:
            sensor:     The Sensor ID for which to extract Sensor Products.
        Returns:
            dict:       A dictionary with product IDs.
        Raises:
            ValueError:     Occurs if the sensor is not a valid Sensor ID.
            ConfigError:    Occurs if extracting sensor Products fails.

        Examples:
            Some example uses of this method are:\n
        *Extracting Sensor products for "L2A":*\n
        ``>> configData = Config()``\n
        ``>> sensorProducts = configData.getSensorProducts("L2A")``
        """
        if sensor not in self.getSensors():
            raise ValueError("Sensor Products Extraction Failed @ Sensor ID check: Invalid Sensor ID")

        try:
            products = self.configData["products"][sensor]
            return dict(products)

        except Exception as e:
            raise apexception.ConfigError(f"Sensor Products Extraction Failed @ product list Extraction: {e}")

    def getSatRevisitTime(self, sat: str) -> int:
        """ *A method that extracts the revisit time for a Satellite ID.*

        The method finds the revisit time in days for a given Satellite ID.

        Args:
            sat:        The Satellite ID for which to retrieve the Revisit Time.
        Returns:
            int:        An integer representing the revisit time in days.
        Raises:
            ValueError:     Occurs if the sat is not a valid Satellite ID.
            ConfigError:    Occurs if extracting revisit time fails.

        Examples:
            Some example uses of this method are:\n
        *Extracting Satellite Revisit Time for Sentinel-2:*\n
        ``>> configData = Config()``\n
        ``>> revisitTime = configData.getSatRevisitTime("S2")``
        """
        if sat not in self.getSatellites():
            raise ValueError("Satellite Revisit Time Extraction Failed @ Sat ID check: Invalid Satellite ID.")

        try:
            revisitTime = self.configData["satellites"][sat]["Revisit Time"].split(" ")[0]
            return int(revisitTime)

        except Exception as e:
            raise apexception.ConfigError(f"Satellite Revisit Time Extraction Failed @ revisit time extraction: {e}")

    def getGEECollection(self, sensor: str) -> str:
        """ *A method that extracts the GEE Collection ID of a Sensor ID.*

        The method finds the Google Earth Engine Collection ID string from the configData.json
        file and returns it as a string to be used to construct an Earth Engine ImageCollection.

        Args:
            sensor:     The Sensor ID for which to retrieve the GEE Collection ID.
        Returns:
            str:        A string GEE Collection ID for the sensor.
        Raises:
            ValueError:     Occurs if the sensor is not a valid Sensor ID.
            ConfigError:    Occurs if extracting GEE Collection fails.

        Examples:
            Some example uses of this method are:\n
        *Extracting Sensor GEE Collection for Sentinel-2 L2A:*\n
        ``>> configData = Config()``\n
        ``>> revisitTime = configData.getGEECollection("L2A")``
        """
        if sensor not in self.getSensors():
            raise ValueError("GEE Collection Extraction Failed @ Sensor ID check: Invalid Sensor ID.")

        try:
            sat = self.getSatfromSensor(sensor)
            collection = self.configData["satellites"][sat][DATA_PRODUCTS][sensor]["GEE Collection"]
            return collection

        except Exception as e:
            raise apexception.ConfigError(f"GEE Collection Extraction Failed @ GEE collection extraction: {e}")

    def getFirebaseConfig(self, bucket: str) -> dict:
        """ *A method that extracts the Firebase Config for a given bucket for the app apGIS
        on antpod-canary project.*

        Args:
            bucket:     The bucket for which to retrieve configuration.
        Returns:
            dict:       A dictionary of firebase configData parameters.
        Raises:
            ConfigError:     Occurs if configData extraction failed.

        Examples:
            Some example uses of this method are:\n
        *Extracting Sensor GEE Collection for Sentinel-2 L2A:*\n
        ``>> configData = Config()``\n
        ``>> revisitTime = configData.getGEECollection("L2A")``
        """
        try:
            firebaseConfig = dict(self.configData["firebase"][bucket])
            return firebaseConfig

        except Exception as e:
            raise apexception.ConfigError(f"Firebase Config Extraction Failed: {e}")
