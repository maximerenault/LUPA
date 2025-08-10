class ElementsException(Exception):
    pass


class BadValueTypeError(ElementsException):
    def __init__(self, got, expected):
        super().__init__(
            "expected value type {} and got {}".format(repr(expected), repr(got))
        )
