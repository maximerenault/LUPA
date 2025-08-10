import numpy as np
from functools import total_ordering


@total_ordering
class Node:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.elems = []
        self.id = -1
        self.radius = 0.05
        self.listened = False
        self.listener_name = ""

    def getcoords(self):
        return np.array([self.x, self.y])

    def setcoords(self, x, y):
        self.x = x
        self.y = y

    def draw(self, drbd):
        radius = self.radius
        x0, y0 = self.x - radius, self.y + radius
        x1, y1 = self.x + radius, self.y - radius
        x0, y0, x1, y1 = drbd.coord2pix(np.array([x0, y0, x1, y1]))
        if self.listened:
            fill = "red"
        else:
            fill = ""
        self.id = drbd.canvas.create_oval(
            x0, y0, x1, y1, fill=fill, outline="", tags="circuit"
        )

    def redraw(self, drbd):
        if self.listened:
            drbd.canvas.itemconfig(self.id, fill="red")
            radius = self.radius
            x0, y0 = self.x - radius, self.y + radius
            x1, y1 = self.x + radius, self.y - radius
            x0, y0, x1, y1 = drbd.coord2pix(np.array([x0, y0, x1, y1]))
            drbd.canvas.coords(self.id, x0, y0, x1, y1)
        else:
            drbd.canvas.itemconfig(self.id, fill="")

    def set_listened(self, val):
        self.listened = bool(val)

    def add_elem(self, elem):
        self.elems.append(elem)

    def __lt__(self, node):
        return self.x < node.x or (self.x == node.x and self.y < node.y)

    def __gt__(self, node):
        return self.x > node.x or (self.x == node.x and self.y > node.y)

    def __le__(self, node):
        return self.x < node.x or (self.x == node.x and self.y <= node.y)

    def __ge__(self, node):
        return self.x > node.x or (self.x == node.x and self.y >= node.y)

    def __eq__(self, node):
        return self.x == node.x and self.y == node.y

    def __str__(self):
        return "N[" + str(self.x) + ", " + str(self.y) + "]"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return [float(self.x), float(self.y)]
