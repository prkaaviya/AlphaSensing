"""
Module for image masking and pixel data manipulations.

Library of top-level functions to generate masked images and pixel level manipulations.

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import ee

import apgis.apexception as apexception

from typing import List, Union
Number = Union[int, float]


# noinspection PyUnresolvedReferences
def generateRangeMask(image: ee.Image,
                      low: Number,
                      high: Number,
                      flip: bool = False) -> ee.Image:
    """ *A function that masks pixels with a value between a range of values.*

    The function mask all pixels in an Image that fall between a specified range of values.
    Option to mask all values outside a given range by setting the flip value to True.

    Args:
        image:      The image to be masked.
        low:        The lower limit of range, inclusive.
        high:       The higher limit of range, inclusive.
        flip:       The flag to flip the mask. Defaults to False.
    Returns:
        A masked Image.
    Raises:
        TypeError:      Occurs if the parameter type check fails.
        ValueError:     Occurs if the image has multiple bands.
        EERuntimeError: Occurs if masking runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Masking all pixels with value between 5 and 9:*\n
    ``>> maskedImage = generateRangeMask(image=image, low=5, high=9)``\n

    *Masking all pixels with value between 5 and 9:*\n
    ``>> maskedImage = generateRangeMask(image=image, low=5, high=9)``\n
    """
    if not isinstance(image, ee.Image):
        raise TypeError("Range Masking Failed @ type check: image must be an ee.Image")

    if not isinstance(low, (float, int)):
        raise TypeError("Range Masking Failed @ type check: low must be an int")

    if not isinstance(high, (float, int)):
        raise TypeError("Range Masking Failed @ type check: high must be an int")

    if len(image.bandNames().getInfo()) != 1:
        raise ValueError("Range Masking Failed @ band check: image must have only one band")

    try:
        if flip:
            highmask = image.gt(high)
            lowmask = image.lt(low)
            masker = lowmask.add(highmask)
        else:
            highmask = image.gte(low)
            lowmask = image.lte(high)
            masker = lowmask.updateMask(highmask)

        maskedimage = ee.Image(image.updateMask(masker))
        return maskedimage

    except Exception as e:
        raise apexception.EERuntimeError(f"Range Masking Failed @ Runtime: {e}")


def generateMultiRangeMask(image: ee.Image,
                           ranges: List[Number]):
    """ *A function that generates an ImageCollection of masked images between a list of ranges.*

    Args:
        image:      The Image for which to generate masks.
        ranges:     The list of ranges to be used to generate masks.
    Returns:
        An ImageCollection of masked Images.
    Raises:
        TypeError:      Occurs if the parameter type check fails.
        ValueError:     Occurs if the image has multiple bands.
        EERuntimeError: Occurs if the masking runtime fails.

    Examples:
        Some example uses of this method are:\n
    *Generating a masked ImageCollection for ranges [0,2,4,6]:*\n
    ``>> maskedCol = generateMultiRangeMasks(image=image, ranges=[0,2,4,6])``\n
    """
    if not isinstance(image, ee.Image):
        raise TypeError("Multi Range Masking Failed @ type check: image must be an ee.Image")

    if not isinstance(ranges, list):
        raise TypeError("Multi Range Masking Failed @ type check: ranges must be a list")

    # noinspection PyUnresolvedReferences
    if len(image.bandNames().getInfo()) != 1:
        raise ValueError("Multi Range Masking Failed @ band check: image must have only one band.")

    try:
        maskedImageList = []

        for low, high in zip(ranges, ranges[1:]):
            maskedImage = generateRangeMask(image=image, low=low, high=high)
            maskedImageList.append(maskedImage)

        maskedCol = ee.ImageCollection(maskedImageList)
        return maskedCol

    except Exception as e:
        raise apexception.EERuntimeError(f"Multi Range Masking Failed @ Runtime: {e}")
