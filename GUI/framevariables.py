from os import name
from tkinter import ttk
import tkinter as tk
from utils.calculator import calculator


class FrameVariables(ttk.Frame):

    def __init__(self, master, drbd):
        super().__init__(master)

        # Treeview for constants and variables
        self.tree = ttk.Treeview(self, columns=("value"))
        self.tree.heading("#0", text="Variable names")
        self.tree.heading("value", text="Value")
        self.tree.column("value", width=100, anchor="center")
        self.tree.insert("", 0, "const", text="Constants")
        self.tree.insert("", 1, "var", text="Variables")
        self.tree.insert("", 2, "elvar", text="Element Variables")
        self.tree.bind("<Double-1>", self.on_double_click)

        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Buttons to add and remove constants/variables
        self.add_const_btn = ttk.Button(self, text="+ Constant", command=self.add_constant)
        self.add_var_btn = ttk.Button(self, text="+ Variable", command=self.add_variable)
        self.remove_btn = ttk.Button(self, text="- Remove", command=self.remove_selected)

        self.add_const_btn.grid(row=1, column=0, sticky="ew")
        self.add_var_btn.grid(row=1, column=1, sticky="ew")
        self.remove_btn.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Configuring resizing behavior
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.drbd = drbd
        self.cC = 0
        self.cV = 0
        self.Constants = {}
        self.Variables = {}

        # Initialize with constants and variables from calculator
        self.initialize_from_calculator()

    def initialize_from_calculator(self):
        for name, value in calculator.constants.items():
            self.add_constant(name, value)
        for name, value in calculator.variables.items():
            self.add_variable(name, value)

    def add_constant(self, name="", value=""):
        C = "C" + str(self.cC)
        self.cC += 1
        self.tree.insert("const", index=tk.END, iid=C, text=name, values=(value,))
        self.Constants[C] = (name, value)

    def remove_constant(self, C):
        if C in self.Constants:
            self.tree.delete(C)
            del self.Constants[C]

    def add_variable(self, name="", value=""):
        V = "V" + str(self.cV)
        self.cV += 1
        self.tree.insert("var", index=tk.END, iid=V, text=name, values=(value,))
        self.Variables[V] = (name, value)

    def remove_variable(self, V):
        if V in self.Variables:
            self.tree.delete(V)
            del self.Variables[V]

    def remove_selected(self):
        selected = self.tree.focus()
        if selected.startswith("C"):
            self.remove_constant(selected)
        elif selected.startswith("V"):
            self.remove_variable(selected)

    def on_double_click(self, event):
        elem_iid = self.tree.focus()
        if elem_iid in ["const", "var", "elvar"]:
            return
        self.edit_variable_name(elem_iid)

    def edit_variable_name(self, iid: str):
        param_dic = self.tree.item(iid)
        elem_text = param_dic["text"]
        elem_value = param_dic["values"][0]
        bbox = self.tree.bbox(iid)
        name_entry = ttk.Entry(self.tree)
        value_entry = ttk.Entry(self.tree)
        name_entry.insert(0, elem_text)
        value_entry.insert(0, elem_value)
        name_entry.select_range(0, tk.END)
        value_entry.select_range(0, tk.END)
        name_entry.focus()
        name_entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, iid, name_entry, value_entry))
        name_entry.bind("<Return>", lambda e: self.on_enter_press(e, iid, name_entry, value_entry))
        value_entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, iid, name_entry, value_entry))
        value_entry.bind("<Return>", lambda e: self.on_enter_press(e, iid, name_entry, value_entry))
        name_entry.place(x=bbox[0], y=bbox[1], width=bbox[2] // 2, height=bbox[3])
        value_entry.place(x=bbox[0] + bbox[2] // 2, y=bbox[1], width=bbox[2] // 2, height=bbox[3])

    def on_focus_out(self, event: tk.Event, iid: str, name_entry: ttk.Entry, value_entry: ttk.Entry):
        if event.widget.focus_get() in [name_entry, value_entry]:
            return
        event.widget.destroy()
        if not name_entry.winfo_exists() and not value_entry.winfo_exists():
            self.tree.focus(iid)
            self.tree.selection_set(iid)

    def on_enter_press(self, event: tk.Event, iid: str, name_entry: ttk.Entry, value_entry: ttk.Entry):
        new_name = name_entry.get()
        new_value = value_entry.get()
        self.edit_variable(iid, new_name, new_value)
        name_entry.destroy()
        value_entry.destroy()

    def edit_variable(self, iid, name, value):
        if iid:
            elem_parent = self.tree.parent(iid)
            if elem_parent == "const":
                self.Constants[iid] = (name, value)
            elif elem_parent == "var":
                self.Variables[iid] = (name, value)
            self.tree.item(iid, text=name, values=(value,))

    def reinitialize(self):
        self.cC = 0
        self.cV = 0
        for const_id in list(self.Constants.keys()):
            self.tree.delete(const_id)
        for var_id in list(self.Variables.keys()):
            self.tree.delete(var_id)
        self.Constants.clear()
        self.Variables.clear()
