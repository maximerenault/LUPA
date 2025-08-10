class CalculatorException(Exception):
    pass


class BadNumberError(CalculatorException):
    def __init__(self, number):
        super().__init__("unable to scan number: {}".format(number))


class BadFunctionError(CalculatorException):
    def __init__(self, func, suppd_func):
        super().__init__(
            "unexpected function {}, list of supported functions: {}".format(
                repr(func), repr(suppd_func)
            )
        )


class UnexpectedCharacterError(CalculatorException):
    def __init__(self, char, expected=[]):
        if expected:
            super().__init__(
                "unexpected character {}, expected: {}".format(
                    repr(char), repr(expected)
                )
            )
        else:
            super().__init__("unexpected character: {}".format(char))


class UnexpectedEndError(CalculatorException):
    def __init__(self, expected):
        super().__init__("found end, but expected: {}".format(repr(expected)))


class WrongArgsLenError(CalculatorException):
    def __init__(self, got, expected):
        super().__init__(
            "got {} arguments, but expected {}".format(repr(got), repr(expected))
        )
