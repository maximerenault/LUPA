class ElementsException(Exception):
    pass


class BadValueTypeError(ElementsException):
    def __init__(self, got: type, expected: type) -> None:
        super().__init__(f"expected value type {repr(expected)} and got {repr(got)}")
