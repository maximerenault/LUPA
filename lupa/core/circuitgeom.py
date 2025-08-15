from lupa.elements.wire import Wire


class CircuitGeom:
    def __init__(self) -> None:
        """
        A class for circuit geometry representation for drawing.
        """
        self.elems = []
        self.nodes = []

    def add_elem(self, elem: Wire) -> None:
        self.elems.append(elem)

    def add_elem_nodes(self, elem: Wire) -> None:
        for node in elem.nodes:
            self.nodes.append(node)

    def del_elem(self, index: int) -> None:
        """
        Deletes the element at position [index].
        Also deletes associated nodes.
        """
        del self.nodes[index * 2 + 1]
        del self.nodes[index * 2]
        del self.elems[index]

    def clear(self) -> None:
        """
        Clears all elements and nodes from the circuit geometry.
        """
        self.elems.clear()
        self.nodes.clear()
