from tkinter import ttk
import tkinter as tk
from lupa.elements.node import Node
from lupa.elements.wire import Wire
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lupa.GUI.drawingboard import DrawingBoard


class FrameProbes(ttk.Treeview):

    def __init__(self, master: ttk.Frame, drbd: "DrawingBoard") -> None:
        super().__init__(master)
        self.heading("#0", text="Probe names")
        self.insert("", 0, "P", text="Pressure")
        self.insert("", 1, "Q", text="Flow")

        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Motion>", self.on_motion)

        self.on_motion_activated = True
        self.drbd = drbd
        self.last_focus = ""
        self.cQ = 0
        self.cP = 0
        self.Pprobes = {}
        self.Qprobes = {}

    def add_probe(self, probe_type: str, element: Wire | Node) -> None:
        if probe_type == "P":
            probe_id = f"P{self.cP}"
            element_id = element.id
            self.cP += 1
            probes = self.Pprobes
        elif probe_type == "Q":
            probe_id = f"Q{self.cQ}"
            element_id = element.ids[0]
            self.cQ += 1
            probes = self.Qprobes
        else:
            raise ValueError(f"Invalid probe type: {probe_type}")

        element.probe_name = element.probe_name or probe_id
        self.insert(probe_type, tk.END, iid=probe_id, text=element.probe_name)
        probes[element_id] = probe_id
        probes[probe_id] = element

    def remove_probe(self, probe_type: str, element: Wire | Node) -> None:
        probes = self.Pprobes if probe_type == "P" else self.Qprobes
        element_id = element.id if probe_type == "P" else element.ids[0]
        probe_id = probes.pop(element_id, None)
        if probe_id:
            self.delete(probe_id)
            del probes[probe_id]

    def add_pressure_probe(self, node: Node) -> None:
        self.add_probe("P", node)

    def remove_pressure_probe(self, node: Node) -> None:
        self.remove_probe("P", node)

    def add_flow_probe(self, elem: Wire) -> None:
        self.add_probe("Q", elem)

    def remove_flow_probe(self, elem: Wire) -> None:
        self.remove_probe("Q", elem)

    def on_double_click(self, event: tk.Event) -> None:
        elem_iid = self.focus()
        if elem_iid in ["P", "Q"]:
            return
        self.on_motion_activated = False
        self.edit_probe_name(elem_iid)

    def edit_probe_name(self, iid: str) -> None:
        param_dic = self.item(iid)
        elem_text = param_dic["text"]
        bbox = self.bbox(iid)
        entry_edit = ttk.Entry(self)
        entry_edit.insert(0, elem_text)
        entry_edit.select_range(0, tk.END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self.on_focus_out)
        entry_edit.bind("<Return>", lambda e: self.on_enter_press(e, iid))
        entry_edit.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])

    def on_focus_out(self, event: tk.Event) -> None:
        self.on_motion_activated = True
        event.widget.destroy()

    def on_enter_press(self, event: tk.Event, iid: str) -> None:
        new_text = event.widget.get()
        self.edit_probe(iid, new_text)
        self.on_motion_activated = True
        event.widget.destroy()

    def edit_probe(self, iid: str, text: str) -> None:
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node: Node = self.Pprobes[iid]
                node.probe_name = text
            elif elem_parent == "Q":
                elem: Wire = self.Qprobes[iid]
                elem.probe_name = text
            self.item(iid, text=text)

    def get_elem_iid(self, elem: Wire) -> str:
        try:
            return self.Qprobes[elem]
        except KeyError:
            return ""

    def get_node_iid(self, node: Node) -> str:
        try:
            return self.Pprobes[node]
        except KeyError:
            return ""

    def on_motion(self, event: tk.Event) -> None:
        if not self.on_motion_activated:
            return
        iid = self.identify_row(event.y)
        if self.last_focus != iid:
            self.update_focus(iid)

    def update_focus(self, iid: str) -> None:
        self.focus(iid)
        self.selection_set(iid)
        self.leave_probe(self.last_focus)
        self.enter_probe(iid)
        self.last_focus = iid

    def enter_probe(self, iid: str) -> None:
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node: Node = self.Pprobes[iid]
                node.radius += 0.1
                node.redraw(self.drbd)
            elif elem_parent == "Q":
                elem: Wire = self.Qprobes[iid]
                elem.Qsize = 2.0
                elem.redraw(self.drbd)

    def leave_probe(self, iid: str) -> None:
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node: Node = self.Pprobes[iid]
                node.radius -= 0.1
                node.redraw(self.drbd)
            elif elem_parent == "Q":
                elem: Wire = self.Qprobes[iid]
                elem.Qsize = 1.0
                elem.redraw(self.drbd)

    def reinitialize(self) -> None:
        self.cQ = 0
        self.cP = 0
        for probe_id in list(self.Pprobes.values()):
            self.delete(probe_id)
        for probe_id in list(self.Qprobes.values()):
            self.delete(probe_id)
        self.Pprobes.clear()
        self.Qprobes.clear()
