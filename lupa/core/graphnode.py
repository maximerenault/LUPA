from lupa.core.graphedge import GraphEdge
from enum import Enum


class GraphNodeType(Enum):
    DIPOLE = "Dipole"
    SOURCE = "Source"


class GraphNode:
    def __init__(self, type: str = GraphNodeType.DIPOLE) -> None:
        self.edges: list[GraphEdge] = []
        self.type: GraphNodeType = type
        self.probed: bool = False
        self.probe_name: str = ""

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the node."""
        self.edges.append(edge)

    def set_type(self, type: GraphNodeType) -> None:
        """Set the type of the node."""
        self.type = type

    def __str__(self) -> str:
        lastr = "GN_" + self.type.value + "["
        for edge in self.edges:
            lastr += str(edge) + ", "
        lastr += "]"
        return lastr

    def __repr__(self) -> str:
        return str(self)
