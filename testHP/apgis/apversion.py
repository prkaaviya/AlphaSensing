"""
Class module that implements the class *Version* along with some related top-level functions.

The Version class is a type Class that parses a string representing a package/subpackage
version tag. This includes the numeric version, the channel, and all the constituent attributes.\n
Additionally this module contains some top-level functions that are used to retrieve
Version tags across the codebase and modify them collectively.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import os
import re
import linecache
import apgis.apexception as apexception

import apgis.apjsonio as jsonio

VERSION_LOCK_LINE = 3
VERSION_INIT_LINE = 3

VERSION_LOCK_FILE = 'meta/versionlock.txt'
VERSION_INIT_FILE = './__init__.py'
VERSION_CONFIG_FILE = 'meta/config.json'


class Version:
    """
    *Class for Version tag strings and related attributes.*

    **Class Attributes:**\n
    - ``major:``        *A numeric string representing the X.0.0 i.e MAJOR version*
    - ``minor:``        *A numeric string representing the 0.X.0 i.e MINOR version*
    - ``patch:``        *A numeric string representing the 0.0.X i.e PATCH version*
    - ``channel:``      *A string representing the version channel*
    - ``version:``      *A string representing the numeric version tag*
    - ``fullVersion:``  *A string representing the formatted version tag which includes the channel*

    The Version class is a type Class that parses a string representing a package/subpackage
    version tag. This includes the numeric version, the channel, and all the constituent attributes.\n
    Contains methods to compare and represent Version objects.

    References:
        Some references to related to this topic:\n
    *Semantic Versioning:*\n
    https://semver.org/
    """

    def __init__(self, versionTag: str):
        """ **Constructor Method**\n
        Yields a ``Version`` object.

        Parses a Version tag into it's constituent attributes such as the MAJOR, MINOR and PATCH
        numbers and the version channel tag.
        The versionString to be parsed must contain three numeric values separated by a period and
        may or may not start with a lowercase 'v'. The channel tag is optional as well.\n

        Args:
            versionTag:  The version string tag to be parsed into a Version object.
        Raises:
            VersionError:   Occurs if the version string regex parsing fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising a Version object:*\n
        ``>> version = Version("v0.3.5-stable")``\n
        ``>> version = Version("0.3.5-canary")``\n
        ``>> version = Version("v1.5.5")``
        """
        try:
            parameters = re.search(r"v?([\d]*)\.([\d]*)\.([\d]*)-?([\w]*)", versionTag)

            if not parameters:
                raise apexception.VersionError("No Regex Match")

        except Exception as e:
            raise apexception.VersionError(f"Version Construction Failed @ Regex Matching : {e}")

        self.major, self.minor, self.patch, self.channel = parameters.group(1, 2, 3, 4)
        self.versionNumber = f"{self.major}.{self.minor}.{self.patch}"

    @property
    def fullVersion(self):
        """ Formatted Version Tag - 'vX.Y.Z-channel'. """
        return f"v{self.versionNumber}" if (self.channel == "") else f"v{self.versionNumber}-{self.channel}"

    def __eq__(self, other):
        """ Compares two *Version* objects for equality. """
        return True if (self.major == other.major and self.minor == other.minor and
                        self.patch == other.patch and self.channel == other.channel) else False

    def __repr__(self):
        """ Represents a *Version* object. """
        return self.fullVersion


def getVersionLock():
    """ *A function that returns the Version from the versionlock.txt file as a Version object.* """
    return Version(linecache.getline(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), VERSION_LOCK_FILE), VERSION_LOCK_LINE))


def setVersionLock(version: Version):
    """ *A function that sets the version of the versionlock.txt file.*

    Args:
        version:    The Version object to set into versionlock.txt.
    Raises:
        IOError:    Occurs if file Read/Write fails.

    Examples:
        Some example uses of this method are:\n
    *Setting versionlock.txt version tag:*\n
    ``>> setVersionLock(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        with open(VERSION_LOCK_FILE, "r") as file:
            vlockData = file.readlines()

    except Exception as e:
        raise IOError(f"Setting Version Lock Tag Failed @ Read File: {e}")

    try:
        vlockData[VERSION_LOCK_LINE-1] = versionString + "\n"
        with open(VERSION_LOCK_FILE, "w") as file:
            file.writelines(vlockData)

    except Exception as e:
        raise IOError(f"Setting Version Lock Tag Failed @ Write File: {e}")


def getInitVersion():
    """ *A function that returns the Version from the __init__.py file as a Version object.* """
    return Version(linecache.getline(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), VERSION_INIT_FILE), VERSION_INIT_LINE))


def setInitVersion(version: Version):
    """ *A function that sets the version of the __init__.py file.*

    Args:
        version:    The Version object to set into __init__.py.
    Raises:
        IOError:    Occurs if file Read/Write fails.

    Examples:
        Some example uses of this method are:\n
    *Setting __init__.py version tag:*
    ``>> setInitVersion(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        with open(VERSION_INIT_FILE, "r") as file:
            initVersion = file.readlines()

    except Exception as e:
        raise IOError(f"Setting Init Version Tag Failed @ Read File: {e}")

    try:
        initVersion[VERSION_INIT_LINE-1] = f"Version: {versionString}\n"
        with open(VERSION_INIT_FILE, "w") as file:
            file.writelines(initVersion)

    except Exception as e:
        raise IOError(f"Setting Init Version Tag Failed @ Write File: {e}")


# TODO: Implement version locking in a mini external script.
def getConfigVersion():
    """ *A function that returns the Version from the config.json file as a Version object.* """
    return Version(jsonio.jsonRead(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), VERSION_CONFIG_FILE))['version'])


def setConfigVersion(version: Version):
    """ *A function that sets the version of the config.json file.*

    Args:
        version:    The Version object to set into config.json.
    Raises:
        IOError:    Occurs if file Read/Write fails.

    Examples:
        Some example uses of this method are:\n
    *Setting config.json version tag:*
    ``>> setConfigVersion(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        config = jsonio.jsonRead(VERSION_CONFIG_FILE)
        config['version'] = versionString
        jsonio.jsonWrite(config, VERSION_CONFIG_FILE)

    except Exception as e:
        raise apexception.JSONError(f"Setting Config Version Tag Failed @ Read/Write File: {e}")


def setPackageVersion(versionString: str):
    """ *A function that simultaneously updates all version tags in the package. Accepts a version string tag.*"""
    try:
        version = Version(versionTag=versionString)
        setConfigVersion(version=version)
        setInitVersion(version=version)
        setVersionLock(version=version)

    except Exception as e:
        raise apexception.VersionError(f"Setting Package Version Tag Failed: {e}")


def checkInternalVersion():
    """ *A function that checks if config.json and versionlock.txt have the same version tags. Returns a bool*"""
    return True if (getConfigVersion() == getVersionLock()) else False


# Simple script to modify version number across the codebase.
# if __name__ == "__main__":
#     setPackageVersion("0.4.3")
