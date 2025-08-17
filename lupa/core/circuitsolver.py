from lupa.exceptions.circuitsolverexceptions import (
    OverconstrainedError,
    UnderconstrainedError,
)
from lupa.elements.capacitor import Capacitor
from lupa.elements.diode import Diode
from lupa.elements.ground import Ground
from lupa.elements.inductor import Inductor
from lupa.elements.psource import PSource
from lupa.elements.qsource import QSource
from lupa.elements.resistor import Resistor
from lupa.core.graphedge import GraphEdge
from lupa.core.graphnode import GraphNode, GraphNodeType
from lupa.core.timeintegration import TimeIntegration, get_system_builders
from lupa.utils.calculator import calculate as calc, deriv_finite_diff as deriv
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
from enum import Enum
import copy

DIODE_RESISTOR_SUBSTITUTE = 0.1


class DIODE_STATE(Enum):
    OPEN = 0
    CLOSED = 1
    RESISTOR = 2


@dataclass
class DiodeContainer:
    state: DIODE_STATE
    idP0: int
    idP1: int
    idQ: int
    signQ: int


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
        self.set_time_integration(TimeIntegration.BDF2.value)
        self.update_source_dict = {}
        self.update_M0_dict = {}
        self.update_M1_dict = {}
        self.update_diode_dict: dict[int, DiodeContainer] = {}
        self.signs = {}
        self.probed = {}

    def set_dt(self, dt: float) -> None:
        self.dt = dt

    def get_dt(self) -> float:
        return self.dt

    def set_maxtime(self, maxtime: float) -> None:
        self.maxtime = maxtime

    def get_maxtime(self) -> float:
        return self.maxtime

    def set_time_integration(self, ti: str) -> None:
        try:
            self.time_integration = TimeIntegration(ti)
            self.LHS_builder, self.RHS_builder = get_system_builders(
                self.time_integration
            )
        except ValueError:
            raise ValueError(f"Unknown time integration method: {ti}")

    def export_full_solution(self, fname: str) -> None:
        names = []
        for i in range(self.nbP):
            try:
                names.append(self.probed[i])
            except KeyError:
                names.append("P" + str(i))
        for i in range(self.nbQ):
            try:
                names.append(self.probed[self.nbP + i])
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

    def export_probed_solution(self, fname: str) -> None:
        np.savetxt(
            fname,
            self.solution[[i for i in self.probed.keys()]],
            fmt="%.11g",
            delimiter=" ",
            newline="\n",
            header=" ".join([self.probed[i] for i in self.probed.keys()]),
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
    ) -> None:
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
        nodes, paths, startends = self.delete_node_sources(
            copy.deepcopy(nodes),
            copy.deepcopy(paths),
            copy.deepcopy(startends),
        )
        self.check_no_solution(nbP, nbQ, paths, startends)
        self.probed, self.signs = self.set_probes(nodes, paths, startends)

        time = 0.0
        step = 0
        nb_step = int(self.maxtime / self.dt)
        self.nbP = nbP
        self.nbQ = nbQ
        self.M1 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.M0 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.Source = np.zeros((nbP + nbQ), dtype=float)
        self.solution = np.zeros((nbP + nbQ, nb_step + 1))

        self.build_M0M1(nbP, paths, startends)
        self.update_M0M1(time)
        self.build_source(paths)
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

    def build_M0M1(
        self, nbP: int, paths: list[list[GraphEdge]], startends: list[list[int]]
    ) -> None:
        """
        Build matrices for zero and first derivatives of the state vector.
        """
        row = 0
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
                    self.build_resistor(edge.elem, row, idP0, idP1, idQ)
                elif type(edge.elem) is Capacitor:
                    self.build_capacitor(edge.elem, row, idP0, idP1, idQ)
                elif type(edge.elem) is Inductor:
                    self.build_inductor(edge.elem, row, idP0, idP1, idQ)
                elif type(edge.elem) is Diode:
                    self.build_diode(row, idP0, idP1, idQ, edge.start)
                elif isinstance(edge.elem, Ground):
                    self.build_ground(edge.elem, row, idP0, idQ, edge.start)
                    idP1 = edge.start
                else:
                    raise TypeError(
                        f"Unknown element type: {type(edge.elem)} in edge {edge}"
                    )
                idP0 = idP1
                row += 1
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
                        self.M0[row, idQ] = -1
                    elif startend[1] == idnode:
                        self.M0[row, idQ] = 1
                    idQ += 1
                row += 1

    def build_resistor(
        self, elem: Resistor, row: int, idP0: int, idP1: int, idQ: int
    ) -> None:
        """
        R * Q - (P0 - P1) = 0
        """
        value = elem.get_value()
        if elem.active:
            self.update_M0_dict[row] = {idQ: calc(value)}
        else:
            self.M0[row, idQ] = value
        self.M0[row, idP1] = 1
        self.M0[row, idP0] = -1

    def build_capacitor(
        self, elem: Capacitor, row: int, idP0: int, idP1: int, idQ: int
    ) -> None:
        """
        C * d(P0 - P1)/dt + dC/dt * (P0 - P1) - Q = 0
        """
        value = elem.get_value()
        if elem.active:
            self.update_M0_dict[row] = {
                idP1: deriv(calc("-(" + value + ")")),
                idP0: deriv(calc(value)),
            }
            self.update_M1_dict[row] = {
                idP1: calc("-(" + value + ")"),
                idP0: calc(value),
            }
        else:
            self.M1[row, idP1] = -value
            self.M1[row, idP0] = value
        self.M0[row, idQ] = -1

    def build_inductor(
        self, elem: Inductor, row: int, idP0: int, idP1: int, idQ: int
    ) -> None:
        """
        L * dQ/dt + dL/dt * Q - (P0 - P1) = 0
        """
        value = elem.get_value()
        if elem.active:
            self.update_M0_dict[row] = {idQ: deriv(calc(value))}
            self.update_M1_dict[row] = {idQ: calc(value)}
        else:
            self.M1[row, idQ] = value
        self.M0[row, idP1] = 1
        self.M0[row, idP0] = -1

    def build_diode(self, row: int, idP0: int, idP1: int, idQ: int, start: int) -> None:
        self.M0[row, idP1] = -1
        self.M0[row, idP0] = 1
        if idP0 == start:
            self.update_diode_dict[row] = DiodeContainer(
                DIODE_STATE.OPEN, idP0, idP1, idQ, 1
            )
        else:
            self.update_diode_dict[row] = DiodeContainer(
                DIODE_STATE.OPEN, idP0, idP1, idQ, -1
            )

    def build_ground(
        self, elem: Ground, row: int, idP0: int, idQ: int, start: int
    ) -> None:
        if type(elem) is Ground or type(elem) is PSource:
            self.M0[row, start] = 1
        elif type(elem) is QSource:
            if idP0 == start:
                self.M0[row, idQ] = -1
            else:
                self.M0[row, idQ] = 1

    def update_M0M1(self, time: float) -> None:
        """
        Update M0 and M1 according to the live elements
        in update_M0_dict and update_M1_dict.
        """
        for row, cols in self.update_M0_dict.items():
            for col, fn in cols.items():
                self.M0[row, col] = fn(time)
        for row, cols in self.update_M1_dict.items():
            for col, fn in cols.items():
                self.M1[row, col] = fn(time)

    def set_diode(self, row: int, diode_state: DIODE_STATE) -> None:
        """Sets the state of a diode to diode_state.

        Args:
            row (int): Row of matrix to which the diode is linked
            diode_state (DIODE_STATE): State of the diode wanted
        """
        self.update_diode_dict[row].state = diode_state
        dc = self.update_diode_dict[row]
        idP0 = dc.idP0
        idP1 = dc.idP1
        idQ = dc.idQ
        if diode_state == DIODE_STATE.RESISTOR:
            self.M0[row, idP1] = -1
            self.M0[row, idP0] = 1
            self.M0[row, idQ] = -DIODE_RESISTOR_SUBSTITUTE
        elif diode_state == DIODE_STATE.OPEN:
            self.M0[row, idP1] = 1
            self.M0[row, idP0] = -1
            self.M0[row, idQ] = 0
        else:
            self.M0[row, idP1] = 0
            self.M0[row, idP0] = 0
            self.M0[row, idQ] = 1

    def update_diode(self, step: int) -> bool:
        """Updates the state of a diode according to the flow passing trough
        or the difference in potential between start and end.

        Args:
            step (int): step of the solution to check

        Returns:
            bool: Whether an update was made or not
        """
        recompute = False
        for row, dc in self.update_diode_dict.items():
            if dc.state == DIODE_STATE.OPEN:
                Q = self.solution[dc.idQ, step + 1]
                if dc.signQ * Q < 0:
                    self.set_diode(row, DIODE_STATE.CLOSED)
                    recompute = True
            else:
                P0 = self.solution[dc.idP0, step + 1]
                P1 = self.solution[dc.idP1, step + 1]
                if dc.signQ * (P0 - P1) > 0:
                    self.set_diode(row, DIODE_STATE.OPEN)
                    recompute = True
        return recompute

    def recompute_diodes(self, step: int) -> None:
        """Replaces diodes with resistors and finds out the flow
        direction to deduce the actual state of the diodes.

        Args:
            step (int): Step of the simulation
        """
        for row in self.update_diode_dict:
            self.set_diode(row, DIODE_STATE.RESISTOR)
        self.build_LHS()
        self.build_RHS(step)
        self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
        self.update_diode(step)

    def build_source(self, paths: list[list[GraphEdge]]) -> None:
        """
        Build live sources dict from list of paths.
        """
        row = 0
        for path in paths:
            for edge in path:
                if type(edge.elem) is PSource or type(edge.elem) is QSource:
                    if edge.elem.active:
                        self.update_source_dict[row] = calc(edge.elem.get_value())
                    else:
                        self.Source[row] = edge.elem.get_value()
                row += 1

    def update_source(self, time: float) -> None:
        """
        Update source vector according to the live sources
        in update_source_dict.
        """
        for row, fn in self.update_source_dict.items():
            self.Source[row] = fn(time)

    def build_LHS(self) -> None:
        """
        Build left hand side of the equation.
        """
        self.LHS = self.LHS_builder(self.M1, self.M0, self.dt)

    def build_RHS(self, step: int) -> None:
        """
        Build right hand side of the equation.
        """
        self.RHS = self.RHS_builder(self.M1, self.Source, self.dt, step, self.solution)

    def check_no_solution(
        self,
        nbP: int,
        nbQ: int,
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> None:
        """
        Check if the problem has a solution.
        """
        c = 0
        # Count equations from elements
        for path in paths:
            for _ in path:
                c += 1
        # Count equations from branching
        arr = np.array(startends).flat
        uniques, counts = np.unique(arr, return_counts=True)
        for unique, count in zip(uniques, counts):
            if count > 1 and unique != -1:
                c += 1
        # Compare with number of unknowns
        if c > nbP + nbQ:
            raise OverconstrainedError(c, nbP + nbQ)
        elif c < nbP + nbQ:
            raise UnderconstrainedError(c, nbP + nbQ)

    def delete_node_sources(
        self,
        nodes: list[GraphNode],
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> tuple[list[GraphNode], list[list[GraphEdge]], list[list[int]]]:
        """
        Method to remove annoying Source nodes that were
        used previously to define correctly the graph.

        Since they are no use to build the system (as they provide the
        same pressure as the node on the other side of the edge) we
        remove them and update edges accordingly.
        """
        rem = []
        for i, node in enumerate(nodes):
            if node.type == GraphNodeType.SOURCE:
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

    def set_probes(
        self,
        nodes: list[GraphNode],
        paths: list[list[GraphEdge]],
        startends: list[list[int]],
    ) -> tuple[dict, dict]:
        """
        Set the probes for the nodes and edges.
        """
        probed = {}
        signs = {}
        for i, node in enumerate(nodes):
            if node.probed:
                probed[i] = node.probe_name
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
                if edge.elem.probed != 0:
                    signs[len(nodes) + i] = sign * edge.elem.probed
                    probed[len(nodes) + i] = edge.elem.probe_name
                idP0 = idP1
        return probed, signs

    def plot_probes(self) -> int:
        """
        Plot the probes defined in the circuit.
        """
        if not self.probed:
            return 1

        _, axs = plt.subplots(2)
        with_p = False
        with_q = False
        for key in self.probed.keys():
            if key < self.nbP:
                axs[0].plot(
                    np.linspace(0, self.maxtime, self.solution.shape[1]),
                    self.solution[key],
                    label=self.probed[key],
                )
                with_p = True
            else:
                axs[1].plot(
                    np.linspace(0, self.maxtime, self.solution.shape[1]),
                    self.solution[key],
                    label=self.probed[key],
                )
                with_q = True
        if with_p:
            axs[0].set_xlabel("Time")
            axs[0].set_ylabel("Pressure")
            axs[0].legend()
        if with_q:
            axs[1].set_xlabel("Time")
            axs[1].set_ylabel("Flow")
            axs[1].legend()
        plt.suptitle("Circuit Solver Probes")
        plt.tight_layout()
        plt.show()
        return 0

    def save_to_csv(self, filename: str) -> None:
        """
        Save the circuit solver's probed solution to a CSV file.
        """
        with open(filename, "w") as f:
            f.write("Time," + ",".join(self.probed.values()) + "\n")
            for i in range(self.solution.shape[1]):
                f.write(
                    str(i * self.dt)
                    + ","
                    + ",".join(
                        [str(self.solution[key, i]) for key in self.probed.keys()]
                    )
                    + "\n"
                )
