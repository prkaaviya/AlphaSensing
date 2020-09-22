"""
Module for geospatial manipulation functions.

Library of top-level functions to manipulate geospatial data on Earth Engine.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import ee

import apgis.apexception as exception
import apgis.apconversion as conversion
from apgis.apfield import Field
import apgis.geemask


# noinspection PyUnresolvedReferences
def getArea(geometry: ee.Geometry,
            unit: str = "SQM") -> float:
    """ *A function that calculates the area of an ee.Geometry.*

    The function calculates area with a 5% error margin.
    Area is calculated in unit of choice. Defaults to SQM.\n
    Options for units are:\n
    - Square Kilometres - "SQKM".
    - Square Metres - "SQM".
    - Square Feet - "SQFT".
    - Square Yards - "SQYARD".
    - Square Miles - "SQMILE".
    - Hectares - "HA".
    - Acres - "ACRE".

    Args:
        geometry:       The geometry for which to find area.
        unit:       The unit in which to calculate area. Defaults to sq.KM.
    Returns:
        float:  The area of the geometry as a float.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError:     Occurs f area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating area in Square Metres:*\n
    ``>> area = getArea(geometry=geo)``

    *Calculating area in Hectares:*\n
    ``>> area = getArea(geometry=geo, unit="HA")``
    """
    units = ["SQKM", "SQM", "SQFT", "SQMILE", "SQYARD", "HA", "ACRE"]

    if not isinstance(geometry, ee.Geometry):
        raise TypeError("Area Calculation Failed @ type check: geometry must be an ee.Geometry")

    if unit not in units:
        raise ValueError(f"Area Calculation Failed @ unit check: {unit} not supported")

    try:
        Area = geometry.area(5).getInfo()
        Area = conversion.areaUnitConversion(Area, convertFrom="SQM", convertTo=unit)
        Area = round(Area, 3)

        return Area

    except Exception as e:
        raise exception.EERuntimeError(f"Area Calculation Failed @ Runtime: {e}")


def genBufferGeo(field: Field, buffer: int) -> ee.Geometry:
    """ *A function that sets the buffer distance for apfield.Field object.*

    Args:
        field:      A Field object.
        buffer:     An integer specifying the distance (default in meters) of the buffering.
    Returns:
        ee.Geometry:    The geometry of the Field object after buffering.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating buffer:*\n
    ``>> geoBuffered = setBufferGeo(field=field, buffer=100)``
    """
    try:
        d1 = ee.Geometry.Point(coords=field.eeROI.centroid().coordinates())
        # noinspection PyUnresolvedReferences
        d2 = ee.Geometry.Point(coords=ee.List(field.eeROI.coordinates().get(0)).get(0))
        bufferVal = d1.distance(d2).add(buffer)
        bufferGeo = ee.Geometry.Point(coords=field.centroid).buffer(bufferVal)
        return bufferGeo

    except Exception as e:
        raise exception.EERuntimeError(f"Buffer Geometry Generation Failed @ Runtime: {e}")


def renderNDMI(ndmi: ee.Image) -> ee.Image:
    """ *A function that returns the render image of an NDMI ee.Image.*

    Args:
        ndmi:       An image containing calculated NDMI values.
    Returns:
        ee.Image:   The render image for raw NDMI values.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> renderNDMI = renderNDMI(ndmi=ndmiImage)``
    """
    try:
        # noinspection PyUnresolvedReferences
        ndmiRounded = ndmi.toFloat().multiply(10).toInt()
        ndmiFocal = ndmiRounded.toFloat().focal_median(kernelType="square", radius=5)
        ndmiRender = apgis.mask.generateRangeMask(image=ndmiFocal, low=2, high=10)
        return ndmiRender

    except Exception as e:
        raise exception.EERuntimeError(f"NDMI Layer Render Failed @ Runtime: {e}")


def renderNDVI(ndvi: ee.Image) -> ee.Image:
    """ *A function that returns the render image of an NDVI ee.Image.*

    Keyword Args:
        ndvi:          An image containing calculated NDVI values.
    Returns:
        ee.Image:   The render image for raw NDVI values.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> renderNDVI = renderNDVI(ndvi=ndviImage)``
    """
    try:
        # noinspection PyUnresolvedReferences
        ndviRounded = ndvi.toFloat().multiply(10).toInt()
        ndviFocal = ndviRounded.toFloat().focal_median(kernelType="square", radius=5)
        ndviRender = apgis.mask.generateRangeMask(image=ndviFocal, low=0, high=10)
        return ndviRender

    except Exception as e:
        raise exception.EERuntimeError(f"NDVI Layer Render Failed @ Runtime: {e}")


def renderVector(renderImage: ee.Image) -> ee.FeatureCollection:
    """ *A function that returns the render vector of an ee.Image.*

    Args:
        renderImage:        An ee.Image.
    Returns:
        ee.FeatureCollection: The feature collection obtained from reducing an ee.Image.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> render = renderVector(renderImage=image)``
    """
    try:
        # noinspection PyUnresolvedReferences
        render = renderImage.toInt().reduceToVectors(scale=1)
        return render

    except Exception as e:
        raise exception.EERuntimeError(f"Vector Generation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def layerCoding(renderImage: ee.Image) -> ee.FeatureCollection:
    """ *A function that sets the layer code for each vector reproduced from an ee.Image.*

    Args:
        renderImage:          An ee.Image.
    Returns:
        ee.FeatureCollection: The feature collection with each feature containing a layerID.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> renderCoded = layerCoding(renderImage=ndviImage)``
    """
    try:
        renderFeature = renderVector(renderImage)
        renderCoded = renderImage.reduceRegions(collection=renderFeature,
                                                reducer=ee.Reducer.mode().setOutputs(['layerID']), scale=1)
        return renderCoded

    except Exception as e:
        raise exception.EERuntimeError(f"LayerID Set Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def mergeLayerPolygons(fCollection: ee.FeatureCollection) -> ee.FeatureCollection:
    """ *A function that merges all the features of a collection with same layerID correspondingly.*

    Args:
        fCollection:          An ee.FeatureCollection of features with property layerID.
    Returns:
        ee.FeatureCollection: The ee.FeatureCollection with features merged according to the layerID.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> featureColLayers = mergeLayerPolygons(fCollection=anyRenderLayer)``
    """
    try:
        layers = [int(float(i)) for i in fCollection.aggregate_histogram("layerID").getInfo().keys()]

        featureList = []
        for layer in layers:
            filterLayer = ee.Filter.rangeContains(field="layerID", minValue=layer, maxValue=layer)
            layerCollection = fCollection.filter(filterLayer)

            layerFeature = layerCollection.union(5).first().set({"layerID": layer})
            featureList.append(layerFeature)

        return ee.FeatureCollection(featureList)

    except Exception as e:
        raise exception.EERuntimeError(f"Polygon Layer Merge Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def accumulateRawValue(indexImage: ee.Image, field: Field) -> ee.FeatureCollection:
    """ *A function that accumulates the raw pixel values for an ee.Image representing an index.*

    Args:
        indexImage:     An image containing calculated NDVI values.
        field:      A Field object.
    Returns:
        ee.FeatureCollection: The ee.FeatureCollection with each feature corresponding to a pixel value.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:     Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> pointFeatures = accumulateRawValue(indexImage=ndviImage, field=field)``
    """
    try:
        latLon = ee.Image.pixelLonLat().reproject(crs=indexImage.projection())
        coords = latLon.select(['longitude', 'latitude']).reduceRegion(reducer=ee.Reducer.toList(),
                                                                       geometry=field.eeAOI, scale=10)

        lat = ee.List(coords.get('latitude'))
        lon = ee.List(coords.get('longitude'))
        coordinates = lon.zip(lat)

        def getFeature(latlon):
            """ A function to map through each feature of an ee.FeatureCollection that sets the coordinated of the
            same."""
            point = ee.Geometry.Point(coords=latlon)
            return ee.Feature(point)

        pointFeatures = ee.FeatureCollection(coordinates.map(getFeature))

        for index in indexImage.bandNames().getInfo():
            reduceIndexValues = ee.Reducer.first().setOutputs(outputs=[index])
            pointFeatures = indexImage.reduceRegions(collection=pointFeatures, reducer=reduceIndexValues, scale=10)

        return pointFeatures

    except Exception as e:
        raise exception.EERuntimeError(f"Raw Value Accumulation Failed @ Runtime: {e}")


def setLatLon(feature: ee.Feature) -> ee.Feature:
    """ *A function that sets the latitude and longitude value of a geometry in the property of that feature.*

    Args:
        feature:        An ee.Feature.
    Returns:
        ee.Feature: The ee.Feature that contains latitude and longitude information in its properties.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> feature = setLatLon(feature=ndviImage)``
    """
    try:
        # noinspection PyUnresolvedReferences
        latlon = feature.geometry().coordinates()
        feature = feature.set({"longitude": latlon.get(0), "latitude": latlon.get(1)})
        return feature

    except Exception as e:
        raise exception.EERuntimeError(f"Coordinate Set Failed @ Runtime: {e}")


def setArea(feature: ee.Feature) -> ee.Feature:
    """ *A function that sets the area of the feature as the property of the same.*

    Args:
        feature:        An image containing calculated NDVI values.
    Returns:
        ee.Feature: The ee.Feature that contains area information in its properties.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> featureAreaProp = setArea(feature=randomFeature)``
    """
    try:
        # noinspection PyUnresolvedReferences
        area = feature.area(5)
        feature = feature.set({"area": area})
        return feature
    except Exception as e:
        raise exception.EERuntimeError(f"Area Set Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def scoreBuilder(rawData: ee.FeatureCollection) -> ee.FeatureCollection:
    """ *A function that calculates the score of an ee.FeatureCollection in percentile.*

    Args:
        rawData:        An ee.FeatureCollection containing raw pixel values of NDVI and NDMI.
    Returns:
        ee.FeatureCollection: The ee.FeatureCollection with NDVI Score, NDVI Mean and NDMI Mean values appended to its properties.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating score:*\n
    ``>> ndviScoreCol = scoreBuilder(rawData=ndviFeatureCol)``
    """
    try:
        filterLowNDVI = ee.Filter.lte("NDVI", 0.4)
        lowCol = rawData.filter(filterLowNDVI)

        NDVIscore = lowCol.size().divide(rawData.size()).multiply(100).round()
        NDVIscore = ee.Number(100).subtract(NDVIscore)
        NDVImean = round(rawData.aggregate_mean("NDVI").getInfo(), 2)
        NDMImean = round(rawData.aggregate_mean("NDMI").getInfo(), 2)

        newRawData = rawData.set({
            "NDVI Score": NDVIscore,
            "NDVI Mean": NDVImean,
            "NDMI Mean": NDMImean
        })

        return newRawData

    except Exception as e:
        raise exception.EERuntimeError(f"Raw Score Calculation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def genCleanSZ(ndviLayerCol: ee.FeatureCollection, field: Field) -> ee.FeatureCollection:
    """ *A function that filters the lower values of layerID (which indicates unhealthy regions) in an
    ee.FeatureCollection.*

    Args:
        ndviLayerCol:       An image containing calculated NDVI values.
        field:      A Field object.
    Returns:
        ee.FeatureCollection: The ee.FeatureCollection in which each feature indicates a StressZone.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating StressZones:*\n
    ``>> cleanSZ = getCleanSZ(ndviLayerCol=ndviImage, field=field)``
    """
    try:
        filterSZ = ee.Filter.rangeContains(field="layerID", minValue=0, maxValue=3)
        szLayers = ndviLayerCol.filter(filterSZ)

        def setSZLayer(feature):
            """ A function to map through each feature of an ee.FeatureCollection that sets the layerID."""
            feature = feature.set({"layerID": 1})
            return feature

        szLayered = szLayers.map(setSZLayer)

        szImage = szLayered.reduceToImage(properties=['layerID'], reducer=ee.Reducer.first().setOutputs(['SZ']))
        cleanSZ = szImage.reduceToVectors(geometry=field.eeAOI, scale=1)  # something fishy here

        return cleanSZ

    except Exception as e:
        raise exception.EERuntimeError(f"StressZone Clean Features Generation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def areaLayers(bigSZLayers: ee.FeatureCollection) -> list:
    """ *A function that creates a list of images which contains clipped StressZone layers from an ee.FeatureCollection.*

    Args:
        bigSZLayers:        An ee.FeatureCollection containing StressZone features with large area.
    Returns:
        list:   The list of images of StressZone layers.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> clusterImageList = areaLayers(bigSZLayers=ndviSZCollection)``
    """
    try:
        bigSZFeatures = bigSZLayers.toList(bigSZLayers.size())

        # noinspection PyUnresolvedReferences
        def makeFeatureCollectionList(feature, imageList):
            """ A function to iterate through an ee.FeatureCollection to reduce its features to an image and append that
            to a list."""
            fCollection = ee.FeatureCollection([feature])
            image = fCollection.reduceToImage(['label'], ee.Reducer.first().setOutputs(['SZ'])).clip(feature)
            imageList = ee.List(imageList).add(image)
            return imageList

        clusterImageList = bigSZFeatures.iterate(makeFeatureCollectionList, ee.List([]))
        return clusterImageList

    except Exception as e:
        raise exception.EERuntimeError(f"Area Layer Generation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def fixSNIC(feature) -> ee.Feature:
    """ *A function that removes all the irrelevant properties of a feature and returns a new feature with just layerID
    and mean NDVI values.*

    Args:
        feature:        An image containing calculated NDVI values.
    Returns:
        ee.Feature: The ee.Feature with new properties set.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> featureNew = fixSNIC(feature=featureOld)``
    """
    try:
        featureOld = ee.Feature(feature)
        featureNew = ee.Feature(featureOld.geometry())

        mean = ee.Number(featureOld.get("mean"))
        layerID = mean.multiply(10).int()

        featureNew = featureNew.set({"layerID": layerID, "meanNDVI": mean})
        return featureNew

    except Exception as e:
        raise exception.EERuntimeError(f"SNIC Correction Failed @ Runtime: {e}")


def splitSZLayers(areaSZ, threshArea: int) -> ee.FeatureCollection:
    """ *A function that returns the render image for an ee.Image of NDVI.*

    Args:
        areaSZ:     An ee.FeatureCollection containing features that has area of each StressZone as its property.
        threshArea:      An integer that specifies the threshold value of area to filter an ee.FeatureCollection.
    Returns:
        ee.FeatureCollection:   The ee.FeatureCollection of big and small StressZones separately according to the threshold.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> bigSZ, smallSZ = splitSZLayers(areaSZ=ndviAreaCollection, threshArea=500)``
    """
    try:
        filterBigArea = ee.Filter.gte("area", threshArea)
        filterSmallArea = ee.Filter.lt("area", threshArea)

        bigSZ = areaSZ.filter(filterBigArea)
        smallSZ = areaSZ.filter(filterSmallArea)

        return bigSZ, smallSZ

    except Exception as e:
        raise exception.EERuntimeError(f"StressZone Layer Split Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def getClusterFeatureList(imageGeo: ee.Image, fList: ee.List) -> list:
    """ *A function that returns an ee.List containing list of all the StressZone clusters.*

    Args:
        imageGeo:       An image containing calculated NDVI values.
        fList:      An empty ee.List needed to iterate.
    Returns:
        list:   The list of all the StressZone clusters.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> fList = getClusterFeatureList(imageGeo=clusterImage, fList=ee.List([]))``
    """
    try:
        fList = ee.List(fList)
        clusters = imageGeo.reduceToVectors(geometry=imageGeo.geometry(), scale=1)
        clusters = clusters.toList(clusters.size())
        fList = fList.add(clusters)
        return fList

    except Exception as e:
        raise exception.EERuntimeError(f"Cluster Feature List Generation Failed @ Runtime: {e}")


# noinspection PyUnresolvedReferences
def genSZRender(ndviLayerCol, ndvi: ee.Image, field: Field) -> ee.FeatureCollection:
    """ *A function that creates an ee.FeatureCollection of all StressZones to be rendered.*

    Args:
        ndviLayerCol:       An f containing calculated NDVI values.
        ndvi:       An image containing calculated NDVI values.
        field:      A Field object.
    Returns:
        ee.FeatureCollection: The ee.FeatureCollection of all StressZones.
    Raises:
        TypeError:      Occurs if the geometry is not a ee.Geometry.
        ValueError:      Occurs if the unit is not valid.
        EERuntimeError: Occurs if area retrieval runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Calculating render:*\n
    ``>> renderNDVI = makeSZRender(ndviLayerCol=ndviImage, ndvi=ndvi, field)``
    """
    try:
        cleanSZ = genCleanSZ(ndviLayerCol, field)
        areaSZ = cleanSZ.map(setArea)

        threshArea = field.eeAOI.area(5).multiply(0.2).round().getInfo()
        threshPixel = round(threshArea / 100)

        bigSZLayers, smallSZLayers = splitSZLayers(areaSZ, threshArea)

        clusterImageList = areaLayers(bigSZLayers)
        clusterCollection = ee.ImageCollection.fromImages(clusterImageList)

        # noinspection PyUnresolvedReferences
        def applySNIC(clusterImage):
            """ A function that uses SNIC Segmentation algorithm to create a clustered image."""
            seeds = ee.Algorithms.Image.Segmentation.seedGrid(size=round(threshPixel / 4), gridType='hex')
            geoClusterImage = (ee.Algorithms.Image.Segmentation.SNIC(image=clusterImage, size=round(threshPixel / 2),
                                                                     compactness=5, seeds=seeds).select(['clusters'])
                               .clip(clusterImage.geometry()))

            return geoClusterImage

        geoClusters = clusterCollection.map(applySNIC)

        clusterFeatureList = ee.List(geoClusters.iterate(getClusterFeatureList, ee.List([]))).flatten()
        SNICCol = ee.FeatureCollection(clusterFeatureList).merge(smallSZLayers)
        SNICCol = ndvi.reduceRegions(collection=SNICCol, reducer=ee.Reducer.mean()).map(fixSNIC)

        return SNICCol

    except Exception as e:
        raise exception.EERuntimeError(f"StressZone SNIC Render Generation Failed @ Runtime: {e}")
