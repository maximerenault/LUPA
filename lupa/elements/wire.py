from bisect import bisect_left
from tkinter import Event
import numpy as np
from lupa.exceptions.calculatorexceptions import CalculatorException
from lupa.utils.calculator import calculator as calc
from lupa.elements.node import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lupa.GUI.drawingboard import DrawingBoard


class Wire:
    def __init__(
        self,
        node1: Node,
        node2: Node,
        value: float | str | None = None,
        active: bool = False,
    ) -> None:
        self.name = ""
        self.nameid = -1
        self.nodes = [node1, node2]
        node1.add_elem(self)
        node2.add_elem(self)
        self.bbox = -1
        self.ids = []
        self.widths = [1]
        self.listened = 0
        self.listener_name = ""
        self.Qid = -1
        self.Qsize = 1.0

        # Useful for elements with value
        self.active = active
        self.set_value(value)

    def drawbbox(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(self.get_bbox_coords())
        self.bbox = drbd.canvas.create_polygon(
            x0, y0, x1, y1, x2, y2, x3, y3, fill="", outline="", tags="circuit"
        )
        drbd.canvas.tag_bind(
            self.bbox,
            "<ButtonPress-1>",
            lambda event, drbd=drbd: self.onElemClick(event, drbd),
        )
        drbd.canvas.tag_bind(
            self.bbox,
            "<ButtonRelease-1>",
            lambda event, drbd=drbd: self.onElemRelease(event, drbd),
        )
        drbd.canvas.tag_bind(
            self.bbox,
            "<B1-Motion>",
            lambda event, drbd=drbd: self.onElemMotion(event, drbd),
        )
        drbd.canvas.tag_bind(
            self.bbox,
            "<Enter>",
            lambda event, drbd=drbd: self.onElemHoverI(event, drbd),
        )
        drbd.canvas.tag_bind(
            self.bbox,
            "<Leave>",
            lambda event, drbd=drbd: self.onElemHoverO(event, drbd),
        )

    def redrawbbox(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(self.get_bbox_coords())
        drbd.canvas.coords(self.bbox, x0, y0, x1, y1, x2, y2, x3, y3)

    def drawQ(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1, x2, y2 = drbd.coord2pix(self.get_Q_coords())
        if self.listened:
            fill = "red"
        else:
            fill = ""
        self.Qid = drbd.canvas.create_polygon(
            x0, y0, x1, y1, x2, y2, fill=fill, outline="", width=2, tags="circuit"
        )

    def redrawQ(self, drbd: "DrawingBoard") -> None:
        if self.listened:
            drbd.canvas.itemconfig(self.Qid, fill="red")
            x0, y0, x1, y1, x2, y2 = drbd.coord2pix(self.get_Q_coords())
            drbd.canvas.coords(self.Qid, x0, y0, x1, y1, x2, y2)
        else:
            drbd.canvas.itemconfig(self.Qid, fill="")

    def drawname(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2
        self.nameid = drbd.canvas.create_text(x, y, text=self.name, tags="circuit")

    def redrawname(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2
        drbd.canvas.coords(self.nameid, x, y)
        drbd.canvas.itemconfig(self.nameid, text=self.name)

    def draw(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        self.ids.append(drbd.canvas.create_line(x0, y0, x1, y1, tags="circuit"))
        self.afterdraw(drbd)

    def afterdraw(self, drbd: "DrawingBoard") -> None:
        for node in self.nodes:
            node.draw(drbd)
        self.drawQ(drbd)
        self.drawname(drbd)
        self.drawbbox(drbd)

    def redraw(self, drbd: "DrawingBoard") -> None:
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        self.afterredraw(drbd)

    def afterredraw(self, drbd: "DrawingBoard") -> None:
        for node in self.nodes:
            node.redraw(drbd)
        self.redrawQ(drbd)
        self.redrawname(drbd)
        self.redrawbbox(drbd)

    def get_bbox_coords(self) -> np.ndarray:
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        length = np.linalg.norm(vec)
        if length == 0:
            return np.concatenate((coords, coords))
        w = 0.8 * length
        h = 0.4
        vec = vec / length
        vor = np.array([-vec[1], vec[0]])
        mid = (coords[2:] + coords[:2]) / 2
        p0 = mid - w / 2 * vec + h / 2 * vor
        p1 = mid + w / 2 * vec + h / 2 * vor
        p2 = mid + w / 2 * vec - h / 2 * vor
        p3 = mid - w / 2 * vec - h / 2 * vor
        return np.concatenate((p0, p1, p2, p3))

    def get_Q_coords(self) -> np.ndarray:
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        length = np.linalg.norm(vec)
        if length == 0:
            return np.concatenate((coords, coords))
        sign = self.listened
        w = 0.85 * length
        h = 0.2 * self.Qsize
        vec = vec / length
        vor = np.array([-vec[1], vec[0]])
        mid = (coords[2:] + coords[:2]) / 2
        p0 = mid + sign * (w / 2 - 0.1 * self.Qsize) * vec - h / 2 * vor
        p1 = mid + sign * w / 2 * vec
        p2 = mid + sign * (w / 2 - 0.1 * self.Qsize) * vec + h / 2 * vor
        return np.concatenate((p0, p1, p2))

    def getcoords(self) -> np.ndarray:
        return np.concatenate((self.nodes[0].getcoords(), self.nodes[1].getcoords()))

    def setstart(self, x: float, y: float) -> None:
        self.nodes[0].setcoords(x, y)

    def setend(self, x: float, y: float) -> None:
        self.nodes[1].setcoords(x, y)

    def get_node_id(self, node: Node) -> int:
        if node == self.nodes[0]:
            return 0
        else:
            return 1

    def get_other_end(self, node: Node) -> Node:
        return self.nodes[(self.get_node_id(node) + 1) % 2]

    def get_listenP(self, pos: int) -> bool:
        return self.nodes[pos].listened

    def set_listenP(self, pos: int, val: int, drbd: "DrawingBoard") -> None:
        self.nodes[pos].set_listened(val)
        if val:
            drbd.frameListeners.add_pressure_listener(self.nodes[pos])
        else:
            drbd.frameListeners.remove_pressure_listener(self.nodes[pos])

    def get_listenQ(self) -> bool:
        return self.listened

    def set_listenQ(self, val: int, drbd: "DrawingBoard") -> None:
        oldval = self.listened
        self.listened = val
        if oldval == 0 and val != 0:
            drbd.frameListeners.add_flow_listener(self)
        elif oldval != 0 and val == 0:
            drbd.frameListeners.remove_flow_listener(self)

    def onElemClick(self, event: Event, drbd: "DrawingBoard") -> None:
        if drbd.drag_function == "Edit":
            id = bisect_left(drbd.cgeom.elems, self.ids[0], key=lambda a: a.ids[0])
            if id == len(drbd.cgeom.elems):
                print("Error: Could not find element")
            drbd.frameAttr.change_elem(id)
            drbd.nomove = True
            self.prevcoords = self.getcoords()
            self.x0, self.y0 = drbd.pix2coord(event.x, event.y)

    def onElemRelease(self, event: Event, drbd: "DrawingBoard") -> None:
        if drbd.drag_function == "Edit":
            drbd.nomove = False

    def onElemMotion(self, event: Event, drbd: "DrawingBoard") -> None:
        if drbd.drag_function == "Edit":
            x1, y1 = drbd.pix2coord(event.x, event.y)
            self.setstart(
                self.prevcoords[0] - round(self.x0 - x1),
                self.prevcoords[1] - round(self.y0 - y1),
            )
            self.setend(
                self.prevcoords[2] - round(self.x0 - x1),
                self.prevcoords[3] - round(self.y0 - y1),
            )
            self.redraw(drbd)

    def onElemHoverI(self, event: Event, drbd: "DrawingBoard") -> None:
        if drbd.drag_function == "Edit":
            for id, w in zip(self.ids, self.widths):
                drbd.canvas.itemconfig(id, width=w + 2)

    def onElemHoverO(self, event: Event, drbd: "DrawingBoard") -> None:
        if drbd.drag_function == "Edit":
            for id, w in zip(self.ids, self.widths):
                drbd.canvas.itemconfig(id, width=w)

    def delete(self, drbd: "DrawingBoard") -> None:
        for id in self.ids:
            drbd.canvas.delete(id)
        drbd.canvas.delete(self.bbox)
        drbd.canvas.delete(self.nameid)
        drbd.canvas.delete(self.Qid)

    def __str__(self) -> str:
        return "W" + str(self.ids[0])

    def __repr__(self) -> str:
        return str(self)

    def set_value(self, value: float | str | None) -> int:
        if value is None:
            self.value = None
            self.active = False
            return 0
        try:  # try value as a float
            value = float(value)
            self.active = False
        except (ValueError, TypeError):
            try:  # try value as an expression
                _, vars = calc.calculate(value, True)
                if vars:
                    self.active = True
                else:
                    self.active = False
            except CalculatorException:
                self.value = value
                self.active = False
                return 1
        self.value = value
        # source = sp.interpolate.CubicSpline(x, y, extrapolate="periodic")
        # self.source = source
        return 0

    def get_value(self) -> float | str | None:
        return self.value

    def set_name(self, name: str) -> None:
        self.name = name

    def to_dict(self, nodes_list: list[Node]) -> dict:
        my_dict = {}
        my_dict["type"] = self.__class__.__name__
        my_dict["name"] = self.name
        my_dict["nodes"] = [
            nodes_list.index(self.nodes[0]),
            nodes_list.index(self.nodes[1]),
        ]
        my_dict["pressure_listeners"] = [self.get_listenP(0), self.get_listenP(1)]
        my_dict["pressure_listener_names"] = [
            self.nodes[0].listener_name,
            self.nodes[1].listener_name,
        ]
        my_dict["flow_listener"] = self.get_listenQ()
        my_dict["flow_listener_name"] = self.listener_name
        my_dict["active"] = self.active
        my_dict["value"] = self.get_value()
        return my_dict
