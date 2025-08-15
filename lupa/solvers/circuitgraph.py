from lupa.elements.node import Node
from lupa.elements.wire import Wire
from lupa.elements.ground import Ground
from lupa.solvers.graphedge import GraphEdge
from lupa.solvers.graphnode import GraphNode
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

    def convert_circuit_to_graph(
        self, cnodes: list[Node], celems: list[Wire]
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        cnodes = sorted(cnodes)
        nodes, edges = [], []
        edgedict = {celem: [-1, -1] for celem in celems if type(celem) is not Wire}

        while len(cnodes) > 0:
            # extract first sublist of identical nodes
            idend = bisect_right(cnodes, cnodes[0])
            subcnodes = cnodes[0:idend]
            del cnodes[0:idend]

            nodes.append(GraphNode())
            idnode = len(nodes) - 1

            for cnode in subcnodes:
                if cnode.listened:
                    nodes[-1].listened = True
                    nodes[-1].listener_name = cnode.listener_name
                celem = cnode.elems[0]
                if type(celem) is Wire:
                    # if we reach a wire, we collapse it
                    otherend = celem.get_other_end(cnode)
                    if otherend.listened:
                        nodes[-1].listened = True
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
                    edgedict[celem][celem.get_node_id(cnode)] = idnode
                    if isinstance(celem, Ground) and celem.get_node_id(cnode) == 1:
                        nodes[-1].set_type("Source")

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
        Paths = []
        StartEnds = []
        for i, node in enumerate(self.nodes):
            if len(node.edges) != 2:
                for edge in node.edges:
                    startend = []
                    startend.append(i)
                    non_branching_path = []
                    non_branching_path.append(edge)
                    if edge.start != i:
                        i1 = edge.start
                    else:
                        i1 = edge.end
                    node1 = self.nodes[i1]
                    prevedge = edge
                    k = 0
                    while len(node1.edges) == 2:
                        for e in node1.edges:
                            if prevedge is not e:
                                non_branching_path.append(e)
                                break
                        prevedge = non_branching_path[-1]
                        if prevedge.start != i1:
                            i1 = prevedge.start
                        else:
                            i1 = prevedge.end
                        node1 = self.nodes[i1]
                        k += 1
                        if k == 10000:
                            print("Error in branching path ", node1)
                            return
                    startend.append(i1)
                    Paths.append(non_branching_path)
                    StartEnds.append(startend)
        # Delete duplicates
        rem = []
        for i in range(len(Paths)):
            path = Paths[i]
            path.reverse()
            if path in Paths[i + 1 :]:
                rem.append(i)
        rem.reverse()
        for i in rem:
            del Paths[i]
            del StartEnds[i]
        for path in Paths:
            path.reverse()
        return Paths, StartEnds
