from elements.wire import Wire
import numpy as np


class Capacitor(Wire):
    def __init__(self, node1, node2, C, active: bool = False) -> None:
        super().__init__(node1, node2, C, active)
        self.w = 0.2
        self.h = 0.6
        self.widths = [2, 2, 1, 1]

    def draw(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_cap_coords()
        x01 = (x0 + x3) / 2
        y01 = (y0 + y3) / 2
        x11 = (x1 + x2) / 2
        y11 = (y1 + y2) / 2
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(
            np.array([x0, y0, x1, y1, x2, y2, x3, y3])
        )
        self.ids.append(
            drbd.canvas.create_line(x0, y0, x3, y3, width=2, tags="circuit")
        )
        self.ids.append(
            drbd.canvas.create_line(x1, y1, x2, y2, width=2, tags="circuit")
        )

        x01, y01, x11, y11 = drbd.coord2pix(np.array([x01, y01, x11, y11]))
        x00, y00, x10, y10 = drbd.coord2pix(self.getcoords())
        self.ids.append(drbd.canvas.create_line(x00, y00, x01, y01, tags="circuit"))
        self.ids.append(drbd.canvas.create_line(x10, y10, x11, y11, tags="circuit"))
        self.afterdraw(drbd)

    def redraw(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_cap_coords()
        x01 = (x0 + x3) / 2
        y01 = (y0 + y3) / 2
        x11 = (x1 + x2) / 2
        y11 = (y1 + y2) / 2
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(
            np.array([x0, y0, x1, y1, x2, y2, x3, y3])
        )
        drbd.canvas.coords(self.ids[0], x0, y0, x3, y3)
        drbd.canvas.coords(self.ids[1], x1, y1, x2, y2)

        x01, y01, x11, y11 = drbd.coord2pix(np.array([x01, y01, x11, y11]))
        x00, y00, x10, y10 = drbd.coord2pix(self.getcoords())
        drbd.canvas.coords(self.ids[2], x00, y00, x01, y01)
        drbd.canvas.coords(self.ids[3], x10, y10, x11, y11)

        self.afterredraw(drbd)

    def get_cap_coords(self):
        w = self.w
        h = self.h
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        length = np.linalg.norm(vec)
        if length == 0:
            return np.concatenate((coords, coords))
        vec = vec / length
        vor = np.array([-vec[1], vec[0]])
        mid = (coords[2:] + coords[:2]) / 2
        p0 = mid - w / 2 * vec + h / 2 * vor
        p1 = mid + w / 2 * vec + h / 2 * vor
        p2 = mid + w / 2 * vec - h / 2 * vor
        p3 = mid - w / 2 * vec - h / 2 * vor
        return np.concatenate((p0, p1, p2, p3))

    def __str__(self):
        return "C" + str(self.ids[0])

    def __repr__(self):
        return str(self)
