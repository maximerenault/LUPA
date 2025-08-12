from GUI.framebase import FrameBase
from tkinter import ttk
import tkinter as tk
import matplotlib
from exceptions.solveframeexceptions import BadNumberError
from solvers.circuitgraph import CircuitGraph
from solvers.circuitsolver import CircuitSolver
from utils.strings import check_strfloat_pos
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GUI.drawingboard import DrawingBoard

matplotlib.use("TkAgg")


class FrameSolve(ttk.Frame):
    """
    A class for choosing simulation parameters
    """

    def __init__(self, master: ttk.Frame, drbd: "DrawingBoard") -> None:
        super().__init__(master)
        self.rowconfigure((0, 2), weight=1)
        self.columnconfigure(0, weight=1)

        self.drbd = drbd
        self.csolver = CircuitSolver()
        self.elem = -1

        self.widget_configs = {
            "Clear": {
                "layout": {
                    "labpanel": {"type": "label", "grid": {"row": 0, "column": 0}}
                },
                "rowcol_weights": {
                    "rows": [0],
                    "rowweights": [1],
                    "cols": [0],
                    "colweights": [1],
                },
            },
            "Solver": {
                "layout": {
                    "labpanel": {
                        "type": "label",
                        "grid": {
                            "row": 0,
                            "column": 0,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labdt": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "timestep": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "labmaxtime": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "maxtime": {"type": "entry", "grid": {"row": 2, "column": 1}},
                    "labtimeint": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "time integration": {
                        "type": "combobox",
                        "grid": {"row": 3, "column": 1},
                    },
                    "Solve": {
                        "type": "button",
                        "grid": {
                            "row": 4,
                            "column": 0,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "ExportMat": {
                        "type": "button",
                        "grid": {
                            "row": 5,
                            "column": 0,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "SaveCSV": {
                        "type": "button",
                        "grid": {
                            "row": 6,
                            "column": 0,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1],
                    "colweights": [1],
                },
            },
        }

        self.label_options = {
            "labpanel": {"text": "Simulation parameters panel"},
            "labdt": {"text": "Timestep"},
            "labmaxtime": {"text": "Max time"},
            "labtimeint": {"text": "Integration scheme"},
        }

        self.entry_options = {
            "timestep": {
                "bindfunc": self.update_timestep,
                "insert": self.csolver.get_dt(),
            },
            "maxtime": {
                "bindfunc": self.update_maxtime,
                "insert": self.csolver.get_maxtime(),
            },
        }

        self.cbbox_options = {
            "time integration": {
                "values": self.csolver.time_integrations,
                "bindfunc": self.update_time_integration,
                "current": self.csolver.time_integrations.index(
                    self.csolver.time_integration
                ),
            },
        }

        self.plot_options = {
            "conn_mat": {"dpi": 100},
        }

        self.button_options = {
            "Solve": {"text": "Solve", "bindfunc": self.solve},
            "ExportMat": {"text": "Export matrices", "bindfunc": self.export_matrices},
            "SaveCSV": {"text": "Save to CSV", "bindfunc": self.save_csv},
        }

        self.widget_frame = FrameBase(self, {})
        self.update_widget_list("Solver")

    def update_timestep(self, stringvar: tk.StringVar) -> None:
        """
        Update timestep of simulation
        """
        dtstr = check_strfloat_pos(stringvar.get())
        stringvar.set(dtstr)
        if dtstr == "" or dtstr == ".":
            return
        try:
            dt = float(dtstr)
            self.csolver.set_dt(dt)
        except (ValueError, TypeError):
            raise BadNumberError(dtstr)

    def update_maxtime(self, stringvar: tk.StringVar) -> None:
        """
        Update max time of simulation
        """
        mtstr = check_strfloat_pos(stringvar.get())
        stringvar.set(mtstr)
        if mtstr == "" or mtstr == ".":
            return
        try:
            mt = float(mtstr)
            self.csolver.set_maxtime(mt)
        except (ValueError, TypeError):
            raise BadNumberError(mtstr)

    def update_time_integration(self, event: tk.Event) -> None:
        """
        Update time integration scheme
        """
        self.csolver.set_time_integration(event.widget.get())

    def solve(self) -> None:
        # Pre-solving operations : removing wires, creating readable graph
        if len(self.drbd.cgeom.nodes) == 0:
            tk.messagebox.showerror("Error", "No system to solve")
            return
        cgraph = CircuitGraph(self.drbd.cgeom.nodes, self.drbd.cgeom.elems)

        # Solving operations
        Paths, StartEnds = cgraph.graph_max_len_non_branching_paths()
        nbQ = len(Paths)
        nbP = len([n for n in cgraph.nodes if n.type != "Source"])
        cns = self.csolver.solve(nbP, nbQ, cgraph.nodes, Paths, StartEnds)
        if cns == 1:
            tk.messagebox.showerror("Error", "The problem is under constrained.")
            return
        if cns == 2:
            tk.messagebox.showerror("Error", "The problem is over constrained.")
            return
        return

    def save_csv(self) -> None:
        """
        Save the results to a CSV file.
        """
        main_window = self.master.master
        filename = main_window.filename.split(".")[0] + ".csv"
        try:
            self.csolver.save_to_csv(filename)
            tk.messagebox.showinfo("Success", f"Results saved to {filename}")
        except Exception as e:
            tk.messagebox.showerror("Error", "Failed to save results. " + str(e))

    def export_matrices(self) -> None:
        return

    def update_widget_list(self, key: str = "Clear") -> None:
        self.widget_frame.delete_all()
        del self.widget_frame
        config = self.widget_configs[key]
        self.widget_frame = FrameBase(
            self,
            config["layout"],
            self.label_options,
            self.entry_options,
            self.button_options,
            self.plot_options,
            self.cbbox_options,
        )
        self.widget_frame.grid(row=1, column=0, sticky="nsew")
        for i, row in enumerate(config["rowcol_weights"]["rows"]):
            w = config["rowcol_weights"]["rowweights"][i]
            self.widget_frame.rowconfigure(row, weight=w)
        for i, col in enumerate(config["rowcol_weights"]["cols"]):
            w = config["rowcol_weights"]["colweights"][i]
            self.widget_frame.columnconfigure(col, weight=w)
