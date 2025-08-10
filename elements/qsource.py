from elements.psource import PSource


class QSource(PSource):
    def __init__(
        self, node1, node2, value: float | str | None = None, active: bool = False
    ) -> None:
        super().__init__(node1, node2, value, active)
        self.name = "Q"

    def __str__(self):
        return "QSc" + str(self.ids[0])

    def __repr__(self):
        return str(self)
