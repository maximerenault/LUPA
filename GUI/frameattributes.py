from GUI.framebase import FrameBase
from utils.io import readvalues
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from elements.ground import Ground
from elements.psource import PSource
from elements.diode import Diode
from exceptions.attibutesexceptions import *
from utils.strings import *
import matplotlib
import utils.calculator as calc

matplotlib.use("TkAgg")


class FrameAttributes(ttk.Frame):
    """
    A class for displaying info about an element
    and editing it
    """

    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.rowconfigure((0, 2), weight=1)
        self.columnconfigure(0, weight=1)

        self.widget_configs = {
            "Clear": {
                "layout": {"clear": {"type": "label", "grid": {"row": 0, "column": 0}}},
                "rowcol_weights": {"rows": [0], "rowweights": [1], "cols": [0], "colweights": [1]},
            },
            "Wire": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {"type": "entry", "grid": {"row": 0, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "lablistenPstart": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "listenPstart": {"type": "checkbox", "grid": {"row": 2, "column": 1}},
                    "labend": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "endx": {"type": "entry", "grid": {"row": 3, "column": 1}},
                    "endy": {"type": "entry", "grid": {"row": 3, "column": 2}},
                    "lablistenPend": {"type": "label", "grid": {"row": 4, "column": 0}},
                    "listenPend": {"type": "checkbox", "grid": {"row": 4, "column": 1}},
                    "lablistenQ": {"type": "label", "grid": {"row": 5, "column": 0}},
                    "listenQ": {"type": "radio", "grid": {"row": 5, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "delete": {"type": "button", "grid": {"row": 6, "column": 0, "columnspan": 3, "sticky": "ew"}},
                },
                "rowcol_weights": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            },
            "Dipole": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {"type": "entry", "grid": {"row": 0, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "labend": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "endx": {"type": "entry", "grid": {"row": 2, "column": 1}},
                    "endy": {"type": "entry", "grid": {"row": 2, "column": 2}},
                    "labval": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "value": {"type": "entry", "grid": {"row": 3, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "delete": {"type": "button", "grid": {"row": 4, "column": 0, "columnspan": 3, "sticky": "ew"}},
                },
                "rowcol_weights": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            },
            "Ground": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {"type": "entry", "grid": {"row": 0, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "labdir": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "direct": {"type": "combobox", "grid": {"row": 2, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "delete": {"type": "button", "grid": {"row": 3, "column": 0, "columnspan": 3, "sticky": "ew"}},
                },
                "rowcol_weights": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            },
            "Source": {
                "layout": {
                    "labnam": {"type": "label", "grid": {"row": 0, "column": 0}},
                    "name": {"type": "entry", "grid": {"row": 0, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "labsta": {"type": "label", "grid": {"row": 1, "column": 0}},
                    "startx": {"type": "entry", "grid": {"row": 1, "column": 1}},
                    "starty": {"type": "entry", "grid": {"row": 1, "column": 2}},
                    "labdir": {"type": "label", "grid": {"row": 2, "column": 0}},
                    "direct": {"type": "combobox", "grid": {"row": 2, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "labval": {"type": "label", "grid": {"row": 3, "column": 0}},
                    "value": {"type": "entry", "grid": {"row": 3, "column": 1, "columnspan": 2, "sticky": "ew"}},
                    "source": {"type": "plot", "grid": {"row": 4, "column": 0, "columnspan": 3, "sticky": "ew"}},
                    "read": {"type": "button", "grid": {"row": 5, "column": 0, "columnspan": 3, "sticky": "ew"}},
                    "delete": {"type": "button", "grid": {"row": 6, "column": 0, "columnspan": 3, "sticky": "ew"}},
                },
                "rowcol_weights": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
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
            "startx": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "start", "x"), "insert": ""},
            "starty": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "start", "y"), "insert": ""},
            "endx": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "x"), "insert": ""},
            "endy": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "y"), "insert": ""},
        }

        self.cbbox_options = {
            "direct": {"values": ["S", "E", "N", "W"], "bindfunc": self.update_direction},
        }

        self.plot_options = {"source": {"dpi": 100, "xy": ([0, 1], [0, 1])}}

        self.button_options = {
            "read": {"text": "Read file", "bindfunc": self.read_values},
            "delete": {"text": "Delete", "bindfunc": self.delete_elem},
        }

        self.checkbox_options = {
            "listenPstart": {"text": "on/off", "onoff": 0, "command": lambda var: self.set_listenP(0, var)},
            "listenPend": {"text": "on/off", "onoff": 0, "command": lambda var: self.set_listenP(1, var)},
        }

        self.radio_options = {
            "listenQ": {"texts": ["off", "Q", "-Q"], "values": [0, 1, -1], "value": 0, "command": self.set_listenQ},
        }

        self.widget_frame = FrameBase(self, {})
        self.update_widget_list()

        self.drbd = drbd
        self.elem = -1

    def update_name(self, stringvar):
        """
        Update name of the object and
        display it
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        el.name = stringvar.get()
        el.redrawname(self.drbd)

    def update_coords(self, stringvar, pos, comp):
        """
        Updates start or end coords of the object
        with id self.elem
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        coords = el.getcoords()
        newcoord = check_strint(stringvar.get())
        stringvar.set(newcoord)
        if newcoord == "" or newcoord == "-":
            return
        try:
            newcoordint = int(newcoord)
        except:
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
        else:
            raise BadCoordError
        newcoords = el.getcoords()
        if (newcoords[:2] == newcoords[2:]).all():
            el.setstart(coords[0], coords[1])
            el.setend(coords[2], coords[3])
            return
        el.redraw(self.drbd)

    def update_value(self, stringvar):
        """
        Updates value for dipole elements
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        el.set_value(stringvar.get())

    def read_values(self):
        """
        Allows for opening a csv file
        with columns time and value,
        with sep='\t'
        """
        file_name = tk.filedialog.askopenfilename()
        if file_name:
            x, y = readvalues(file_name)
            el = self.drbd.cgeom.elems[self.elem]
            el.set_source(x, y)
            self.update_attributes()

    def update_direction(self, event: tk.Event):
        """
        Update source-type element direction
        """
        el = self.drbd.cgeom.elems[self.elem]
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

    def set_listenP(self, pos, var):
        """
        Change pressure listening from True to False
        and the other way around.
        """
        el = self.drbd.cgeom.elems[self.elem]
        val = var.get()
        el.set_listenP(pos, val, self.drbd)
        el.redraw(self.drbd)

    def set_listenQ(self, var):
        """
        Set Q listening flag to 0 if off, 1 if same direction
        as elem, -1 otherwise.
        """
        el = self.drbd.cgeom.elems[self.elem]
        val = var.get()
        el.set_listenQ(val, self.drbd)
        el.redraw(self.drbd)

    def delete_elem(self):
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

    def change_elem(self, id):
        """
        Interface function for other modules
        to change the element selected

        id : int, unique id number of the element
        """
        self.elem = id
        self.update_attributes()

    def update_widget_list(self, key: str = "Clear"):
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

    def update_attributes(self):
        if self.elem == -1:
            self.update_widget_list()
            return

        el = self.drbd.cgeom.elems[self.elem]

        if isinstance(el, Resistor) or isinstance(el, Inductor) or isinstance(el, Capacitor):
            elemtype = "Dipole"
        elif type(el) == Wire or type(el) == Diode:
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
            x = np.linspace(0, 10, 100)
            y = calc.calculate(el.get_value())(x)
            self.plot_options["source"]["xy"] = (x, y)

        self.update_widget_list(elemtype)
