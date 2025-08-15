from lupa.elements.psource import PSource
from lupa.elements.node import Node


class QSource(PSource):
    def __init__(
        self,
        node1: Node,
        node2: Node,
        value: float | str | None = None,
        active: bool = False,
    ) -> None:
        super().__init__(node1, node2, value, active)
        self.name = "Q"

    def __str__(self) -> str:
        return "QSc" + str(self.ids[0])

    def __repr__(self) -> str:
        return str(self)
