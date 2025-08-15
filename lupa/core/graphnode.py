from lupa.core.graphedge import GraphEdge


types = ["Normal", "Source"]


class GraphNode:
    def __init__(self, type: str = "Normal") -> None:
        self.edges = []
        self.type = type
        self.probed = False
        self.probe_name = ""

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the node."""
        self.edges.append(edge)

    def set_type(self, type: str) -> None:
        """Set the type of the node."""
        self.type = type

    def __str__(self) -> str:
        lastr = "GN_" + self.type + "["
        for edge in self.edges:
            lastr += str(edge) + ", "
        lastr += "]"
        return lastr

    def __repr__(self) -> str:
        return str(self)
