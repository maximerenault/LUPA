class SolveFrameException(Exception):
    pass


class BadNumberError(SolveFrameException):
    def __init__(self, nbrstr: str) -> None:
        super().__init__(f"unable to correct number: {nbrstr}")
