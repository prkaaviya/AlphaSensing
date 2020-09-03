"""
Class module that implements the class *Version* along with some related top-level functions.

The Version class is a type Class that parses a string representing a package/subpackage
version tag. This includes the numeric version, the channel, and all the constituent attributes.\n
Additionally this module contains some top-level functions that are used to retrieve
Version tags across the codebase and modify them collectively.

Author: AntPod Designs Pvt Ltd.
"""
import os
import re
import linecache
import apgis.apexception as apexception

import apgis.apjsonio as jsonio

VERSION_LOCK_LINE = 3
VERSION_INIT_LINE = 2


class Version:
    """
    Class for Version tag strings and related attributes.

    The Version class is a type Class that parses a string representing a package/subpackage
    version tag. This includes the numeric version, the channel, and all the constituent attributes.\n
    Contains methods to compare and represent Version objects.

    Class Attributes:
        - ``major:``        *A numeric string representing the X.0.0 i.e MAJOR version*
        - ``minor:``        *A numeric string representing the 0.X.0 i.e MINOR version*
        - ``patch:``        *A numeric string representing the 0.0.X i.e PATCH version*
        - ``channel:``      *A string representing the version channel*
        - ``version:``      *A string representing the numeric version tag*
        - ``fullVersion:``  *A string representing the formatted version tag which includes the channel*

    References:
        *Semantic Versioning:*
    https://semver.org/
    """

    def __init__(self, versionTag: str):
        """ Constructs a *Version* object.\n

        Parses a Version tag into it's constituent attributes such as the MAJOR, MINOR and PATCH
        numbers and the version channel tag.
        The versionString to be parsed must contain three numeric values separated by a period and
        may or may not start with a lowercase 'v'. The channel tag is optional as well.\n
        Yields a *Version* object.

        Args:
            versionTag:  The version string tag to be parsed into a Version object.
        Raises:
            VersionError:   if the version string regex parsing fails.

        Examples:
            *Initialising a Version object:*
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
        self.version = f"{self.major}.{self.minor}.{self.patch}"

    @property
    def fullVersion(self):
        """ Formatted Version Tag - 'vX.Y.Z-channel'. """
        return f"v{self.version}" if (self.channel == "") else f"v{self.version}-{self.channel}"

    def __eq__(self, other):
        """ Compares two *Version* objects for equality. """
        return True if (self.major == other.major and self.minor == other.minor and
                        self.patch == other.patch and self.channel == other.channel) else False

    def __repr__(self):
        """ Represents a *Version* object. """
        return self.fullVersion


def getVersionLock():
    """ A function that returns the Version from the versionlock.txt file as a Version object. """
    return Version(linecache.getline(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'meta/versionlock.txt'), VERSION_LOCK_LINE))


def setVersionLock(version: Version):
    """ A function that sets the version of the versionlock.txt file.

    Args:
        version:    The Version object to set into versionlock.txt.
    Raises:
        IOError:    if file Read/Write fails.

    Examples:
        *Setting versionlock.txt version tag:*
    ``>> setVersionLock(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        with open('meta/versionlock.txt', "r") as file:
            vlockData = file.readlines()

    except Exception as e:
        raise IOError(f"Setting Version Lock Tag Failed @ Read File: {e}")

    try:
        vlockData[VERSION_LOCK_LINE-1] = versionString + "\n"
        with open('meta/versionlock.txt', "w") as file:
            file.writelines(vlockData)

    except Exception as e:
        raise IOError(f"Setting Version Lock Tag Failed @ Write File: {e}")


def getInitVersion():
    """ A function that returns the Version from the __init__.py file as a Version object. """
    return Version(linecache.getline(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), './__init__.py'), VERSION_INIT_LINE))


def setInitVersion(version: Version):
    """ A function that sets the version of the __init__.py file.

    Args:
        version:    The Version object to set into __init__.py.
    Raises:
        IOError:    if file Read/Write fails.

    Examples:
        *Setting __init__.py version tag:*
    ``>> setInitVersion(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        with open('./__init__.py', "r") as file:
            initVersion = file.readlines()

    except Exception as e:
        raise IOError(f"Setting Init Version Tag Failed @ Read File: {e}")

    try:
        initVersion[VERSION_INIT_LINE-1] = f"Version: {versionString}\n"
        with open('./__init__.py', "w") as file:
            file.writelines(initVersion)

    except Exception as e:
        raise IOError(f"Setting Init Version Tag Failed @ Write File: {e}")


# TODO: Implement version locking in a mini external script.
def getConfigVersion():
    """ A function that returns the Version from the config.json file as a Version object. """
    return Version(jsonio.jsonRead(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'meta/config.json'))['version'])


def setConfigVersion(version: Version):
    """ A function that sets the version of the config.json file.

    Args:
        version:    The Version object to set into config.json.
    Raises:
        IOError:    if file Read/Write fails.

    Examples:
        *Setting config.json version tag:*
    ``>> setConfigVersion(version=Version('v0.3.2-dev'))``\n
    """
    try:
        versionString = version.fullVersion
        config = jsonio.jsonRead('meta/config.json')
        config['version'] = versionString
        jsonio.jsonWrite(config, 'meta/config.json')

    except Exception as e:
        raise apexception.JSONError(f"Setting Config Version Tag Failed @ Read/Write File: {e}")


def setPackageVersion(versionString: str):
    """ A function that simultaneously updates all version tags in the package. Accepts a version string tag."""
    try:
        version = Version(versionTag=versionString)
        setConfigVersion(version=version)
        setInitVersion(version=version)
        setVersionLock(version=version)

    except Exception as e:
        raise apexception.VersionError(f"Setting Package Version Tag Failed: {e}")


def checkInternalVersion():
    """ A function that checks if configmap.json and versionlock.txt have the same version tags. Returns a bool"""
    return True if (getConfigVersion() == getVersionLock()) else False


# Simple script to modify version number across the codebase.
# if __name__ == "__main__":
#     setPackageVersion("0.4.0")
