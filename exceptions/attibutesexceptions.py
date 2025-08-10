class AttributesException(Exception):
    pass


class BadNumberError(AttributesException):
    def __init__(self, number):
        super().__init__("unable to correct number: {}".format(number))


class BadCoordError(AttributesException):
    def __init__(self, coord):
        super().__init__("unable to find position: {}".format(coord))
