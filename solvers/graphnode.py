from solvers.graphedge import GraphEdge


types = ["Normal", "Source"]


class GraphNode:
    def __init__(self, type: str = "Normal") -> None:
        self.edges = []
        self.type = type
        self.listened = False
        self.listener_name = ""

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    def set_type(self, type: str):
        self.type = type

    def __str__(self):
        lastr = "GN_" + self.type + "["
        for edge in self.edges:
            lastr += str(edge) + ", "
        lastr += "]"
        return lastr

    def __repr__(self):
        return str(self)
