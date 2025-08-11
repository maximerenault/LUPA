class CalculatorException(Exception):
    pass


class BadNumberError(CalculatorException):
    def __init__(self, number: str) -> None:
        super().__init__(f"unable to scan number: {number}")


class BadFunctionError(CalculatorException):
    def __init__(self, func: str, suppd_func: list) -> None:
        super().__init__(
            f"unexpected function {func}, list of supported functions: {suppd_func}"
        )


class UnexpectedCharacterError(CalculatorException):
    def __init__(self, char: str, expected: list = None) -> None:
        if expected:
            super().__init__(f"unexpected character {char}, expected: {expected}")
        else:
            super().__init__(f"unexpected character: {char}")


class UnexpectedEndError(CalculatorException):
    def __init__(self, expected: list) -> None:
        super().__init__(f"found end, but expected: {repr(expected)}")


class WrongArgsLenError(CalculatorException):
    def __init__(self, got: int, expected: int) -> None:
        super().__init__(f"got {got} arguments, but expected {expected}")


class ReadOnlyError(CalculatorException):
    def __init__(self, name: str) -> None:
        super().__init__(f"cannot modify read-only variable: {name}")
