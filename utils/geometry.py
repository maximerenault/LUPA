from elements.wire import Wire
from math import sqrt
import numpy as np


def intersect(elem1: Wire, elem2: Wire):
    """
    Returns intersection coordinates
    with special cases for avoiding
    the creation of undesirable nodes
    """
    x1, y1, x2, y2 = elem1.getcoords()
    x3, y3, x4, y4 = elem2.getcoords()
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # parallel
        if (y4 - y2) * (x2 - x1) - (x4 - x2) * (y2 - y1) == 0:  # colinear
            d13 = distance(x1, y1, x3, y3)
            d14 = distance(x1, y1, x4, y4)
            if d13 < d14:
                dp = dotprod(x1, y1, x2, y2, x3, y3, x4, y4)
                if dp > 0:
                    return (x3, y3)
            else:
                dp = dotprod(x1, y1, x2, y2, x3, y3, x4, y4)
                if dp < 0:
                    return (x4, y4)
        return (x2, y2)

    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    if ua <= 0 or ua > 1:  # out of range
        return (x2, y2)

    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ub < 0 or ub > 1:  # out of range
        return (x2, y2)
    if ub == 0:
        return (x3, y3)
    if ub == 1:
        return (x4, y4)
    return (x1, y1)


def distance(x1: float, y1: float, x2: float, y2: float):
    """
    Returns the distance between
    (x1,y1) and (x2,y2)
    """
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def dotprod(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x3: float,
    y3: float,
    x4: float,
    y4: float,
):
    """
    Returns the dot product of vectors
    (x2-x1,y2-y1) and (x4-x3,y4-y3)
    """
    return (x2 - x1) * (x4 - x3) + (y2 - y1) * (y4 - y3)


def point_on_elem(elem: Wire, x0: float, y0: float):
    """
    Checks if a point (x0,y0) is
    on the line of elem
    """
    x1, y1, x2, y2 = elem.getcoords()
    # Check angle by cross product 0->1 x 1->2
    if (y1 - y0) * (x2 - x1) - (x1 - x0) * (y2 - y1) != 0:
        return False
    dp1 = dotprod(x1, y1, x0, y0, x1, y1, x2, y2)
    dp2 = dotprod(x2, y2, x0, y0, x2, y2, x1, y1)
    if dp1 >= 0 and dp2 >= 0:
        return True
    return False


def start_from_elem(drbd, x0: float, y0: float):
    """
    Returns position and direction if starting from an
    existing element
    """
    # Direction of the starting element
    # by default it points left (so we draw to the right)
    eldir = 3
    for el in drbd.cgeom.elems[::-1]:
        if point_on_elem(el, x0, y0):
            xs, ys, xe, ye = el.getcoords()
            if xs == xe:
                if abs(ys - y0) < abs(ye - y0):
                    x0, y0 = xs, ys
                    if ys < ye:
                        eldir = 2
                    else:
                        eldir = 0
                else:
                    x0, y0 = xe, ye
                    if ys < ye:
                        eldir = 0
                    else:
                        eldir = 2
            else:
                if abs(xs - x0) < abs(xe - x0):
                    x0, y0 = xs, ys
                    if xs < xe:
                        eldir = 1
                    else:
                        eldir = 3
                else:
                    x0, y0 = xe, ye
                    if xs < xe:
                        eldir = 3
                    else:
                        eldir = 1
            break
    return x0, y0, eldir


def elem_init_pos(drbd, elem: Wire, startdir: int):
    """
    This method tries 4 cardinal directions for initial
    positionning of the element

    The default ordering is 0:S 1:E 2:N 3:W
    """

    x0, y0, _, _ = elem.getcoords()
    directions = np.array([[x0, y0 - 1], [x0 + 1, y0], [x0, y0 + 1], [x0 - 1, y0]])
    directions = np.roll(directions, -startdir, axis=0)
    direction = 0
    while direction < 4:
        x1, y1 = directions[direction]
        elem.setend(x1, y1)
        for el in drbd.cgeom.elems:
            tempx, tempy = intersect(elem, el)
            if distance(x0, y0, tempx, tempy) <= distance(x0, y0, x1, y1):
                x1 = tempx
                y1 = tempy
        if x1 == x0 and y1 == y0:
            direction += 1
        else:
            direction = 100
    elem.setend(x1, y1)
