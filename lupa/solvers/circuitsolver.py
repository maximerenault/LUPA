from typing import Generator
import numpy as np
from lupa.elements.capacitor import Capacitor
from lupa.elements.diode import Diode
from lupa.elements.ground import Ground
from lupa.elements.inductor import Inductor
from lupa.elements.psource import PSource
from lupa.elements.qsource import QSource
from lupa.elements.resistor import Resistor
from lupa.solvers.graphedge import GraphEdge
from lupa.solvers.graphnode import GraphNode
import matplotlib.pyplot as plt
from lupa.utils.calculator import calculate as calc, deriv_finite_diff as deriv
import copy


class CircuitSolver:
    def __init__(self) -> None:
        self.M1 = None  # Matrix for order 1 derivatives
        self.M0 = None  # Matrix for order 0 derivatives
        self.Source = None  # Vector for source terms
        self.LHS = None
        self.RHS = None
        self.nbP = 0
        self.nbQ = 0
        self.dt = 0.01
        self.maxtime = 10.0
        self.solution = None
        # Backwards Differentiation Formula
        self.time_integrations = ["BDF", "BDF2", "BDF3"]
        self.time_integration = self.time_integrations[1]
        self.update_source_dict = {}
        self.update_M0_dict = {}
        self.update_M1_dict = {}
        self.update_diode_dict = {}
        self.signs = {}
        self.listened = {}

    def set_dt(self, dt: float) -> None:
        self.dt = dt

    def get_dt(self) -> float:
        return self.dt

    def set_maxtime(self, maxtime: float) -> None:
        self.maxtime = maxtime

    def get_maxtime(self) -> float:
        return self.maxtime

    def set_time_integration(self, ti: str) -> None:
        self.time_integration = ti

    def export_full_solution(self, fname: str) -> None:
        names = []
        for i in range(self.nbP):
            try:
                names.append(self.listened[i])
            except KeyError:
                names.append("P" + str(i))
        for i in range(self.nbQ):
            try:
                names.append(self.listened[self.nbP + i])
            except KeyError:
                names.append("Q" + str(self.nbP + i))
        np.savetxt(
            fname,
            self.solution,
            fmt="%.11g",
            delimiter=" ",
            newline="\n",
            header=" ".join(names),
            footer="",
            comments="# ",
            encoding=None,
        )

    def export_listened_solution(self, fname: str) -> None:
        np.savetxt(
            fname,
            self.solution[[i for i in self.listened.keys()]],
            fmt="%.11g",
            delimiter=" ",
            newline="\n",
            header=" ".join([self.listened[i] for i in self.listened.keys()]),
            footer="",
            comments="# ",
            encoding=None,
        )

    def solve(
        self,
        nbP: int,
        nbQ: int,
        nodes: list[GraphNode],
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> int:
        """
        Method that takes all the steps to solve the system:
        - check solution existence necessary condition
        - adapts input data
        - allocates arrays
        - builds zero and first order differential matrices
        - builds source vector and give update dictionary for transient sources
        - takes steady state solution as initial state
        - builds LHS
        - solves LHS.x = RHS at each timestep
        """
        cns = self.check_no_solution(nbP, nbQ, paths, startends)
        if cns:
            return cns
        nodes, paths, startends = self.delete_node_sources(
            copy.deepcopy(nodes),
            copy.deepcopy(paths),
            copy.deepcopy(startends),
        )
        self.listened, self.signs = self.set_listeners(nodes, paths, startends)

        time = 0.0
        step = 0
        nb_step = int(self.maxtime / self.dt)
        self.nbP = nbP
        self.nbQ = nbQ
        self.M1 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.M0 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.Source = np.zeros((nbP + nbQ), dtype=float)
        self.solution = np.zeros((nbP + nbQ, nb_step + 1))

        self.update_diode_dict, self.update_M0_dict, self.update_M1_dict = (
            self.build_M0M1(nbP, paths, startends)
        )
        self.update_M0M1(time)
        self.update_source_dict = self.build_source(paths)
        self.update_source(time)

        if self.update_diode_dict != {}:
            self.recompute_diodes(-1)

        # Initializing with steady-state solution
        try:
            self.solution[:, :] = np.linalg.solve(self.M0, self.Source).reshape(-1, 1)
        except np.linalg.LinAlgError:
            self.solution[:, :] = 0
        self.build_LHS()

        while step < nb_step:
            time += self.dt
            self.update_source(time)
            if self.update_M0_dict != {} or self.update_M1_dict != {}:
                self.update_M0M1(time)
                self.build_LHS()
            self.build_RHS(step)
            self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
            if self.update_diode(step):
                self.build_LHS()
                try:
                    self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
                except np.linalg.LinAlgError:
                    self.recompute_diodes(step)
                    self.build_LHS()
                    self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
            step += 1

        for key in self.signs.keys():
            self.solution[key] *= self.signs[key]

        _, axs = plt.subplots(2)
        for key in self.listened.keys():
            if key < nbP:
                axs[0].plot(
                    np.linspace(0, self.maxtime, nb_step + 1),
                    self.solution[key],
                    label=self.listened[key],
                )
            else:
                axs[1].plot(
                    np.linspace(0, self.maxtime, nb_step + 1),
                    self.solution[key],
                    label=self.listened[key],
                )
        axs[0].legend()
        axs[1].legend()
        plt.show()

        return 0

    def build_M0M1(
        self, nbP: int, paths: list[list[GraphEdge]], startends: list[list[int]]
    ) -> tuple[dict, dict, dict]:
        """
        Build matrices for zero and first order derivatives
        of the unknown vector.
        """
        M1 = self.M1
        M0 = self.M0
        update_diode_dict = {}
        update_M0_dict = {}
        update_M1_dict = {}
        line = 0
        idQ = nbP
        for i, path in enumerate(paths):
            startend = startends[i]
            idP0 = startend[0]
            for edge in path:
                if idP0 == edge.start:
                    idP1 = edge.end
                else:
                    idP1 = edge.start
                if type(edge.elem) is Resistor:
                    # P = R * Q
                    if edge.elem.active:
                        update_M0_dict[line] = {
                            idQ: calc("-(" + edge.elem.get_value() + ")")
                        }
                    else:
                        M0[line, idQ] = -edge.elem.get_value()
                    M0[line, idP1] = -1
                    M0[line, idP0] = 1
                elif type(edge.elem) is Capacitor:
                    # Q = C * d(P0 - P1)/dt + dC/dt * (P0 - P1)
                    if edge.elem.active:
                        update_M0_dict[line] = {
                            idP1: deriv(calc("-(" + edge.elem.get_value() + ")")),
                            idP0: deriv(calc(edge.elem.get_value())),
                        }
                        update_M1_dict[line] = {
                            idP1: calc("-(" + edge.elem.get_value() + ")"),
                            idP0: calc(edge.elem.get_value()),
                        }
                    else:
                        M1[line, idP1] = -edge.elem.get_value()
                        M1[line, idP0] = edge.elem.get_value()
                    M0[line, idQ] = -1
                elif type(edge.elem) is Inductor:
                    # P = L * dQ/dt + dL/dt * Q
                    if edge.elem.active:
                        update_M0_dict[line] = {
                            idQ: deriv(calc("-(" + edge.elem.get_value() + ")"))
                        }
                        update_M1_dict[line] = {
                            idQ: calc("-(" + edge.elem.get_value() + ")"),
                        }
                    else:
                        M1[line, idQ] = -edge.elem.get_value()
                    M0[line, idP1] = -1
                    M0[line, idP0] = 1
                elif type(edge.elem) is Diode:
                    M0[line, idP1] = -1
                    M0[line, idP0] = 1
                    if idP0 == edge.start:
                        update_diode_dict[line] = [
                            True,  # True = Open
                            idP0,
                            idP1,
                            idQ,
                            1,  # 1 -> Q
                        ]
                    else:
                        update_diode_dict[line] = [
                            True,  # True = Open
                            idP0,
                            idP1,
                            idQ,
                            -1,  # -1 -> -Q
                        ]
                elif type(edge.elem) is Ground or type(edge.elem) is PSource:
                    idP1 = edge.start
                    M0[line, idP1] = 1
                elif type(edge.elem) is QSource:
                    if idP0 == edge.start:
                        M0[line, idQ] = -1
                    else:
                        M0[line, idQ] = 1
                    idP1 = edge.start
                else:
                    raise TypeError(
                        f"Unknown element type: {type(edge.elem)} in edge {edge}"
                    )
                idP0 = idP1
                line += 1
            idQ += 1
        # Branching equations
        arr = np.array(startends).flat
        unique, counts = np.unique(arr, return_counts=True)
        for i in range(len(counts)):
            if counts[i] > 1 and unique[i] != -1:
                idnode = unique[i]
                idQ = nbP
                for startend in startends:
                    if startend[0] == idnode:
                        M0[line, idQ] = -1
                    elif startend[1] == idnode:
                        M0[line, idQ] = 1
                    idQ += 1
                line += 1
        return update_diode_dict, update_M0_dict, update_M1_dict

    def update_M0M1(self, time: float) -> None:
        """
        Update M0 and M1 according to the live elements
        in update_M0_dict and update_M1_dict.
        """
        for line in self.update_M0_dict.keys():
            for col in self.update_M0_dict[line].keys():
                self.M0[line, col] = self.update_M0_dict[line][col](time)
        for line in self.update_M1_dict.keys():
            for col in self.update_M1_dict[line].keys():
                self.M1[line, col] = self.update_M1_dict[line][col](time)

    def set_diode(self, line: int, diode_open: bool, resistor: bool = False) -> None:
        """Sets the state of a diode to diode_open. Replaces it with a resistor if
        resistor is True.

        Args:
            line (int): Line of matrix to which the diode is linked
            diode_open (bool): State of the diode wanted
            resistor (bool, optional): Whether to replace the diode with a resistor.
                Defaults to False.
        """
        _, idP0, idP1, idQ, _ = self.update_diode_dict[line]
        self.update_diode_dict[line][0] = diode_open
        if resistor:
            self.M0[line, idP1] = -1
            self.M0[line, idP0] = 1
            self.M0[line, idQ] = -0.1
        elif diode_open:
            self.M0[line, idP1] = 1
            self.M0[line, idP0] = -1
            self.M0[line, idQ] = 0
        else:
            self.M0[line, idP1] = 0
            self.M0[line, idP0] = 0
            self.M0[line, idQ] = 1

    def update_diode(self, step: int) -> bool:
        """Updates the state of a diode according to the flow passing trough
        or the difference in potential between start and end.

        Args:
            step (int): step of the solution to check

        Returns:
            bool: Whether an update was made or not
        """
        recompute = False
        for line in self.update_diode_dict.keys():
            diode_open, idP0, idP1, idQ, signQ = self.update_diode_dict[line]
            if diode_open:
                Q = self.solution[idQ, step + 1]
                if signQ * Q < 0:
                    self.set_diode(line, diode_open=False)
                    recompute = True
            else:
                P0 = self.solution[idP0, step + 1]
                P1 = self.solution[idP1, step + 1]
                if signQ * (P0 - P1) > 0:
                    self.set_diode(line, diode_open=True)
                    recompute = True
        return recompute

    def try_diode_positions(self) -> Generator[None, None, None]:
        """DEPRECATED.
        Try diode positions in order following binary counting.

        Yields:
            Generator[None, None, None]: Nothing
        """
        lines = [line for line in self.update_diode_dict.keys()]
        n = len(lines)

        for b in range(1 << n):
            # Change list of True/False "not intelligently"
            s = bin(b)[2:].zfill(n)
            diode_pos = map(lambda x: not bool(int(x)), list(s))
            for line in lines:
                diode_open = next(diode_pos)
                self.set_diode(line, diode_open)
            yield

    def recompute_diodes(self, step: int) -> None:
        """Replaces diodes with resistors and finds out the flow
        direction to deduce the actual state of the diodes.

        Args:
            step (int): Step of the simulation
        """
        for line in self.update_diode_dict:
            self.set_diode(line, False, True)
        self.build_LHS()
        self.build_RHS(step)
        self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
        self.update_diode(step)

    def build_source(self, paths: list[list[GraphEdge]]) -> dict:
        """
        Build live sources dict from list of paths.
        """
        update_source_dict = {}
        line = 0
        for path in paths:
            for edge in path:
                if type(edge.elem) is PSource or type(edge.elem) is QSource:
                    if edge.elem.active:
                        update_source_dict[line] = calc(edge.elem.get_value())
                    else:
                        self.Source[line] = edge.elem.get_value()
                line += 1
        return update_source_dict

    def update_source(self, time: float) -> None:
        """
        Update source vector according to the live sources
        in update_source_dict.
        """
        for line in self.update_source_dict.keys():
            self.Source[line] = self.update_source_dict[line](time)

    def build_LHS(self) -> None:
        """
        Build left hand side of the equation.
        """
        if self.time_integration == "BDF":
            self.LHS = self.M0 + self.M1 / self.dt
        elif self.time_integration == "BDF2":
            self.LHS = self.M0 + 3 * self.M1 / (2 * self.dt)
        elif self.time_integration == "BDF3":
            self.LHS = self.M0 + 11 * self.M1 / (6 * self.dt)
        else:
            raise ValueError(
                f"Unknown time integration method: {self.time_integration}"
            )
        return

    def build_RHS(self, step: int) -> None:
        """
        Build right hand side of the equation.
        """
        if self.time_integration == "BDF":
            self.RHS = self.Source + np.matmul(
                self.M1, self.solution[:, step] / self.dt
            )
        elif self.time_integration == "BDF2":
            self.RHS = self.Source + np.matmul(
                self.M1,
                (4 * self.solution[:, step] - self.solution[:, step - 1])
                / (2 * self.dt),
            )
        elif self.time_integration == "BDF3":
            self.RHS = self.Source + np.matmul(
                self.M1,
                (
                    18 * self.solution[:, step]
                    - 9 * self.solution[:, step - 1]
                    + 2 * self.solution[:, step - 2]
                )
                / (6 * self.dt),
            )
        else:
            raise ValueError(
                f"Unknown time integration method: {self.time_integration}"
            )
        return

    def check_no_solution(
        self,
        nbP: int,
        nbQ: int,
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> int:
        """
        Check if the problem has a solution.
        0 : OK
        1 : under constrained
        2 : over constrained
        """
        c = 0
        # Count equations from elements
        for path in paths:
            for _ in path:
                c += 1
        # Count equations from branching
        arr = np.array(startends).flat
        _, counts = np.unique(arr, return_counts=True)
        for count in counts:
            if count > 1:
                c += 1
        # Compare with number of unknowns
        if c > nbP + nbQ:
            return 2
        if c < nbP + nbQ:
            return 1
        return 0

    def delete_node_sources(
        self,
        nodes: list[GraphNode],
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> tuple[list[GraphNode], list[list[GraphEdge]], list[list[int]]]:
        """
        Method to remove annoying "Source" nodes that were
        used previously to define correctly the graph.

        Since they are no use to build the system (as they provide the
        same pressure as the node on the other side of the edge) we
        remove them and update edges accordingly.
        """
        rem = []
        for i, node in enumerate(nodes):
            if node.type == "Source":
                rem.append(i)
        rem.reverse()
        for i in rem:
            del nodes[i]
            for path in paths:
                for edge in path:
                    if edge.start == i:
                        edge.start = -1
                    if edge.end == i:
                        edge.end = -1
                    if edge.start > i:
                        edge.start -= 1
                    if edge.end > i:
                        edge.end -= 1
            for startend in startends:
                if startend[0] == i:
                    startend[0] = -1
                if startend[1] == i:
                    startend[1] = -1
                if startend[0] > i:
                    startend[0] -= 1
                if startend[1] > i:
                    startend[1] -= 1
        return nodes, paths, startends

    def set_listeners(
        self,
        nodes: list[GraphNode],
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> tuple[dict, dict]:
        """
        Set the listeners for the nodes and edges.
        """
        listened = {}
        signs = {}
        for i, node in enumerate(nodes):
            if node.listened:
                listened[i] = node.listener_name
        for i, path in enumerate(paths):
            startend = startends[i]
            idP0 = startend[0]
            for edge in path:
                if idP0 == edge.start:
                    idP1 = edge.end
                    sign = 1
                else:
                    idP1 = edge.start
                    sign = -1
                if isinstance(edge.elem, Ground):
                    idP1 = edge.start
                if edge.elem.listened != 0:
                    signs[len(nodes) + i] = sign * edge.elem.listened
                    listened[len(nodes) + i] = edge.elem.listener_name
                idP0 = idP1
        return listened, signs

    def save_to_csv(self, filename: str) -> None:
        """
        Save the circuit solver's listened solution to a CSV file.
        """
        with open(filename, "w") as f:
            f.write("Time," + ",".join(self.listened.values()) + "\n")
            for i in range(self.solution.shape[1]):
                f.write(
                    str(i * self.dt)
                    + ","
                    + ",".join(
                        [str(self.solution[key, i]) for key in self.listened.keys()]
                    )
                    + "\n"
                )
