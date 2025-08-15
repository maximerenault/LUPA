class CircuitSolverException(Exception):
    pass


class OverconstrainedError(CircuitSolverException):
    def __init__(self, eqs: int, unkns: int) -> None:
        super().__init__(
            f"Overconstrained system: {eqs} equations for {unkns} unknowns."
        )


class UnderconstrainedError(CircuitSolverException):
    def __init__(self, eqs: int, unkns: int) -> None:
        super().__init__(
            f"Underconstrained system: {eqs} equations for {unkns} unknowns."
        )
