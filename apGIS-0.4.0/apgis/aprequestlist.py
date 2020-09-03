"""
Class module that implements the class **RequestList**.

The RequestList class wraps a list of request products after validating them.
It also holds additional context attributes like the Sat and Sensor ID associated with the product list.
Generates a list of Product ID bands that are not part of the Satellite BASE bands.

Author: AntPod Designs Pvt Ltd.
"""
from apgis.apconfig import Config

CONFIG = Config()


class RequestList:
    """
    Class for product request list along with relevant data like required bands, satellite and sensor names.

    The RequestList class wraps a list of request products after validating them.
    It also holds additional context attributes like the Sat and Sensor ID associated with the product list.
    Generates a list of Product ID bands that are not part of the Satellite BASE bands.

    Class Attributes:
        - ``products:``         A list of product IDs.
        - ``sensorProducts:``   A dictionary of all Product IDs for the given sensor.
        - ``sensor:``           The Sensor ID associated with the productList.
        - ``sat:``              The Satellite ID.
        - ``reqBands:``         A list of product IDs that need to be generated.
    """

    def __init__(self, productList: list, sensor: str):
        """ Constructs a *RequestList* object.\n

        Yields a *RequestList* object.

        Args:
            productList:    The list of products around which to build the RequestList.
            sensor:         The Sensor ID for which the productList is intended.
        """
        try:
            if sensor not in CONFIG.getSensors():
                raise ValueError("@ Sensor ID validation: Invalid Sensor ID")

            self.products = productList
            self.sensor = sensor
            self.sat = CONFIG.getSatfromSensor(sensor=self.sensor)
            self.sensorProducts = CONFIG.getSensorProducts(sensor=self.sensor)

            if not self.__validateList__():
                raise ValueError(f"@ productList Validation: productList contains invalid products for {self.sensor}")

            self.reqBands = self.__generateReqBands__()

        except ValueError as e:
            raise ValueError(f"RequestList Construction Failed {e}")
        except Exception as e:
            raise RuntimeError(f"RequestList Construction Failed @ Object Initialisation: {e}")

    def __validateList__(self):
        """ A method that validates the productList with the list of possible products for a Sensor ID. """
        try:
            validate = True
            for product in self.products:
                if product not in self.sensorProducts:
                    validate = False
                    break

            return validate

        except Exception as e:
            raise RuntimeError(f"RequestList Validation Failed: {e}")

    def __generateReqBands__(self):
        """ A method that generates a list of req.bands i.e not available in the BASE product of the Sensor ID. """
        try:
            reqBands = []
            if self.sensorProducts:
                for product in self.products:
                    for band in self.sensorProducts[product]:
                        reqBands.append(band)

            reqBands = list(dict.fromkeys(reqBands))
            reqBands = [x for x in reqBands if x not in self.sensorProducts['BASE']]

            return reqBands

        except Exception as e:
            raise RuntimeError(f"RequestList ReqBand Generation Failed: {e}")
