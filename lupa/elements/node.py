import numpy as np
from functools import total_ordering
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lupa.GUI.drawingboard import DrawingBoard
    from lupa.elements.wire import Wire


@total_ordering
class Node:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.elems: list[Wire] = []
        self.id: int = -1
        self.radius: float = 0.05
        self.probed: bool = False
        self.probe_name: str = ""

    def getcoords(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def setcoords(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def draw(self, drbd: "DrawingBoard") -> None:
        radius = self.radius
        x0, y0 = self.x - radius, self.y + radius
        x1, y1 = self.x + radius, self.y - radius
        x0, y0, x1, y1 = drbd.coord2pix(np.array([x0, y0, x1, y1]))
        if self.probed:
            fill = "red"
        else:
            fill = ""
        self.id = drbd.canvas.create_oval(
            x0, y0, x1, y1, fill=fill, outline="", tags="circuit"
        )

    def redraw(self, drbd: "DrawingBoard") -> None:
        if self.probed:
            drbd.canvas.itemconfig(self.id, fill="red")
            radius = self.radius
            x0, y0 = self.x - radius, self.y + radius
            x1, y1 = self.x + radius, self.y - radius
            x0, y0, x1, y1 = drbd.coord2pix(np.array([x0, y0, x1, y1]))
            drbd.canvas.coords(self.id, x0, y0, x1, y1)
        else:
            drbd.canvas.itemconfig(self.id, fill="")

    def set_probed(self, val: int) -> None:
        self.probed = bool(val)

    def add_elem(self, elem: "Wire") -> None:
        self.elems.append(elem)

    def __lt__(self, node: "Node") -> bool:
        return self.x < node.x or (self.x == node.x and self.y < node.y)

    def __gt__(self, node: "Node") -> bool:
        return self.x > node.x or (self.x == node.x and self.y > node.y)

    def __le__(self, node: "Node") -> bool:
        return self.x < node.x or (self.x == node.x and self.y <= node.y)

    def __ge__(self, node: "Node") -> bool:
        return self.x > node.x or (self.x == node.x and self.y >= node.y)

    def __eq__(self, node: "Node") -> bool:
        return self.x == node.x and self.y == node.y

    def __str__(self) -> str:
        return "N[" + str(self.x) + ", " + str(self.y) + "]"

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> list[float]:
        return [float(self.x), float(self.y)]
