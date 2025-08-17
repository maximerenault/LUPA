from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt

from lupa.core.graphedge import GraphEdge
from lupa.core.graphnode import GraphNode
from lupa.elements.ground import Ground


@dataclass
class Probes:
    """Holds probe metadata and provides plotting/export helpers.

    probed: mapping from state index -> display name
    signs: mapping from state index -> sign multiplier (+/-1 or 0)
    """

    probed: Dict[int, str]
    signs: Dict[int, int]
    nbP: int = 0
    nbQ: int = 0

    @staticmethod
    def build(
        nodes: List[GraphNode],
        paths: List[List[GraphEdge]],
        startends: List[List[int]],
    ) -> "Probes":
        nbP = len(nodes)
        nbQ = len(paths)
        probed: Dict[int, str] = {}
        signs: Dict[int, int] = {}
        # Node probes
        for i, node in enumerate(nodes):
            if node.probed:
                probed[i] = node.probe_name
        # Edge probes (flows)
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
                if getattr(edge.elem, "probed", 0) != 0:
                    signs[len(nodes) + i] = sign * int(edge.elem.probed)
                    probed[len(nodes) + i] = getattr(edge.elem, "probe_name", f"Q{i}")
                idP0 = idP1
        return Probes(probed=probed, signs=signs, nbP=nbP, nbQ=nbQ)

    def any(self) -> bool:
        return bool(self.probed)

    def apply_signs(self, arr: np.ndarray) -> np.ndarray:
        """Return a signed copy of the selected rows according to signs.

        Expects arr to be shaped (states, timesteps).
        """
        if not self.signs:
            # Nothing to change; return view of selected rows
            rows = [i for i in self.probed.keys()]
            return arr[rows]
        rows = []
        signed = []
        for idx in self.probed.keys():
            rows.append(idx)
            s = self.signs.get(idx, 1)
            signed.append(arr[idx] * s)
        return np.stack(signed, axis=0)

    def plot(self, solution: np.ndarray, dt: float, maxtime: float, nbP: int) -> int:
        """Plot probed signals from solution. Returns 0 on success, 1 if no probes."""
        if not self.probed:
            return 1
        t = np.linspace(0, maxtime, solution.shape[1])
        _, axs = plt.subplots(2)
        with_p = False
        with_q = False
        for key, name in self.probed.items():
            sig = self.signs.get(key, 1)
            if key < nbP:
                axs[0].plot(t, solution[key] * sig, label=name)
                with_p = True
            else:
                axs[1].plot(t, solution[key] * sig, label=name)
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

    def save_full(
        self,
        fname: str,
        solution: np.ndarray,
        dt: float,
        maxtime: float,
    ) -> None:
        names = ["Time"]
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
        sol = solution.copy()
        for idx, s in self.signs.items():
            sol[idx] = sol[idx] * s
        time = np.arange(0, maxtime + dt, dt)
        sol = np.vstack([time, sol])
        header = " ".join(names)
        np.savetxt(
            fname,
            sol.T,
            fmt="%.11g",
            delimiter="\t",
            newline="\n",
            header=header,
            footer="",
            comments="",
            encoding=None,
        )
        del sol

    def save_probed(
        self,
        fname: str,
        solution: np.ndarray,
        dt: float,
        maxtime: float,
    ) -> None:
        rows = [i for i in self.probed.keys()]
        time = np.arange(0, maxtime + dt, dt)
        sol = np.vstack([time] + [solution[i] * self.signs.get(i, 1) for i in rows])
        header = "Time " + " ".join([self.probed[i] for i in rows])
        np.savetxt(
            fname,
            sol.T,
            fmt="%.11g",
            delimiter="\t",
            newline="\n",
            header=header,
            footer="",
            comments="",
            encoding=None,
        )
        del sol
