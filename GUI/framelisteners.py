from tkinter import ttk
import tkinter as tk
from elements.node import Node
from elements.wire import Wire


class FrameListeners(ttk.Treeview):

    def __init__(self, master, drbd):
        super().__init__(master)
        self.heading("#0", text="Listener names")
        self.insert("", 0, "P", text="Pressure")
        self.insert("", 1, "Q", text="Flow")

        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Motion>", self.on_motion)

        self.on_motion_activated = True
        self.drbd = drbd
        self.last_focus = ""
        self.cQ = 0
        self.cP = 0
        self.Plisteners = {}
        self.Qlisteners = {}

    def add_listener(self, listener_type, element):
        if listener_type == "P":
            listener_id = f"P{self.cP}"
            element_id = element.id
            self.cP += 1
            listeners = self.Plisteners
        elif listener_type == "Q":
            listener_id = f"Q{self.cQ}"
            element_id = element.ids[0]
            self.cQ += 1
            listeners = self.Qlisteners
        else:
            raise ValueError(f"Invalid listener type: {listener_type}")

        element.listener_name = element.listener_name or listener_id
        self.insert(listener_type, tk.END, iid=listener_id, text=element.listener_name)
        listeners[element_id] = listener_id
        listeners[listener_id] = element

    def remove_listener(self, listener_type, element):
        listeners = self.Plisteners if listener_type == "P" else self.Qlisteners
        element_id = element.id if listener_type == "P" else element.ids[0]
        listener_id = listeners.pop(element_id, None)
        if listener_id:
            self.delete(listener_id)
            del listeners[listener_id]

    def add_pressure_listener(self, node: Node):
        self.add_listener("P", node)

    def remove_pressure_listener(self, node: Node):
        self.remove_listener("P", node)

    def add_flow_listener(self, elem: Wire):
        self.add_listener("Q", elem)

    def remove_flow_listener(self, elem: Wire):
        self.remove_listener("Q", elem)

    def on_double_click(self, event):
        elem_iid = self.focus()
        if elem_iid in ["P", "Q"]:
            return
        self.on_motion_activated = False
        self.edit_listener_name(elem_iid)

    def edit_listener_name(self, iid):
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

    def on_focus_out(self, event):
        self.on_motion_activated = True
        event.widget.destroy()

    def on_enter_press(self, event, iid):
        new_text = event.widget.get()
        self.edit_listener(iid, new_text)
        self.on_motion_activated = True
        event.widget.destroy()

    def edit_listener(self, iid, text):
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node = self.Plisteners[iid]
                node.listener_name = text
            elif elem_parent == "Q":
                elem = self.Qlisteners[iid]
                elem.listener_name = text
            self.item(iid, text=text)

    def get_elem_iid(self, elem):
        try:
            return self.Qlisteners[elem]
        except:
            return ""

    def get_node_iid(self, node):
        try:
            return self.Plisteners[node]
        except:
            return ""

    def on_motion(self, event):
        if not self.on_motion_activated:
            return
        iid = self.identify_row(event.y)
        if self.last_focus != iid:
            self.update_focus(iid)

    def update_focus(self, iid):
        self.focus(iid)
        self.selection_set(iid)
        self.leave_listener(self.last_focus)
        self.enter_listener(iid)
        self.last_focus = iid

    def enter_listener(self, iid):
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node = self.Plisteners[iid]
                node.radius += 0.1
                node.redraw(self.drbd)
            elif elem_parent == "Q":
                elem = self.Qlisteners[iid]
                elem.Qsize = 2.0
                elem.redraw(self.drbd)

    def leave_listener(self, iid):
        if iid:
            elem_parent = self.parent(iid)
            if elem_parent == "P":
                node = self.Plisteners[iid]
                node.radius -= 0.1
                node.redraw(self.drbd)
            elif elem_parent == "Q":
                elem = self.Qlisteners[iid]
                elem.Qsize = 1.0
                elem.redraw(self.drbd)

    def reinitialize(self):
        self.cQ = 0
        self.cP = 0
        for listener_id in list(self.Plisteners.values()):
            self.delete(listener_id)
        for listener_id in list(self.Qlisteners.values()):
            self.delete(listener_id)
        self.Plisteners.clear()
        self.Qlisteners.clear()
