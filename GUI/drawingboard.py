from GUI.framelisteners import FrameListeners
from GUI.framevariables import FrameVariables
from GUI.gridzoom import GridZoom
from GUI.frameattributes import FrameAttributes
from GUI.framesolve import FrameSolve
from elements.diode import Diode
from elements.node import Node
from elements.ground import Ground
from elements.psource import PSource
from elements.qsource import QSource
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from solvers.circuitgeom import CircuitGeom
from utils.geometry import start_from_elem, elem_init_pos, intersect, distance
import tkinter as tk
from tkinter import ttk

from utils.io import loadfromjson, savetojson


class DrawingBoard(GridZoom):
    def __init__(self, mainframe):
        GridZoom.__init__(self, mainframe)
        # Bind events to the Canvas
        self.canvas.bind("<Configure>", self.db_resize)  # canvas is resized
        self.canvas.bind("<ButtonPress-1>", self.db_move_from)
        self.canvas.bind("<ButtonRelease-1>", self.db_release)
        self.canvas.bind("<B1-Motion>", self.db_move_to)
        self.canvas.bind("<MouseWheel>", self.db_wheel)  # with Windows and MacOS
        self.canvas.bind("<Button-5>", self.db_wheel)  # with Linux, scroll down
        self.canvas.bind("<Button-4>", self.db_wheel)  # with Linux, scroll up

        self.frameChoices = ttk.Frame(self.master)
        self.frameChoices.grid(row=2, column=0, pady=1)
        self.radiovalue = tk.StringVar()
        self.radiovalue.set("Edit")  # Default Select
        self.drag_func_elems = ["Wire", "R", "C", "L", "Gnd", "P", "Q", "Diode"]
        self.drag_functions = ["Edit", "Wire", "R", "C", "L", "Gnd", "P", "Q", "Diode"]
        for fc in self.drag_functions:
            tk.Radiobutton(
                self.frameChoices,
                text=fc,
                variable=self.radiovalue,
                value=fc,
                command=self.dragchanger,
            ).pack(side=tk.LEFT, padx=6, pady=3)
        self.drag_function = "Edit"
        self.prevdragx = 0
        self.prevdragy = 0
        self.nomove = False

        self.cgeom = CircuitGeom()

        self.tabControl = ttk.Notebook(self.master)

        self.frameAttr = FrameAttributes(self.tabControl, self)
        self.frameAttr.grid(row=0, column=0, pady=1)
        self.frameSolve = FrameSolve(self.tabControl, self)
        self.frameSolve.grid(row=0, column=0, pady=1)
        self.frameListeners = FrameListeners(self.tabControl, self)
        self.frameVariables = FrameVariables(self.tabControl, self)

        self.tabControl.add(self.frameAttr, text="Attributes")
        self.tabControl.add(self.frameSolve, text="Solver")
        self.tabControl.add(self.frameListeners, text="Listeners")
        self.tabControl.add(self.frameVariables, text="Consts & Vars")
        self.tabControl.grid(row=0, column=1, rowspan=3, pady=1, sticky="nsew")

    def db_resize(self, event):
        """
        Resizing the window and
        redrawing everything
        """
        dx, dy = self.resize()
        self.canvas.move("circuit", dx, dy)

    def db_move_from(self, event):
        """
        Function for first press
        of left MB
        """
        if not self.nomove:
            self.move_from(event)

        # In Edit mode, all the work is done in elem.onElemClick
        if self.drag_function == "Edit":
            return

        # In Drawing mode, we use geometry function to check if the start
        # belongs to an element already defined. In that case the start
        # of the new element is set at the end of the one already defined.
        x0, y0 = self.pix2coord(self.prevx, self.prevy)
        x0 = round(x0)
        y0 = round(y0)
        x0, y0, eldir = start_from_elem(self, x0, y0)

        if self.drag_function in self.drag_func_elems:
            node1 = Node(x0, y0)
            node2 = Node(x0, y0)

            if self.drag_function == "Wire":
                elem = Wire(node1, node2)
            elif self.drag_function == "R":
                elem = Resistor(node1, node2, 10)
            elif self.drag_function == "C":
                elem = Capacitor(node1, node2, 10)
            elif self.drag_function == "L":
                elem = Inductor(node1, node2, 10)
            elif self.drag_function == "Gnd":
                elem = Ground(node1, node2)
            elif self.drag_function == "P":
                elem = PSource(node1, node2, "sin(2*pi*t)", True)
            elif self.drag_function == "Q":
                elem = QSource(node1, node2, "cos(2*pi*t)", True)
            elif self.drag_function == "Diode":
                elem = Diode(node1, node2)

            elem_init_pos(self, elem, eldir + 2)
            elem.draw(self)
            self.cgeom.add_elem(elem)

    def db_move_to(self, event):
        """
        Function for moving mouse
        while pressing left MB
        """
        if self.drag_function == "Edit":
            if not self.nomove:
                self.canvas.move("circuit", event.x - self.prevx, event.y - self.prevy)
                self.move_to(event)

        elif self.drag_function in self.drag_func_elems:
            x1, y1 = self.pix2coord(event.x, event.y)
            x1 = round(x1)
            y1 = round(y1)
            if self.prevdragx != x1 or self.prevdragy != y1:
                self.prevdragx = x1
                self.prevdragy = y1
                elem = self.cgeom.elems[-1]
                x0, y0, _, _ = elem.getcoords()
                elem.setend(x1, y1)

                # Find the closest intersection
                closest_x, closest_y = x1, y1
                min_dist = float("inf")

                for el in self.cgeom.elems[:-1]:
                    tempx, tempy = intersect(elem, el)
                    dist = distance(x0, y0, tempx, tempy)
                    if dist < min_dist:
                        closest_x, closest_y = tempx, tempy
                        min_dist = dist

                if min_dist < distance(x0, y0, x1, y1):
                    x1, y1 = closest_x, closest_y

                elem.setend(x1, y1)
                elem.redraw(self)
                self.show_frontground(event)

    def db_release(self, event):
        """
        Function for releasing left MB
        """
        if self.drag_function in self.drag_func_elems:
            elem = self.cgeom.elems[-1]
            x0, y0, x1, y1 = elem.getcoords()
            if x0 == x1 and y0 == y1:
                self.cgeom.del_elem(-1)
            else:
                self.cgeom.add_elem_nodes(elem)
                self.frameAttr.change_elem(len(self.cgeom.elems) - 1)

    def db_wheel(self, event):
        """
        Function for rolling the
        mouse wheel
        """
        self.gridwheel(event)
        self.redraw_elements()

    def dragchanger(self, event=None):
        self.drag_function = self.radiovalue.get()  # selected radio value

    def deleteElement(self, el_id):
        el = self.cgeom.elems[el_id]
        el.delete(self)
        self.cgeom.del_elem(el_id)
        del el

    def save(self, filename=None):
        data = {}
        data["nodes"] = []
        data["elements"] = []
        for node in self.cgeom.nodes:
            data["nodes"].append(node.to_dict())
        for el in self.cgeom.elems:
            data["elements"].append(el.to_dict(self.cgeom.nodes))
        self.frameVariables.save_variables(data)
        return savetojson(data, filename)

    def load(self, filename=None):
        data, filename = loadfromjson(filename)
        if data is None:
            return None

        self.clear_canvas()
        self.load_nodes_elements(data["nodes"], data["elements"])
        self.redraw_elements()
        self.frameVariables.load_variables(data)

        return filename

    def clear_canvas(self):
        for el in self.cgeom.elems:
            for id in el.ids:
                self.canvas.delete(id)
            self.canvas.delete(el.nameid)
        self.cgeom.clear()

    def load_nodes_elements(self, nodes_data, elements_data):
        for el_dict in elements_data:
            id1, id2 = el_dict["nodes"]
            node1 = Node(*nodes_data[id1])
            node2 = Node(*nodes_data[id2])

            constructor = globals().get(el_dict["type"], None)
            if constructor is None:
                print(f"Unknown element type: {el_dict['type']}")
                continue

            element = constructor(node1, node2, el_dict["value"], el_dict["active"])
            element.set_name(el_dict["name"])
            element.draw(self)

            for i in range(2):
                element.set_listenP(i, el_dict["pressure_listeners"][i], self)
                iid = self.frameListeners.get_node_iid(element.nodes[i].id)
                self.frameListeners.edit_listener(
                    iid, el_dict["pressure_listener_names"][i]
                )

            element.set_listenQ(int(el_dict["flow_listener"]), self)
            iid = self.frameListeners.get_elem_iid(element.ids[0])
            self.frameListeners.edit_listener(iid, el_dict["flow_listener_name"])

            self.cgeom.add_elem(element)
            self.cgeom.add_elem_nodes(element)

    def redraw_elements(self):
        for el in self.cgeom.elems:
            el.redraw(self)
