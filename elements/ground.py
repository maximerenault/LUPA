import numpy as np
from elements.wire import Wire


class Ground(Wire):
    def __init__(
        self, node1, node2, value: float | str | None = None, active: bool = False
    ) -> None:
        super().__init__(node1, node2, value, active)
        self.widths = [1, 1, 1, 1]

    def draw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6 = drbd.coord2pix(
            self.get_gnd_coords()
        )
        self.ids.append(drbd.canvas.create_line(xs, ys, xe, ye, tags="circuit"))
        self.ids.append(drbd.canvas.create_line(x1, y1, x2, y2, tags="circuit"))
        self.ids.append(drbd.canvas.create_line(x3, y3, x4, y4, tags="circuit"))
        self.ids.append(drbd.canvas.create_line(x5, y5, x6, y6, tags="circuit"))
        self.afterdraw(drbd)

    def redraw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6 = drbd.coord2pix(
            self.get_gnd_coords()
        )
        drbd.canvas.coords(self.ids[0], xs, ys, xe, ye)
        drbd.canvas.coords(self.ids[1], x1, y1, x2, y2)
        drbd.canvas.coords(self.ids[2], x3, y3, x4, y4)
        drbd.canvas.coords(self.ids[3], x5, y5, x6, y6)
        self.afterredraw(drbd)

    def get_gnd_coords(self):
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        length = np.linalg.norm(vec)
        if length == 0:
            return np.concatenate(
                (
                    coords[:2],
                    coords[:2],
                    coords[:2],
                    coords[:2],
                    coords[:2],
                    coords[:2],
                    coords[:2],
                    coords[:2],
                )
            )
        vec = vec / length
        w = 0.2
        h = 0.6
        vor = np.array([-vec[1], vec[0]])
        mid = coords[:2] + vec / 2
        p0 = coords[:2]
        p1 = mid - w / 2 * vec
        p2 = mid - w / 2 * vec + h / 2 * vor
        p3 = mid - w / 2 * vec - h / 2 * vor
        p4 = mid + (h - 0.175) / 2 * vor
        p5 = mid - (h - 0.175) / 2 * vor
        p6 = mid + w / 2 * vec + (h - 0.35) / 2 * vor
        p7 = mid + w / 2 * vec - (h - 0.35) / 2 * vor
        return np.concatenate((p0, p1, p2, p3, p4, p5, p6, p7))

    def setend(self, x, y):
        x0, y0, _, _ = self.getcoords()
        dist = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        if dist == 0:
            self.nodes[1].setcoords(x0, y0)
        else:
            x = x0 + round((x - x0) / dist) * 0.75
            y = y0 + round((y - y0) / dist) * 0.75
            self.nodes[1].setcoords(x, y)

    def drawname(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + 2 * x1) // 3
        y = (y0 + 2 * y1) // 3
        self.nameid = drbd.canvas.create_text(x, y, text=self.name, tags="circuit")

    def redrawname(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + 2 * x1) // 3
        y = (y0 + 2 * y1) // 3
        drbd.canvas.coords(self.nameid, x, y)
        drbd.canvas.itemconfig(self.nameid, text=self.name)

    def __str__(self):
        return "Gnd" + str(self.ids[0])

    def __repr__(self):
        return str(self)
