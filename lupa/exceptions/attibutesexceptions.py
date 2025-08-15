class AttributesException(Exception):
    pass


class BadNumberError(AttributesException):
    def __init__(self, nbrstr: str) -> None:
        super().__init__(f"unable to correct number: {nbrstr}")
