"""
Module for Google Cloud Client Library service interfaces.

Implements the classes:\n
- ``Drive`` for Google Drive.\n
- ``CloudStorage`` for Google Cloud Storage.\n
- ``FireStore`` for Cloud FireStore.\n
- ``FirebaseStorage`` for Firebase Cloud Storage.\n

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import os
import shutil
import pathlib

import apgis.apexception as apexception
from apgis.apconfig import Config

import typing
pathString = typing.Union[str, pathlib.Path]

CONFIG = Config()


class DrivePath:
    """
    *Class for a string-like object that represent a Google Drive path.*

    **Class Attributes:**\n
    - ``root``:         A string with the value "root".
    - ``path``:         A string representing the directory path to the path from the root to the file.
    - ``file``:         A string representing the filename without the extension.
    - ``type``:         A string representing the file extension/type.

    - ``pathDirs``:     A list representing the directories in the path attribute.
    - ``filename``:     A string representing the full filename including its extension.

    - ``drivepath``:    A path that represents the full drivepath.

    Simple path class module for a path string that is parsed with the following RegEx pattern:\n
    ``(root)/([\\sa-zA-Z0-9-/._]*)/([a-zA-Z0-9-_]*).([a-zA-Z]*)``\n

    Objects of this class are used for simple path parsing to assist with Google Drive operations.
    """

    def __init__(self, drivepath: str):
        """ **Constructor Method**\n
        Yields a ``DrivePath`` object.

        *Parses a raw path string into a format usable for Google Drive Operations.*\n

        Args:
            drivepath:  The string to parse into a DrivePath.
        Raises:
            DriveError:     Occurs if the DrivePath construction fails at regex parsing.
            AttributeError: Occurs if the attribute generation fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising a DrivePath object:*\n
        ``>> drivePath = DrivePath(drivepath="root/sampleDir/sample.txt")``
        """
        import re

        try:
            parameters = re.search(r"(root)/([\sa-zA-Z0-9-/._]*)/([a-zA-Z0-9-_]*).([a-zA-Z]*)", drivepath)
            if not parameters:
                raise apexception.DriveError("No Regex Match")

        except Exception as e:
            raise apexception.DriveError(f"Version Construction Failed @ Regex Matching : {e}")

        try:
            self.root, self.path, self.file, self.type = parameters.group(1, 2, 3, 4)
            self.pathDirs = self.path.split("/")
            self.filename = f"{self.file}.{self.type}"

        except Exception as e:
            raise AttributeError

    @property
    def drivepath(self) -> str:
        """ The full DrivePath string: *root/path/file.type* """
        return f"{self.root}/{self.path}/{self.file}.{self.type}"

    @staticmethod
    def generateExportPath(filename: str):
        """ *A staticmethod that generates a drivepath for files.*

        Only allows GeoTIFF files with a valid AP Asset ID.

        Args:
            filename:       A filename that represents the AP Asset ID.
        Returns:
            DrivePath:      A drivepath string suitable for the AP Asset ID
        Raises:
            TypeError:      Occurs if the filename is not a str.
            ValueError:     Occurs if non-GeoTIFF files are passed.
            DriveError:     Occurs if DrivePath generation fails.

        Examples:
            Some example uses of this staticmethod are:\n
        *Generating a drivepath for an Asset:*\n
        ``>> drivepath = gdrive.genDrivePath("APX000-01-L2A-2020-01-01")``
        """
        # TODO: Implement as Asset ID property
        monthstring = ["0", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        if not isinstance(filename, str):
            raise TypeError

        name = filename.split("-")
        if not name[-1].endswith(".tif"):
            raise ValueError

        try:
            year, month = name[3], int(name[4])
            drivepath = f"root/Test Collections/{year}/{month}.{monthstring[month]}/{filename}"
            drivepath = DrivePath(drivepath=drivepath)

            return drivepath

        except Exception as e:
            raise apexception.DriveError(e)


class Drive:
    """
    *Class for Google Drive client interface.*

    **Class Methods:**\n
    - ``traverseDrive:``    A method that traverses through a drivepath
    - ``checkFile:``        A method that checks for the existence of a file
    - ``downloadFile:``     A method that downloads a file

    **Class Attributes:**\n
    - ``drive:``            The Google Drive session instance.

    Initialises a Google Drive session using the pyDrive wrapper library.
    Allows basic file I/O and file existence testing. Authentication is done
    by remote key retrieval from Firebase Cloud Storage and disposal.
    """

    def __init__(self):
        """ **Constructor Method**\n
        Yields a ``Drive`` object.

        *Creates a Google Drive client using the PyDrive GSuite library*

        A Google Drive client is initialised to access the Google Drive of
        the *developer.1@antpod.io* account.\n

        The Google Drive Access Keys and Settings file for the PyDrive library
        are fetched from a Firebase Cloud Storage bucket and then deleted upon
        initialization.\n

        Raises:
            FirebaseError:  Occurs if the Firebase pull fails.
            DriveError:     Occurs if the Google Drive Authentication fails.
            EnvironmentError:   Occurs if the cleanup or directory change fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising a Drive object:*\n
        ``>> gdrive = Drive()``

        Notes:
            A drivepath is an inferred string format that represents the path to a file in Google Drive.
        Always begins with 'root' and follows the format:\n
        ``root``/``folder1``/``folder2``/``filename``.``extension``\n
        DrivePath is implemented as a class in the same module and parses and verifies the validity of paths.

        References:
            *PyDrive wrapper documentation for Google Drive Python Client Library:*
        https://pythonhosted.org/PyDrive/quickstart.html
        """
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive

        try:
            fStorage = FirebaseStorage(bucket="antpod-apgis")
            fStorage.downloadFolder(remoteFolder="gdrive-auth", localFolder="driveKeys")
            fStorage.closeApp()

        except Exception as e:
            raise apexception.FirebaseError(f"Google Drive Initialisation Failed @ Firebase Pull: {e}")

        try:
            currentPath = os.path.dirname(os.path.realpath(__file__))
            print(currentPath)
            os.chdir(os.path.join(currentPath, "driveKeys/gdrive-auth"))

        except Exception as e:
            raise EnvironmentError(f"Google Drive Initialisation Failed @ Directory Change: {e}")

        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            self.driveClient = GoogleDrive(gauth)

        except Exception as e:
            raise apexception.DriveError(f"Google Drive Initialisation Failed @ Google Drive Auth: {e}")

        try:
            os.chdir(currentPath)
            shutil.rmtree(os.path.join(currentPath, "driveKeys"))

        except Exception as e:
            raise EnvironmentError(f"Google Drive Initialisation Succeeded but cleanup failed: {e}")

    def traverseDrive(self, drivepath: DrivePath) -> list:
        """ *A method that traverses through a given drivepath from the root of the Drive.*

        Args:
            drivepath:  A DrivePath that represents the path to a file in Google Drive.
        Returns:
            list:       A list of file objects in the final folder of the drivepath.
        Raises:
            DriveError: Occurs if the Drive traversal fails.

        Examples:
            Some example uses of this method are:\n
        *Traversing a drivepath:*\n
        ``>> gdrive = Drive()``\n
        ``>> fileList = gdrive.traversePath("root/testfolder/testfile.txt")``
        """
        try:
            folder = {}
            fileList = self.driveClient.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

            for pathDir in drivepath.pathDirs:
                for file in fileList:
                    if file['title'] == pathDir:
                        folder = file
                if folder:
                    folderID = folder['id']
                    fileList = self.driveClient.ListFile({'q': f"'{folderID}' in parents and trashed=false"}).GetList()
                else:
                    raise apexception.DriveError

            return fileList

        except Exception as e:
            raise apexception.DriveError(f"Google Drive Path Traversal Failed @ Runtime: {e}")

    def checkFile(self, drivepath: DrivePath) -> bool:
        """ *A method that checks whether a given a file exists given its drivepath.*

        Args:
            drivepath:  A DrivePath that represents the path to a file in Google Drive.
        Returns:
            bool:       A bool representing whether a file exists or not.
        Raises:
            DriveError: Occurs if the file check runtime fails.

        Examples:
            Some example uses of this method are:\n
        *Checking for a file:*\n
        ``>> gdrive = Drive()``\n
        ``>> fileCheck = gdrive.checkFile("root/testfolder/testfile.txt")``
        """
        try:
            fileList = self.traverseDrive(drivepath=drivepath)
            for file in fileList:
                if file['title'] == drivepath.filename:
                    return True

            return False

        except Exception as e:
            raise apexception.DriveError(f"Google Drive File Check Failed @ Runtime: {e}")

    def downloadFile(self, drivepath: DrivePath, downloadPath: pathString) -> None:
        """ *A method that downloads a specified file from Google Drive into the current directory.*

        Args:
            drivepath:      A DrivePath that represents the path to a file in Google Drive.
            downloadPath:   A string that represents the download path.
        Raises:
            FileNotFoundError:  Occurs if the file was not found at drivepath.
            DriveError:     Occurs if the download runtime failed.

        Examples:
            Some example uses of this method are:\n
        *Downloading a file:*\n
        ``>> gdrive = Drive()``\n
        ``>> gdrive.getFile("root/testfolder/testfile.txt")``
        """
        try:
            image = {}
            fileList = self.traverseDrive(drivepath=drivepath)
            for file in fileList:
                if file['title'] == drivepath.filename:
                    image = file
                    break
        except Exception as e:
            raise apexception.DriveError

        if image == {}:
            raise FileNotFoundError(f"Google Drive File Retrieval Failed @ File discovery: file was not found")

        try:
            currentDir = os.getcwd()
            os.chdir(os.path.join(currentDir, downloadPath))

            image.GetContentFile(image['title'])

            os.chdir(currentDir)

        except Exception as e:
            raise apexception.DriveError(f"Google Drive File Retrieval Failed @ Download runtime: {e}")


class CloudStorage:
    """ **Not Currently Implemented.**

    ``CloudStorage`` is not currently not implemented.\n
    This namespace is reserved for future use.
    """
    pass


class FireStore:
    """ **Not Currently Implemented.**

    ``FireStore`` is not currently not implemented.\n
    This namespace is reserved for future use.
    """
    pass


class FirebaseStorage:
    """
    *Class for Firebase Cloud Storage client interface.*

    **Class Methods:**\n
    - ``closeApp:``         A method that closes the Firebase app instance gracefully.
    - ``uploadBlob:``       A method that uploads a blob into the app bucket.
    - ``downloadBlob:``     A method that downloads a blob from the app bucket.
    - ``listBlobs:``        A method that returns a list of all blobs from the app bucket.
    - ``downloadFolder:``   A method that downloads all blobs from a folder in the app bucket.

    **Class Attributes:**\n
    - ``app:``      The Firebase app instance.
    - ``bucket``    The storage bucket that has been initialised along with the app.

    Initialises a Firebase Storage session using the firebase-admin SDK.
    Allows basic file I/O and downloading of the entire bucket or a specific folder.
    Authentication is done by locally stored key in apgis/firebasekey/firebasekey.json

    ***DO NOT COMMIT THIS KEY TO VERSION CONTROL.***
    """

    def __init__(self, bucket: str = "antpod-apgis"):
        """ **Constructor Method**\n
        Yields a ``FirebaseStorage`` object.

        *Creates a Firebase Storage client using the Firebase Admin SDK*

        A Firebase App session  for the apGIS app is initialised to access
        the bucket specified in the parameter, bucket. Defaults to "antpod-apgis".\n

        Raises:
            FirebaseError:      Occurs if the Firebase initialisation fails
            FileNotFoundError:  Occurs if the Firebase credential build fails.

        Examples:
            Some example uses of this class are:\n
        *Initialising a Firebase object:*\n
        ``>> fStorage = FirebaseStorage()``

        *Initialising a Firebase object with a specific bucket ID:*\n
        ``>> fStorage = FirebaseStorage(bucket="sample-bucket")``

        References:
            *Cloud Storage for Firebase:*\n
        https://firebase.google.com/docs/storage
        """
        import firebase_admin
        from firebase_admin import credentials, storage

        try:
            firebaseCredentials = credentials.Certificate(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'meta/firebasekey.json'))

        except Exception as e:
            raise FileNotFoundError(f"Firebase Initialisation Failed @ Credential Building: {e}")

        try:
            self.app = firebase_admin.initialize_app(firebaseCredentials, CONFIG.getFirebaseConfig(bucket=bucket))
            self.bucket = storage.bucket()

        except Exception as e:
            raise apexception.FirebaseError(f"Firebase Initialisation Failed @ Firebase App Initialize: {e}")

    def closeApp(self) -> None:
        """ *A method that closes the Firebase app instance gracefully.*

        Raises:
            FirebaseError: Occurs if the app shutdown fails.

        Examples:
            Some example uses of this method are:\n
        *Shutting a Firebase app:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.closeApp()``
        """
        import firebase_admin

        try:
            firebase_admin.delete_app(self.app)

        except Exception as e:
            raise apexception.FirebaseError(f"Firebase App Shutdown Failed @ shutdown: {e}")

    def uploadBlob(self, localName: pathString, remoteName: str) -> None:
        """ *A method that uploads a blob into the app bucket.*

        Args:
            localName:      a pathString representing the file to upload
            remoteName:     a pathString representing the path to upload the file into on the bucket.
        Raises:
            FirebaseError:  Occurs if the blob upload fails.

        Examples:
            Some example uses of this method are:\n
        *Uploading a blob:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.uploadBlob(localName="sample.txt", remoteName="dir/cloudSample.txt")``
        """
        try:
            blob = self.bucket.blob(remoteName)
            blob.upload_from_filename(localName)

        except Exception as e:
            raise apexception.FirebaseError(f"Upload to Firebase Failed @ upload runtime: {e}")

    def downloadBlob(self, localName: pathString, remoteName: str) -> None:
        """ *A method that downloads a blob from the app bucket.*

        Args:
            localName:      a pathString representing the path to download the file into locally.
            remoteName:     a pathString representing the path to download from on the bucket.
        Raises:
            FirebaseError:  Occurs if the blob download fails.

        Examples:
            Some example uses of this method are:\n
        *Downloading a blob:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.downloadBlob(localName="download.txt", remoteName="dir/cloudSample.txt")``
        """
        try:
            blob = self.bucket.blob(remoteName)
            blob.download_to_filename(localName)

        except Exception as e:
            raise apexception.FirebaseError(f"Download from Firebase Failed @ upload runtime: {e}")

    def listBlobs(self, folder: str = None) -> list:
        """ *A method that returns a list of all blobs from the app bucket.*

        If folder is set, it acts the prefix match and only blobs matching this prefix are returned.
        This can emulate folder hierarchy on the cloud bucket. and hence only returns blobs from a
        specific folder.

        Args:
            folder:     The folder from which to list blobs. Defaults to None and lists all blobs in bucket.
        Returns:
            list:       A list of blob names.
        Raises:
            FirebaseError: Occurs if the blob listing fails.

        Examples:
            Some example uses of this method are:\n
        *Listing all blobs in the bucket:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.listBlobs()``

        *Listing all blobs in a folder:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.listBlobs(folder="dir")``
        """
        try:
            blobs = (self.bucket.list_blobs(prefix=folder)
                     if folder else
                     self.bucket.list_blobs())

        except Exception as e:
            raise apexception.FirebaseError(f"Listing Firebase Blobs Failed @ list collection: {e}")

        try:
            blobList = []
            for blob in blobs:
                blobList.append(blob.name)
            return blobList

        except Exception as e:
            raise apexception.FirebaseError(f"Listing Firebase Blobs Failed @ list building: {e}")

    def downloadFolder(self, remoteFolder: str = None, localFolder: pathString = None) -> None:
        """ *A method that downloads all blobs from a folder in the app bucket.*

        If remoteFolder is not set, all blobs in the bucket are downloaded into the localFolder.
        otherwise only the blobs in the specified folder are downloaded.\n
        If localFolder is not set, defaults to "/resource".

        Args:
            remoteFolder:  The folder from which to download blobs.
            localFolder:   The folder in which to download blobs.
        Raises:
            FirebaseError: Occurs if the folder download fails.

        Examples:
            Some example uses of this method are:\n
        *Downloading all blobs in the bucket:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.downloadFolder(localFolder="someDir")``

        *Downloading all blobs from a folder:*\n
        ``>> fStorage = FirebaseStorage()``\n
        ``>> fStorage.downloadFolder(remoteFolder="configResource", localFolder="configDir")``
        """
        try:
            remoteBlobList = self.listBlobs(folder=remoteFolder)
            folder = "resource" if localFolder is None else localFolder
            localDir = f"{os.path.dirname(os.path.realpath(__file__))}/{folder}"

        except Exception as e:
            raise apexception.FirebaseError(f"Downloading Firebase Folder Failed @ path setting: {e}")

        try:
            localBlobList = []
            for blob in remoteBlobList:
                filename = f"{localDir}/{blob}"
                localBlobList.append(filename)

            if not os.path.isdir(localDir):
                os.makedirs(localDir)

        except Exception as e:
            raise apexception.FirebaseError(f"Downloading Firebase Folder Failed @ local filename build: {e}")

        try:
            for local, remote in zip(localBlobList, remoteBlobList):
                if local.endswith("/"):
                    if not os.path.isdir(local):
                        os.makedirs("/".join(local.split("/")[:-1]))
                else:
                    if not os.path.isfile(local):
                        self.downloadBlob(localName=local, remoteName=remote)

        except Exception as e:
            raise apexception.FirebaseError(f"Downloading Firebase Folder Failed @ download runtime: {e}")
