from elements.wire import Wire


class GraphEdge:
    def __init__(self, start: int, end: int, elem: Wire) -> None:
        self.start = start
        self.end = end
        self.elem = elem

    def __str__(self):
        lastr = repr(self.elem) + "[" + str(self.start) + "," + str(self.end) + "]"
        return lastr

    def __repr__(self):
        return str(self)
