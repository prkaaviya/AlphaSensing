# apGIS  
*Author*: **AntPod Designs Pvt Ltd**  
*Latest Release*: ** releaseName [vTag]**  
*Python 3.8*   

**A python package that represents the primary codebase for all GIS Applications 
and Containers that run on the AntPod platform.**   

### Contributors: 
- Manish Meganathan
- Kaaviya Ramkumar  

### Contents
- [1. Google Earth Engine](#1-google-earth-engine)
- [2. Project Hierarchy & Structure](#2-project-hierarchy--structure)
- [3. Release Channels](#3-release-channels)
- [4. Version Control](#4-version-control)
- [5. Code Styling](#5-code-styling)
- [6. Using the Package](#6-using-the-package)
- [7. ConfigMap Specification](#7-config-specifications)
- [8. Format Specifications](#8-format-specifications)
- [9. Package Dependencies](#9-package-dependencies)
- [10. Release History](#10-release-history)
- [11. Changelog](#11-changelog)
- [12. Future Development](#12-future-development)  

*Contents were last updated on: August 30, 2020*


## 1. Google Earth Engine

This codebase is primarily built around the **Google Earth Engine Python API.**   
Documentation for how this codebase uses GEE for Geo-Spatial Analysis listed here 

### 1.1 Introduction to Earth Engine. 
Google Earth Engine is a planetary-scale platform for Earth science data & analysis. 
It combines a multi-petabyte catalog of satellite imagery and geospatial datasets with planetary-scale analysis 
capabilities and makes it available for scientists, researchers, and developers to detect changes, map trends, 
and quantify differences on the Earth's surface.

Earth Engine's public data archive includes more than forty years of historical imagery and scientific datasets, 
updated and expanded daily. 
Explore the [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/).

For more information refer to the Google Earth Engine [website](https://earthengine.google.com/).

### 1.2 Programming with the Earth Engine Python API.
This codebase works on the Earth Engine Python API which is an open source project available on GitHub.
For more information about other ways to use Earth Engine, check [here](https://developers.google.com/earth-engine).

For setting up Earth Engine on your local system. 
Check [here](https://developers.google.com/earth-engine/guides/python_install).  
An anaconda/pipenv installation is recommended to maintain a virtual environment 
while working with this codebase and it's dependencies.   

A clear understanding of [Client vs. Server](https://developers.google.com/earth-engine/guides/client_server) 
analogies and [Deferred Execution](https://developers.google.com/earth-engine/guides/deferred_execution) logic 
is important to work with the Earth Engine API.   
For information about programming with the Earth Engine API. 
Check [here](https://developers.google.com/earth-engine/guides/concepts_overview).  

### 1.3 Earth Engine Session Management
The Earth Engine API requires the client libraries to be initialised with credentials that have been authenticated 
to use Earth Engine.   

Several methods are available to pass these credentials into the client library such as:
- **OAuth2 Authentication Flow.**.
This requires the user signing in to be verified and authenticated to use Earth Engine.
- **Project ID Authentication**.
This requires a GCP Project that has been verified and allowed access to the commercial license of Earth Engine.
- **Service Account Credentials**.
This requires a Service Account Key to be generated from either a personal or GCP account and needs to be passed 
to the client library to initialise the session.  

This codebase abstracts this session management by unifying this initialization interface into a single function.
The eeInitialize() function accepts a flag to enable the use of an internal config which is facilitated by an
OAuth flow that requires a signup if the credentials don't already exist.   
This is recommended only for development testbenches and when a Google Drive Export Runtime is required.  
If no flag are passed, the Service Account credentials are pulled from a Firebase Cloud Storage bucket and used
to authenticate using the service account certificate mode. The keys are immediately deleted upon a successful 
initialization.


## 2. Project Hierarchy & Structure

The documentation for all the repository directories and package details are listed here.

### 2.1 Repository Tree
The repository is maintained in a file tree as described below. Wildcard characters are used to represent multiple 
files of a certain data type.
```
apGIS
|-- apgis/
    |-- __init__.py
    |-- apcloud.py
    |-- apconfig.py
    |-- apconversion.py
    |-- apdate.py
    |-- apexception.py
    |-- apfield.py
    |-- apgeojson.py
    |-- apjsonio.py
    |-- apresource.py
    |-- aprequestlist.py
    |-- apversion.py
    |-- geebase.py
    |-- geeexport.py
    |-- geeindex.py
    |-- geemask.py
    |-- geespatial.py
    |-- geetemporal.py
    |-- geevisual.py
    |-- gisgeodf.py
    |-- gisraster.py
    |-- meta/
        |-- config.json
        |-- versionlock.txt
        |-- $firebasekey.json
    |-- tests/
        |-- test_*.py
        |-- testdata/
            |-- testdata.json
            |-- testfiles.*
|-- README.md
|-- DEPENDANCIES.txt
|-- LICENSE.txt
```

### 2.2 Repository Directories
The repository contains the following directories:

#### 2.2.1 apgis  
This is the package root directory. Contains all the subpackages, tests and version profiles within it.  

- **apcloud.py**   
A module that implements the classes *Drive* and *FirebaseStorage* which each interface with their namesake
services and provide and authenticated object for operations with that service.  
    > **Project v0.5** proposes adding expanded functionality for Firebase and adding classes for Cloud Storage  
    and Firestore into this Class.  
 
- **apconfig.py**   
A module that implements the class *Config* which interfaces with a configmap.json file to provide 
Satellite and Sensor ID information along with any other data required by the codebase.    
    > **Project v0.5** proposes integrating additional firebase configuration and function mapping into this Class.      
 
- **apconversion.py**   
A module for a library of top-level functions that convert units between each other
and also contain methods to convert multiple file formats.    
    > **Project v0.5** proposes integration with the units module and adding conversions for more units 
    additional firebase configuration and function mapping into this Class.
    
- **apdate.py**  
A module that implements the class *Date* which creates a date representation object and wraps around an Earth
Engine Date Object. Additionally contains functionality to represent dates in multiple accepted standards.  
    > **Project v0.5** proposes integrating a datestring validation subtype and more  temporal scaling options.
    
- **apexception.py**   
A module for a library of custom exceptions that are used all over the codebase.   
    > **Project v0.5** proposes more fine-grained exception classes.
    
- **apfield.py**  
A module that implements the class *Field* which creates an object that takes a GeoJSON object and creates a
administrative object that represent a farm or field. 
    > **Project v0.5** proposes integrating more solid geocoding and a formalized schema for the user
    GeoJSON validation subtype and more temporal scaling options.

- **apgeojson.py**  
A module that implements the class *GeoJSON* which reads and parses a GeoJSON file or dictionary into an object 
that holds all its properties and geometry data. 
    > **Project v0.5** proposes supporting multigeometry and multi-feature geojson files as well. 
    
- **apjsonio.py**  
A module for a library of top-level functions to read, parse and write JSON and related formats such as GeoJSON 
and TopoJSON files.
    > **Project v0.5** proposes implementing support for TopoJSON IO. 
    
- **apresource.py**  
A module that implements the class *Resource* which creates an object that contains a GeoJSON and a Field object
that collectively are used for request handling. Allows remote resource fetching for GeoJSON files.
    > **Project v0.5** proposes unifying with apfield if possible and exploring added features.
       
- **aprequestlist.py**  
A module that implements the class *RequestList* which validates a list of request products and provides an interface
that gives access to some commonly used features of the Export library.   
    > **Project v0.5** proposes expanded functionality such as including a GeoJSON object and absorbing its date
    request fields from it.

- **apversion.py**  
A module that implements the class *Version* that parses a string representing a package/subpackage
version tag. Also contains a library utility functions to set/ verify package internal consistency.
    > **Project v0.5** proposes more robust version locking.
    
- **geebase.py**  
A module for a library of top-level functions for basic Earth Engine functions that acquire, verify, repair, 
extract and mosaic Image and ImageCollections.
    > **Project v0.5** proposes support for SRTM and ALOS satellite IDs
    
- **geeexport.py**  
A module that implements a static class *Export* that implements methods that create export tasks on the Earth 
Engine batch system.
    > **Project v0.5** proposes addition of more functionality to other sources and more robust cloud exports

- **geeindex.py**  
A module for a library of top-level functions that implement methods for bandmath operations.
    > **Project v0.5** proposes addition of bandmath tools for other satellites

- **geemask.py**  
A module for a library of top-level functions that implement methods for masking operations.
    > **Project v0.5** proposes implementing Cloud Masking algorithms and more options for range masking

- **geespatial.py**   
A module for a library of top-level functions that implement methods for Geospatial manipulations.
    > **Project v0.5** proposes any code additions as contributions towards expanding its functionality 
    and implement altitude contour mapping.

- **geetemporal.py**  
A module for a library of top-level functions that implement methods for Temporal manipulation and generation.
    > **Project v0.5** proposes expanding datestring functionality
      
- **geevisual.py**  
A module that has functions for basic visualization tools imported from geemap.
    > **Project v0.5** proposes addition of expanded functionality like map resetting, split maps, etc.
   
- **tests/**  
A unittest library that contains modules to test each corresponding module in the apgis package. Also contains a 
directory testdata which holds resources that are used to perform unit tests.
    > **Project v0.5** proposes making testdata remote and integrating testconfig with Config and writing
    more comprehensive tests.  

- **meta/**  
A directory that contains the package configuration files. This includes a config.json file and a versionlock.txt
that are used as configuration data for the codebase and the version locking file respectively.   
Additionally the firebase service account key is also expected in this directory as a file called called
firebasekey.json. However this file is not committed to VCS.
    > **Project v0.5** proposes implementing secret manager or a more unified auth interface.

#### 2.2.2 Other Files

- **DEPENDANCIES.txt**    
A requirements.txt style file listing all the core external packages used by the package.

- **LICENSE.txt**    
A closed source license for the package.


## 3. Release Channels
Information about the release channels of the package are listed here. For information about the latest Release.
Refer to the [Changelog](#11-changelog) section.  

### 3.1 Persistent Branches:

**Master :: origin/master** branch to hold the  ***most stable and reliable*** build of the codebase.
This is the branch used for production deployments.
- *branch from and merge back, if*:
    - a quick hotfix is to be performed. Branch to a *hotfix-* branch and merge back after testing
    - a test runtime needs to be performed or modified. Branch to a *test-prod-* branch and if there are any. 
    changes, they should be merged as a hotfix.
        
**Stable :: origin/stable** branch to hold the ***latest stable*** build of the codebase.
This is the branch used for preproduction testing before rolling it out to production.
- *merges up, if*:
    - this branch has been tested to work with all microservice dependants.
    - AND all code and release documentation must be fully completed.
- *branch from and merge back, if*:
    - a quick hotfix is to be performed. Branch to a *hotfix-* branch and merge back after testing
    - a test runtime needs to be performed or modified. Branch to a *test-stable-* branch and merge changes.

**Stage :: origin/stage** branch to hold a ***pretty stable*** build of the codebase.
This is the branch used for preproduction staging and contains the latest working features.
- *merges up, if*:
    - this branch has been tested and code reviewed.
    - AND critical documentation must be completed.
- *branch from and merge back, if*:
    - a quick hotfix is to be performed. Branch to a *hotfix-* branch and merge back after testing
    - a comprehensive bugfix is be performed. Branch to a *bugfix-* branch and merge back after testing.
    - a test runtime needs to be performed or modified. Branch to a *test-stage-* branch and merge changes.

**Dev :: origin/dev** branch to hold a ***functional*** build of the codebase.
This is the branch used for all active development and contains the features that are under development
- *merges up, if*:
    - this branch has fully functional features that have been tested for staging.
    - AND contains unit tests for any new additions.
- *branch from and merge back, if*:
    - a quick hotfix is to be performed. Branch to a *hotfix-* branch and merge back after testing
    - a comprehensive bugfix is be performed. Branch to a *bugfix-* branch and merge back after testing.
    - a test runtime needs to be performed or modified. Branch to a *test-dev-* branch and merge changes.
    - a feature addition is to be done. Branch to a *canary-* or *feature-* branch and merge back.
    - an experimental, potentially code breaking features needs to be worked on. Branch a *probe-* branch 
    and discard after use. Any new features can be implemented by branching as *canary-* or *feature-*

### 3.2 Temporary Branches:

##### **Canary**
*canary-\<project name\>* branches are for more comprehensive feature additions.  
Branch these from *origin/dev*

##### **Feature**
*feature-\<feature description\>* branches are for targeted and specific feature additions.  
Branch these from *origin/dev* or an existing *canary-* branch.

##### **Probe**
*probe-\<description\>* branches are for more experimental, code breaking feature tests.  
Branch these from *origin/dev*

##### **Test**
*test-\<branch name\>-\<test description\>* branches are for test runtimes of specific branches 
Branch these from any persistent branch.

##### **Bugfix**
*bugfix-\<bug description\>* branches are for comprehensive bug fixes.
Branch these from *origin/dev* or *origin/stage*

##### **Hotfix**
*hotfix-\<bug description\>* branches are for targeted and specific bug fixes.
Branch these from any persistent branch.

    
## 4. Version Control
Version Control Guidelines are specified here.

A guide to best practices for Git and Github:  
https://www.datree.io/resources/github-best-practices 

Commit messages must be descriptive contain description of changes for each file and/or directory.
The commit header must contain a short description of the changes for a given commit.
For more information, read:   
https://chris.beams.io/posts/git-commit/


## 5. Code Styling
**The codebase is compliant with the Google Styling Guide for Python.**   
It is recommended that all future development is compliant with this styling guide. 

The Google Python Style Guide can be found [here](https://google.github.io/styleguide/pyguide.html).

Optionally the entire package can be run over the [YAPF](https://github.com/google/yapf) style formatter
during development to maintain style consistency.


## 6. Using the Package
Currently unavailable. Check back later.    
A section that describes the usage of this codebase from a testbench perspective will be available here soon.   
## 7. Config Specifications
Currently unavailable. Check back later.  
A section that describes the specifications of the config.json file and its contents. Proposed addition 
for Project v0.5. Will contain information regarding both config and testdata files.  
## 8. Format Specifications
Currently unavailable. Check back later.   
A section that describes specifications for Auth tokens and Asset ID conventions.


## 9. Package Dependencies
**References to all the primary dependancies of this package**  

### 9.1 Earth Engine
[earthengine-api](https://github.com/google/earthengine-api) 0.1.232  
[geemap](https://github.com/giswqs/geemap) 0.7.11

### 9.2 Google Cloud Services
[PyDrive](https://pythonhosted.org/PyDrive/) 1.3.1  
[firebase-admin](https://firebase.google.com/docs/reference/admin/python) 4.3.0

### 9.3 Python GIS
[geopandas](https://geopandas.org/install.html)    
[rasterio](https://rasterio.readthedocs.io/en/latest/)   
[rasterstats](https://pythonhosted.org/rasterstats/)   
[shapely](https://pypi.org/project/Shapely/)     

### 9.4 JSON5
[json5](https://json5.org/) 0.9.5  
[geojson](https://geojson.org/) 2.5.0


## 10. Release History
Currently unavailable. Check back later.   
A section that describes the release history of the package.


## 11. Changelog
**The changelog contains all the changes made to the codebase from its inception as listed below.**  
Contact the admin for access to legacy codebase files.

### v0.4
- **v0.4.0**
    - codebase reseeded @ apGIS.
    - rebuilt package with new structure and features.
    - no more subpackages. all modules are under a single package called *apgis*.
    - unified earth engine initialization implemented in *\_\_init\_\_.py.*
    - new module *apexception.py* to implement custom exception classes.
    - entire test suite has been reimplemented and optimized.
    - *gisconversion* has been reimplemented into the following:
        - *apjsonio* for all file read/write operations and built framework to support TopoJSON files in the future.
        - *apconversion.py* new file implements unit conversion library.
    - Class modules:
        - class *User* has been reimplemented into class *Field* in a file *apfield.py*, now contains 
        geocoded address information from the Nominatim open source geocoder.
        - class *ConfigMap* has been reimplemented as *Config*. Now validates package internal 
        consistency with versioning. 
        - class *Date* and class *RequestList* implemented in new files *apdate.py* and *aprequestlist.py*
        - class *GDrive* has been deprecated and reimplemented as *Drive* in *apcloud.py*
        - new classes:
            - new class *GeoJSON* to parse and store GeoJSON file attributes implemented in *apgeojson.py*
            - new class *Version* to parse semantic version tags implemented in *apversion.py* along with 
            new top-level functions to utilize it and set package version numbers. 
            - new class *FirebaseStorage* to create an authenticated firebase app instance to pull credentials
            and demo resources from Cloud Storage implemented in *apcloud.py*
    - GEE modules:
        - *geemain* renamed back to *geebase.py*.
        - class *Temporal*, *Index*, *Mask* and *Spatial* reimplemented as a libraries of top-level functions 
        in their respective modules.
        - changed function names in *geeexport.py* and fixed and reimplemented export preprocessing.
        - *geevisual.py* has been updated to match the package standard. still requires more feature addition.
    - GIS modules:
        - *gisgeodf* reimplemented as top level library
        - *gisraster* has fine grained exception handling and some optimized iteration for assignMean.
       
### v0.3
- **v0.3.0**
    - fully re-implemented codebase in compliance with styling guide. documentation expanded and format unified.
    - reimplementation involves restructuring all modules in static classes.
    - package build refactoring. services and scripts directory removed to be implemented as a new repository.
    - unified all documentation into the README.md
    - new classes added to apClass subpackage.
        - sensorMap renamed to ConfigMap.
        - Landsat-8 Surface Reflectance SatID renamed to L8SR.
        - Date class to handle all date operation added.
        - RequestList class to handle all export library requests added.
        - User class expanded and reimplemented.
        - GDrive class added from utilgdrive library. Now initializes a Google Drive session object.
        - Session class added from utilsession library. Intended for testbench usage only. 
    - apGEE reimplemented
        - geebase renamed to geemain.py
        - geeexport now contains a class Export that handles all export task for Image and ImageCollections. Heavily
        optimized and now works with RequestList class to handle images and collections independently.
        - geeindex now contains a class Index that has a unified bandmath function that makes calls to functions calls
        to pure server side algorithms that can now be used for collection map operations.
        - geemask added with a class Mask that contains operation that involve image and collection masking. groundwork
        for cloud-masking and other related features.
        - geespatial added with a class Spatial that has the area calculation and will soon hold all other geospatial
        manipulations.
        - geetemporal added with class Temporal that contains temporal manipulation functions.
    - apGIS reimplemented
        - antpodGIS deprecated in favour of new modules
        - gisGeoDF added with a static class GeoDF that implements GeoDataFrame functionality.
        - gisRaster added with a class Raster that initializes a Raster object with methods to manipulate it.
        - gisconversion added from utilconversion library for file I/O.
    - test UnitTest Suite created
        - unit test library for all modules added.
        - testconfig.json created with all testing data.
         
### v0.2
- **v0.2.7**
    - antpodGIS re-implemented in smaller more specific modules. gisGeoDataFrame and gisRaster.
    - styling documentation added.
- **v0.2.6**
    - sensorMap re-implemented in it's own module.
    - microservice framework updates.
- **v0.2.5**
    - codebase reseeded @ **GIS** Repository.
    - stabilized codebase and added functionality to support use with microservices
    - unified subpackage versioning.
    - User class re-implemented in it's own module.
- **v0.2.4**
    - pyDrive integration into the codebase.
- **v0.2.3**
    - antpodGIS optimization and export functionality.
- **v0.2.2**
    - antpodGIS grid overlay functions added.
    - antpodGIS updated to lay groundwork for using the User class.
    - date jumping and datestring validation functions have been added.
- **v0.2.1**
    - all satellite and sensor moved to a sensormap.json file
    - interfacing with configmap.json functions added.
    - codebase updated to utilize configmap.json
- **v0.2.0**
    - Landsat-8 support added.
    - Sentinel-2 verification functions have been unified.
    - Sentinel-2 indices have been updated to reflect new functionality and have new documentation.
    - MSI and NDII bandmath functions deleted.
    - date functions have been unified.
    - groundwork for a potential Datestring class.
    - export library expanded for Landsat-8

### v0.1
- **v0.1.7**
    - User class added to \_\_init__.py
    - major overhaul to antpodGIS including documentation and optimization.
    - collection filtering is made end inclusive.
    - conversions.py optimized.
    - flipped pixel-masking functionality added.
    - resource data extracted from .antpodConfig.txt
- **v0.1.6**
    - documentation for all indices updated.
    - deprecated ARI, MSI and NDII.
    - AVI, NPCRI, NDGI, BSI and SI bandmath functions added.
    - metadata repair functions for Sentinel-2 added.
    - mosaic image generation function added.
- **v0.1.5**
    - initial GitHub seed as the *EyesInTheSky* Repository, 
    previously archived @ **legacyGIS**
- **v0.1.2**
    - antpodGIS module is merged into codebase.
- **v0.1.1**
    - session.py module is added 
    - geebase.py, geeindex.py, geevisual.py and geeexport.py are added.
- **v0.1.0**
    - entire codebase reworked into a proper package structure.

### v0.0
- **v0.0.6**
    - export functionality to Google Drive added
    - conversions.py module is added
- **v0.0.5**
    - GNDVI, ARVI, SAVI, ARI, MCARI, LeafNDWI, BodyNDWI, MSI, NDII, NBR, NDCI, NDSI and PSRI bandmath functions added.
    - visualization parameters and tools derived from geemap added.
- **v0.0.4** 
    - pixel masking and range masking functions added.  
- **v0.0.3** 
    - NDVI, EVI bandmath functions added.  
- **v0.0.2**   
    - simple image manipulation, handling and extraction functions added.  
    - temporal and spatial filtering functions added.
- **v0.0.1**  
    - initial experimental codebase on the Earth Engine Code Editor.  


## 12. Future Development
**The development roadmap for the codebase is listed here.**    

Named projects have a structured rollout plan. Functionality that depends on a particular development 
rollout are listed under a separate section and will be added into project at an appropriate time.  
  
(Note: This is not a strict and fixed rollout plan. Any functionality may be prioritised or added during development 
while the codebase is in a pre-release phase. Refer to the [Changelog](#11-changelog) for information about 
the latest release.)

### Project Pluto (v0.5)
- google drive library expansion.
- unified session interface for GISApps and testbenches
- expanding functionality of object classes.
- cloud masking algorithm
- contour mapping functionality
- geospatial manipulation features
- google cloud framework.
- improving unittests and unifying testconfig into ConfigMap
- new proposed type-classes
    - AP Asset ID to identify export assets.
    - datestring to format ISO dateStrings.
- expanded file I/O functionality.
- topojson support.
- multi feature support in GeoJSON.

### Other Development Proposals
Currently all proposals have been assigned to **Project v0.4** 
