from GUI.framebase import FrameBase
from utils.io import readvalues
import numpy as np
from tkinter import ttk
import tkinter as tk
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from elements.ground import Ground
from elements.psource import PSource
from elements.diode import Diode
from exceptions.attibutesexceptions import BadNumberError
from exceptions.calculatorexceptions import CalculatorException
from utils.strings import check_strint
import matplotlib
import utils.calculator as calc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GUI.drawingboard import DrawingBoard

matplotlib.use("TkAgg")


class FrameAttributes(ttk.Frame):
    """
    A class for displaying info about an element
    and editing it
    """

    def __init__(self, master: ttk.Frame, drbd: "DrawingBoard") -> None:
        ttk.Frame.__init__(self, master)
        self.rowconfigure((0, 2), weight=1)
        self.columnconfigure(0, weight=1)

        self.widget_configs = {
            "Clear": {
                "layout": {"clear": {"type": "label", "grid": {"row": 0, "column": 0}}},
                "rowcol_weights": {
                    "rows": [0],
                    "rowweights": [1],
                    "cols": [0],
                    "colweights": [1],
                },
            },
            "Wire": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {
                        "type": "entry",
                        "grid": {
                            "row": 0,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "lablistenPstart": {
                        "type": "label",
                        "grid": {"row": 2, "column": 0},
                    },
                    "listenPstart": {
                        "type": "checkbox",
                        "grid": {"row": 2, "column": 1},
                    },
                    "labend": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "endx": {"type": "entry", "grid": {"row": 3, "column": 1}},
                    "endy": {"type": "entry", "grid": {"row": 3, "column": 2}},
                    "lablistenPend": {"type": "label", "grid": {"row": 4, "column": 0}},
                    "listenPend": {"type": "checkbox", "grid": {"row": 4, "column": 1}},
                    "lablistenQ": {"type": "label", "grid": {"row": 5, "column": 0}},
                    "listenQ": {
                        "type": "radio",
                        "grid": {
                            "row": 5,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "delete": {
                        "type": "button",
                        "grid": {
                            "row": 6,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1, 2],
                    "colweights": [1, 1],
                },
            },
            "Dipole": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {
                        "type": "entry",
                        "grid": {
                            "row": 0,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "lablistenPstart": {
                        "type": "label",
                        "grid": {"row": 2, "column": 0},
                    },
                    "listenPstart": {
                        "type": "checkbox",
                        "grid": {"row": 2, "column": 1},
                    },
                    "labend": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "endx": {"type": "entry", "grid": {"row": 3, "column": 1}},
                    "endy": {"type": "entry", "grid": {"row": 3, "column": 2}},
                    "lablistenPend": {"type": "label", "grid": {"row": 4, "column": 0}},
                    "listenPend": {"type": "checkbox", "grid": {"row": 4, "column": 1}},
                    "lablistenQ": {"type": "label", "grid": {"row": 5, "column": 0}},
                    "listenQ": {
                        "type": "radio",
                        "grid": {
                            "row": 5,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labval": {"type": "label", "grid": {"row": 6, "column": 0}},
                    "value": {
                        "type": "entry",
                        "grid": {
                            "row": 6,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "read": {
                        "type": "button",
                        "grid": {
                            "row": 7,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                    "delete": {
                        "type": "button",
                        "grid": {
                            "row": 8,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1, 2],
                    "colweights": [1, 1],
                },
            },
            "DipoleSource": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {
                        "type": "entry",
                        "grid": {
                            "row": 0,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "lablistenPstart": {
                        "type": "label",
                        "grid": {"row": 2, "column": 0},
                    },
                    "listenPstart": {
                        "type": "checkbox",
                        "grid": {"row": 2, "column": 1},
                    },
                    "labend": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "endx": {"type": "entry", "grid": {"row": 3, "column": 1}},
                    "endy": {"type": "entry", "grid": {"row": 3, "column": 2}},
                    "lablistenPend": {"type": "label", "grid": {"row": 4, "column": 0}},
                    "listenPend": {"type": "checkbox", "grid": {"row": 4, "column": 1}},
                    "lablistenQ": {"type": "label", "grid": {"row": 5, "column": 0}},
                    "listenQ": {
                        "type": "radio",
                        "grid": {
                            "row": 5,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labval": {"type": "label", "grid": {"row": 6, "column": 0}},
                    "value": {
                        "type": "entry",
                        "grid": {
                            "row": 6,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "source": {
                        "type": "plot",
                        "grid": {
                            "row": 7,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                    "read": {
                        "type": "button",
                        "grid": {
                            "row": 8,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                    "delete": {
                        "type": "button",
                        "grid": {
                            "row": 9,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1, 2],
                    "colweights": [1, 1],
                },
            },
            "Ground": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {
                        "type": "entry",
                        "grid": {
                            "row": 0,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "labdir": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "direct": {
                        "type": "combobox",
                        "grid": {
                            "row": 2,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "delete": {
                        "type": "button",
                        "grid": {
                            "row": 3,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1, 2],
                    "colweights": [1, 1],
                },
            },
            "Source": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {
                        "type": "entry",
                        "grid": {
                            "row": 0,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "labdir": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "direct": {
                        "type": "combobox",
                        "grid": {
                            "row": 2,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "labval": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "value": {
                        "type": "entry",
                        "grid": {
                            "row": 3,
                            "column": 1,
                            "columnspan": 2,
                            "sticky": "ew",
                        },
                    },
                    "source": {
                        "type": "plot",
                        "grid": {
                            "row": 4,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                    "read": {
                        "type": "button",
                        "grid": {
                            "row": 5,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                    "delete": {
                        "type": "button",
                        "grid": {
                            "row": 6,
                            "column": 0,
                            "columnspan": 3,
                            "sticky": "ew",
                        },
                    },
                },
                "rowcol_weights": {
                    "rows": [],
                    "rowweights": [],
                    "cols": [1, 2],
                    "colweights": [1, 1],
                },
            },
        }

        self.label_options = {
            "labnam": {"text": "Name"},
            "labval": {"text": "Value"},
            "labsta": {"text": "Start"},
            "lablistenPstart": {"text": "Listen P"},
            "lablistenPend": {"text": "Listen P"},
            "lablistenQ": {"text": "Listen Q"},
            "labend": {"text": "End"},
            "labdir": {"text": "Direction"},
            "clear": {"text": "Attributes edition panel"},
        }

        self.entry_options = {
            "name": {"bindfunc": self.update_name, "insert": ""},
            "value": {"bindfunc": self.update_value, "insert": ""},
            "startx": {
                "bindfunc": lambda stringvar: self.update_coords(
                    stringvar, "start", "x"
                ),
                "insert": "",
            },
            "starty": {
                "bindfunc": lambda stringvar: self.update_coords(
                    stringvar, "start", "y"
                ),
                "insert": "",
            },
            "endx": {
                "bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "x"),
                "insert": "",
            },
            "endy": {
                "bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "y"),
                "insert": "",
            },
        }

        self.cbbox_options = {
            "direct": {
                "values": ["S", "E", "N", "W"],
                "bindfunc": self.update_direction,
            },
        }

        self.plot_options = {"source": {"dpi": 100, "xy": ([0, 1], [0, 1])}}

        self.button_options = {
            "read": {"text": "Read file", "bindfunc": self.read_values},
            "delete": {"text": "Delete", "bindfunc": self.delete_elem},
        }

        self.checkbox_options = {
            "listenPstart": {
                "text": "on/off",
                "onoff": 0,
                "command": lambda var: self.set_listenP(0, var),
            },
            "listenPend": {
                "text": "on/off",
                "onoff": 0,
                "command": lambda var: self.set_listenP(1, var),
            },
        }

        self.radio_options = {
            "listenQ": {
                "texts": ["off", "Q", "-Q"],
                "values": [0, 1, -1],
                "value": 0,
                "command": self.set_listenQ,
            },
        }

        self.widget_frame = FrameBase(self, {})
        self.update_widget_list()

        self.drbd = drbd
        self.elem = -1

    def update_name(self, stringvar: tk.StringVar) -> None:
        """
        Update name of the object and
        display it
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el: Wire = self.drbd.cgeom.elems[self.elem]
        el.name = stringvar.get()
        el.redrawname(self.drbd)

    def update_coords(self, stringvar: tk.StringVar, pos: str, comp: str) -> None:
        """
        Updates start or end coords of the object
        with id self.elem
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el: Wire = self.drbd.cgeom.elems[self.elem]
        coords = el.getcoords()
        newcoord = check_strint(stringvar.get())
        stringvar.set(newcoord)
        if newcoord == "" or newcoord == "-":
            return
        try:
            newcoordint = int(newcoord)
        except (ValueError, TypeError):
            raise BadNumberError(newcoord)
        if pos == "start":
            if comp == "x":
                el.setstart(newcoordint, coords[1])
            elif comp == "y":
                el.setstart(coords[0], newcoordint)
        elif pos == "end":
            if comp == "x":
                el.setend(newcoordint, coords[3])
            elif comp == "y":
                el.setend(coords[2], newcoordint)
        newcoords = el.getcoords()
        if (newcoords[:2] == newcoords[2:]).all():
            el.setstart(coords[0], coords[1])
            el.setend(coords[2], coords[3])
            return
        el.redraw(self.drbd)

    def update_value(self, stringvar: tk.StringVar) -> None:
        """
        Updates value for dipole elements
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el: Wire = self.drbd.cgeom.elems[self.elem]
        err = el.set_value(stringvar.get())
        if err:
            self.widget_frame.entries["value"].config(bg="orange red")
        else:
            self.widget_frame.entries["value"].config(bg="white")

    def read_values(self) -> None:
        """
        Allows for opening a csv file
        with columns time and value,
        with sep='\t'
        """
        file_name = tk.filedialog.askopenfilename()
        if file_name:
            x, y = readvalues(file_name)
            el: Wire = self.drbd.cgeom.elems[self.elem]
            el.set_source(x, y)
            self.update_attributes()

    def update_direction(self, event: tk.Event) -> None:
        """
        Update source-type element direction
        """
        el: Wire = self.drbd.cgeom.elems[self.elem]
        coords = el.getcoords()
        dirx = event.widget.get()
        if dirx == "S":
            el.setend(coords[0], coords[1] - 1)
        elif dirx == "E":
            el.setend(coords[0] + 1, coords[1])
        elif dirx == "N":
            el.setend(coords[0], coords[1] + 1)
        elif dirx == "W":
            el.setend(coords[0] - 1, coords[1])
        el.redraw(self.drbd)

    def set_listenP(self, pos: str, var: tk.StringVar) -> None:
        """
        Change pressure listening from True to False
        and the other way around.
        """
        el: Wire = self.drbd.cgeom.elems[self.elem]
        val = var.get()
        el.set_listenP(pos, val, self.drbd)
        el.redraw(self.drbd)

    def set_listenQ(self, var: tk.StringVar) -> None:
        """
        Set Q listening flag to 0 if off, 1 if same direction
        as elem, -1 otherwise.
        """
        el: Wire = self.drbd.cgeom.elems[self.elem]
        val = var.get()
        el.set_listenQ(val, self.drbd)
        el.redraw(self.drbd)

    def delete_elem(self) -> None:
        """
        Calls deleteElement from the
        drawing board and resets attributes.
        """
        if self.elem == -1:
            self.update_attributes()
            return
        self.drbd.deleteElement(self.elem)
        self.elem = -1
        self.update_attributes()

    def change_elem(self, id: int) -> None:
        """
        Interface function for other modules
        to change the element selected

        id : int, unique id number of the element
        """
        self.elem = id
        self.update_attributes()

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
            self.checkbox_options,
            self.radio_options,
        )
        self.widget_frame.grid(row=1, column=0, sticky="nsew")
        for i, row in enumerate(config["rowcol_weights"]["rows"]):
            w = config["rowcol_weights"]["rowweights"][i]
            self.widget_frame.rowconfigure(row, weight=w)
        for i, col in enumerate(config["rowcol_weights"]["cols"]):
            w = config["rowcol_weights"]["colweights"][i]
            self.widget_frame.columnconfigure(col, weight=w)

    def update_attributes(self) -> None:
        if self.elem == -1:
            self.update_widget_list()
            return

        el: Wire = self.drbd.cgeom.elems[self.elem]

        if (
            isinstance(el, Resistor)
            or isinstance(el, Inductor)
            or isinstance(el, Capacitor)
        ):
            elemtype = "Dipole"
        elif type(el) is Wire or type(el) is Diode:
            elemtype = "Wire"
        elif isinstance(el, PSource):
            elemtype = "Source"
        elif isinstance(el, Ground):
            elemtype = "Ground"
        else:
            raise "No idea what this object is"

        coords = el.getcoords()
        self.entry_options["name"]["insert"] = el.name
        self.entry_options["value"]["insert"] = el.value
        self.entry_options["startx"]["insert"] = int(coords[0])
        self.entry_options["starty"]["insert"] = int(coords[1])
        self.entry_options["endx"]["insert"] = int(coords[2])
        self.entry_options["endy"]["insert"] = int(coords[3])

        self.checkbox_options["listenPstart"]["onoff"] = int(el.get_listenP(0))
        self.checkbox_options["listenPend"]["onoff"] = int(el.get_listenP(1))
        self.radio_options["listenQ"]["value"] = int(el.get_listenQ())

        if el.active:
            try:
                maxt = self.drbd.frameSolve.csolver.get_maxtime()
                dt = self.drbd.frameSolve.csolver.get_dt()
                x = np.arange(0, maxt + dt, dt)
                y = calc.calculate(el.get_value())(x)
                self.plot_options["source"]["xy"] = (x, y)
                if elemtype == "Dipole":
                    elemtype = "DipoleSource"
            except CalculatorException:
                tk.messagebox.showerror("Error", "Invalid expression")

        self.update_widget_list(elemtype)
