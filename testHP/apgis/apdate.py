"""
Class module that implements the class *Date*.

The Date class wraps a datetime object and contains method for different forms of representation.
It can be initialized in multiple formats and supports basic operations on itself like advancing
by a delta and generating the next day, etc..

************************************************************************
Copyrights (c) 2020 ANTPOD Designs Private Limited. All Rights Reserved.
************************************************************************
"""
import ee

import apgis.apexception as apexception


class Date:
    """
    *Class for date & time data categories and relevant conversions.*

    **Class Attributes:**\n
    - ``eeDate:``       An ee.Date object
    - ``dateFormat:``       A string retrieved from ee that contains all the temporal parameter separated by a "/".
    - ``dateValues``        A list containing all the datetime parameters as members.

    - ``year:``     A numeric string representing the year.
    - ``month:``        A numeric string representing the month.
    - ``monthCode:``        An alpha-3 string representing the month.
    - ``monthName:``        A string representing the name of the month.
    - ``day:``      A numeric string representing the day.
    - ``dayOfWeek:``        A number string representing the day of the week.
    - ``dayOfWeekCode:``        An alpha-3 string representing the day of the week.
    - ``dayOfWeekName:``        A string representing the name of the day of the week.
    - ``hour24:``       A numeric string representing the hour in a 24hour format.
    - ``hour12:``       A numeric string representing the hour in a 12hour format.
    - ``meridiem:``     A string representing the meridiem. AM/PM
    - ``minute:``       A numeric string representing the minutes.
    - ``seconds:``      A numeric string representing the seconds.
    - ``microSeconds:``     A numeric string representing the microseconds.
    - ``timezone:``     A numeric string representing the timezone as difference from UTC.
    - ``tzCode:``       An alpha-3 string representing the timezone.

    - ``timeString``        A string representing time. "hh:mm:ss".
    - ``timeStringFull``        A string representing the full time. "hh:mm:ss:SSS Z".
    - ``timeStringHuman``       A human-readable string representing simple time. "hh:mm aa".

    - ``dateString``        A string representing the date. "YYYY-MM-DD".
    - ``dateStringHuman:``      A human-readable string representing the date. "day of month YYYY"

    - ``ISOString:``        An ISO 8601 datestring of the date.
    - ``EpochMS:``      An integer representing the UNIX Epoch time in microseconds.

    **Class Methods:**\n
    - ``advanceDelta:``     A method that returns a Date object that has been advanced by a specified delta.
    - ``nextDay:``      A method that returns a Date object that has been advanced by a single day.

    The Date class wraps a datetime object and contains method for different forms of representation.
    It can be initialized in multiple formats and supports basic operations on itself like advancing
    by a delta and generating the next day, etc..\n

    References:
        Some references to related topics:\n
    *Datetime Formatting Standards:*\n
    http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html

    *ISO 8601 Standard:*\n
    https://www.iso.org/iso-8601-date-and-time-format.html

    *ISO DateString Standard:*\n
    https://www.w3.org/TR/NOTE-datetime

    *UNIX Epoch Time Standard:*\n
    https://www.unixtimestamp.com/index.php
    """

    def __init__(self, dateParam):
        """ **Constructor Method**\n
        Yields a ``Date`` object.

        *Wraps an ee.Date object within it along with a few other datetime parameters.*\n
        Accepts the following formats as input parameters:\n
        -  An ee.Date.
        -  An ee.Image. (Stores its acquisition time)
        -  An ISO 8601 string.
        -  An integer number of milliseconds since the epoch.
        -  A bare date.
        -  An ee.ComputedObject.

        Args:
            dateParam:      The parameter to parse/extract and wrap into a Date object.
        Raises:
            TypeError:      if the date parameter to wrap is not among the valid formats.

        Examples:
            Some example uses of this staticmethod are:\n
        *Initialising with an ee.Image:*\n
        ``>> date = Date(image)``

        *Initialising with an ISO String:*\n
        ``>> date = Date("2020-06-05T04:58:03.3852730Z")``

        *Initialising with an epoch integer:*\n
        ``>> date = Date(1591645881000)``
        """
        try:
            if isinstance(dateParam, ee.Date):
                self.eeDate = dateParam

            elif isinstance(dateParam, ee.Image):
                # noinspection PyUnresolvedReferences
                self.eeDate = dateParam.date()

            else:
                self.eeDate = ee.Date(dateParam)

        except Exception as e:
            raise RuntimeError(f"Date Construction Failed @ eeDate generation: {e}")

        if not isinstance(self.eeDate, ee.Date):
            raise TypeError("Date Construction Failed @ eeDate type check: Invalid ee.Date Wrapped")

        try:
            # noinspection PyTypeChecker
            self.__generateAttributes__(self.eeDate)

        except Exception as e:
            raise RuntimeError(f"Date Construction Failed @ Attribute Generation: {e}")

    def __generateAttributes__(self, eeDate):
        """ A method that initializes all the datetime attribute values. Used to construct the Date object. """
        try:
            self.dateFormat = eeDate.format("yyyy/MM/MMM/MMMM/dd/e/EEE/EEEE/kk/hh/aa/mm/ss/SSS/Z/z").getInfo()
            self.dateValues = self.dateFormat.split("/")

        except Exception as e:
            raise apexception.EERuntimeError(f"Date Attribute Generation Failed @ ee.Date format API call: {e}")

        try:
            self.year = self.dateValues[0]
            self.month = self.dateValues[1]
            self.day = self.dateValues[4]

            self.hour24 = self.dateValues[8]
            self.minute = self.dateValues[11]
            self.seconds = self.dateValues[12]
            self.microSeconds = self.dateValues[13]

            self.timezone = self.dateValues[14]

        except Exception as e:
            raise RuntimeError(f"Date Attribute Generation Failed @ Attribute assignment: {e}")

    def __repr__(self):
        """ Represents a *Date* object. """
        return self.ISOString

    def __str__(self):
        """ String representation of a *Date* object. """
        return f"{self.timeStringHuman} {self.dateStringHuman}"

    @property
    def monthCode(self):
        """ Alpha-3 string of the month. eg. Aug, Dec, etc. """
        return self.dateValues[2]

    @property
    def monthName(self):
        """ Name of the month. """
        return self.dateValues[3]

    @property
    def dayOfWeek(self):
        """ Numeric string of the day of the week. eg. Monday -> 2, Thursday -> 5, etc. """
        return self.dateValues[5]

    @property
    def dayOfWeekCode(self):
        """ Alpha-3 string of the day of the week. eg. Mon, Tue, etc. """
        return self.dateValues[6]

    @property
    def dayOfWeekName(self):
        """ Name of the day of the week."""
        return self.dateValues[7]

    @property
    def hour12(self):
        """ Numeric string of the hour in a 12hour format."""
        return self.dateValues[9]

    @property
    def meridiem(self):
        """ Meridiem. AM/PM"""
        return self.dateValues[10]

    @property
    def tzCode(self):
        """ Alpha-3 of the timezone. eg. UTC, IST, etc. """
        return self.dateValues[15]

    @property
    def timeString(self):
        """ Time represented as 'hh:mm:ss'. """
        return f"{self.hour24}:{self.minute}:{self.seconds}"

    @property
    def timeStringFull(self):
        """ Time represented as 'hh:mm:ss:SSS Z'. """
        return f"{self.timeString}:{self.microSeconds} {self.tzCode}"

    @property
    def timeStringHuman(self):
        """ Time represented as 'hh:mm aa'. """
        return f"{self.hour12}:{self.minute} {self.meridiem}"

    @property
    def dateString(self):
        """ Date represented as 'YYYY-MM-DD'. """
        return f"{self.year}-{self.month}-{self.day}"

    @property
    def dateStringHuman(self):
        """ Date represented as 'day of month YYYY'. """
        return f"{self.day} of {self.monthName} {self.year}"

    @property
    def ISOString(self):
        """ ISO 8601 datestring of the Date."""
        return f"{self.dateString}T{self.timeString}.{self.microSeconds}Z"

    @property
    def epochMS(self):
        """ Number of microseconds since the Epoch i.e UNIX Time."""
        return int(self.eeDate.getInfo()['value'])

    def advanceDelta(self, delta: float, unit: str):
        """ *A method that returns the Date advanced by certain unit of delta.*

        The Method advances a Date object the delta number of units and returns a newly wrapped Date object.\n
        Allowed units to advance the date are:
            **'year', 'month', 'week', 'day', 'hour', 'minute', 'second'**.

        Args:
            delta:      The delta to be advanced.
            unit:       The unit on which to advance.
        Returns:
            Date:       a Date that has to be advanced by the specified parameters.
        Raises:
            ValueError: Occurs if the unit passed for delta advancing is not allowed.

        Examples:
            Some example uses of this method are:\n
        *Advancing a Date by 1 week:*\n
        ``>> newDate = date.advance(1, "week")``\n

        *Advancing a Date by 5 years:*
        ``>> newDate = date.advance(5, "year")``\n
        """
        if unit not in ["year", "month", "week", "day", "hour", "minute", "second"]:
            raise ValueError("Advance Delta Failed @ Unit Check: Invalid Delta Unit")

        try:
            # noinspection PyUnresolvedReferences
            return Date(self.eeDate.advance(delta, unit))

        except Exception as e:
            raise apexception.EERuntimeError(f"Advance Delta Failed @ ee.Date advance API call: {e}")

    def nextDay(self):
        """ *A method that returns the Date advanced by exactly 1 day.*

        Returns:
            Date:       a Date that has to be advanced by 1 day.

        Examples:
            Some example uses of this method are:\n
        *Advancing a Date:*\n
        ``>> newDate = date.nextDay()``\n
        """
        try:
            return self.advanceDelta(1, "day")

        except Exception as e:
            raise RuntimeError(f"Next Day Generation Failed @ advanceDelta: {e}")
