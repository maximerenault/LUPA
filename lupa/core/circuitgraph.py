from lupa.elements.node import Node
from lupa.elements.wire import Wire
from lupa.elements.ground import Ground
from lupa.core.graphedge import GraphEdge
from lupa.core.graphnode import GraphNode, GraphNodeType
from bisect import bisect_left, bisect_right


class CircuitGraph:
    def __init__(self, cnodes: list[Node], celems: list[Wire]) -> None:
        """
        A class that contains a directional graph representation of the circuit
        and allows for communication with the circuit solver.

        This is not a "real" directional graph as we traverse its edges in any
        direction, but they keep their direction to facilitate the next steps.
        """
        self.nodes, self.edges = self.convert_circuit_to_graph(cnodes, celems)
        self.paths, self.start_ends = self.graph_max_len_non_branching_paths()
        self.delete_node_sources()

    def convert_circuit_to_graph(
        self, cnodes: list[Node], celems: list[Wire]
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """
        We construct a graph from the geometrical nodes (cnodes) and elements (celems).
        Based on the cnodes positions and the elements they contain, we create
        a list of GraphNode and GraphEdge objects.

        A GraphNode contains a list of GraphEdge objects to which it is connected.
        A GraphEdge contains the start and end node indices and the element it
        represents.
        """
        cnodes = sorted(cnodes)
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        edgedict = {celem: [-1, -1] for celem in celems if type(celem) is not Wire}

        while len(cnodes) > 0:
            # extract first sublist of identical nodes
            idend = bisect_right(cnodes, cnodes[0])
            subcnodes = cnodes[0:idend]
            del cnodes[0:idend]

            newnode = GraphNode()
            nodes.append(newnode)
            idnode = len(nodes) - 1

            for cnode in subcnodes:
                if cnode.probed:
                    newnode.probed = True
                    newnode.probe_name = cnode.probe_name
                celem = cnode.elems[0]
                if type(celem) is Wire:
                    # if we reach a wire, we collapse it
                    otherend = celem.get_other_end(cnode)
                    if otherend.probed:
                        newnode.probed = True
                    idstart = bisect_left(cnodes, otherend)
                    idend = bisect_right(cnodes, otherend)
                    # we prevent going back through the same wire by removing the node.
                    # we can't use list.remove because two nodes are equal if they have
                    # the same coords.
                    for i in range(idstart, idend):
                        if cnodes[i].elems[0] == celem:
                            del cnodes[i]
                            break
                    subcnodes += cnodes[idstart : idend - 1]
                    del cnodes[idstart : idend - 1]
                else:
                    # for other elements we save the position of the node
                    idn = celem.get_node_id(cnode)
                    edgedict[celem][idn] = idnode
                    if isinstance(celem, Ground) and idn == 1:
                        newnode.set_type(GraphNodeType.SOURCE)

        for celem in celems:
            if type(celem) is not Wire:
                start = edgedict[celem][0]
                end = edgedict[celem][1]
                edges.append(GraphEdge(start, end, celem))
                nodes[start].add_edge(edges[-1])
                nodes[end].add_edge(edges[-1])

        return nodes, edges

    def graph_max_len_non_branching_paths(
        self,
    ) -> tuple[list[list[GraphEdge]], list[list[int]]]:
        """
        Naive algorithm for maximal non-branching paths in
        a graph from : https://rosalind.info/problems/ba3m/

        Basic principle : starts from any node not in the middle
        of a path (not 2 connexions) and finds all non-branching
        paths from here.

        It is adapted here naively for non directional graph
        by removing redundancy afterwards.

        Also returns start and end of each path.
        """
        paths: list[list[GraphEdge]] = []
        start_ends: list[list[int]] = []
        for i, node in enumerate(self.nodes):
            if len(node.edges) == 2:
                continue
            for edge in node.edges:
                non_branching_path: list[GraphEdge] = []
                non_branching_path.append(edge)
                if edge.start == i:
                    j = edge.end
                else:
                    j = edge.start
                node1 = self.nodes[j]
                prevedge = edge
                while len(node1.edges) == 2:
                    for e in node1.edges:
                        if prevedge is not e:
                            non_branching_path.append(e)
                            break
                    prevedge = non_branching_path[-1]
                    if prevedge.start != j:
                        j = prevedge.start
                    else:
                        j = prevedge.end
                    node1 = self.nodes[j]
                startend = [i, j]
                paths.append(non_branching_path)
                start_ends.append(startend)
        # Delete duplicates
        rem = []
        for i in range(len(paths)):
            path = paths[i]
            path.reverse()
            if path in paths[i + 1 :]:
                rem.append(i)
        rem.reverse()
        for i in rem:
            del paths[i]
            del start_ends[i]
        for path in paths:
            path.reverse()
        return paths, start_ends

    def delete_node_sources(
        self,
    ) -> None:
        """
        Method to remove annoying Source nodes that were
        used previously to define correctly the graph.

        Since they are no use to build the system (as they provide the
        same pressure as the node on the other side of the edge) we
        remove them and update edges accordingly.

        Results in "headless" edges that are connected to only one node,
        the other being -1.
        """
        rem = []
        for i, node in enumerate(self.nodes):
            if node.type == GraphNodeType.SOURCE:
                rem.append(i)
        rem.reverse()
        for i in rem:
            del self.nodes[i]
            for path in self.paths:
                for edge in path:
                    if edge.start == i:
                        edge.start = -1
                    if edge.end == i:
                        edge.end = -1
                    if edge.start > i:
                        edge.start -= 1
                    if edge.end > i:
                        edge.end -= 1
            for startend in self.start_ends:
                if startend[0] == i:
                    startend[0] = -1
                if startend[1] == i:
                    startend[1] = -1
                if startend[0] > i:
                    startend[0] -= 1
                if startend[1] > i:
                    startend[1] -= 1

    def get_nbQ(self) -> int:
        """
        Returns the number of flow unknowns in the graph.
        This is the number of paths in the graph.
        """
        return len(self.paths)

    def get_nbP(self) -> int:
        """
        Returns the number of pressure unknowns in the graph.
        This is the number of nodes in the graph.
        """
        return len(self.nodes)
