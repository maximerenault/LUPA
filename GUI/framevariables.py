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
        self.tree.insert("", 0, "const", text="Constants", open=True)
        self.tree.insert("", 1, "var", text="Variables", open=True)
        self.tree.insert("", 2, "elvar", text="Element Variables", open=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Buttons to add and remove constants/variables
        self.add_const_btn = ttk.Button(
            self, text="+ Constant", command=self.add_constant
        )
        self.add_var_btn = ttk.Button(
            self, text="+ Variable", command=self.add_variable
        )
        self.remove_btn = ttk.Button(
            self, text="- Remove", command=self.remove_selected
        )

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

        # Initialize with constants and variables from calculator
        self.initialize_from_calculator()

    def initialize_from_calculator(self):
        for name, value in calculator.constants.items():
            self.add_constant(name, value)
        for name, value in calculator.variables.items():
            self.add_variable(name, value)

    def add_constant(self, name: str = "", value: str | float = ""):
        C = "C" + str(self.cC)
        self.cC += 1
        self.tree.insert("const", index=tk.END, iid=C, text=name, values=(value,))
        self.tree.item("const", open=True)
        if name == "":
            self.enter_edition(C)

    def remove_constant(self, C: str):
        if not self.tree.exists(C):
            return
        name = self.tree.item(C).get("text", "")
        if not name:
            return
        try:
            calculator.remove_constant(name)
        except Exception:
            # Protected or invalid; do nothing
            return
        self.tree.delete(C)

    def add_variable(self, name: str = "", value: str = ""):
        V = "V" + str(self.cV)
        self.cV += 1
        self.tree.insert("var", index=tk.END, iid=V, text=name, values=(value,))
        self.tree.item("var", open=True)
        if name == "":
            self.enter_edition(V)

    def remove_variable(self, V: str):
        if not self.tree.exists(V):
            return
        name = self.tree.item(V).get("text", "")
        if not name:
            return
        try:
            calculator.remove_variable(name)
        except Exception:
            # Protected or invalid; do nothing
            return
        self.tree.delete(V)

    def remove_selected(self):
        selected = self.tree.focus()
        if not selected:
            return
        if selected.startswith("C"):
            self.remove_constant(selected)
        elif selected.startswith("V"):
            self.remove_variable(selected)

    def on_double_click(self, event):
        elem_iid = self.tree.focus()
        if elem_iid in ["const", "var", "elvar"] or not elem_iid:
            return
        parent = self.tree.parent(elem_iid)
        name = self.tree.item(elem_iid).get("text", "")
        if (parent == "const" and calculator.is_protected_constant(name)) or (
            parent == "var" and calculator.is_protected_variable(name)
        ):
            return
        self.enter_edition(elem_iid)

    def enter_edition(self, iid: str):
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
        name_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, iid, name_entry, value_entry)
        )
        name_entry.bind(
            "<Return>", lambda e: self.on_enter_press(e, iid, name_entry, value_entry)
        )
        value_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, iid, name_entry, value_entry)
        )
        value_entry.bind(
            "<Return>", lambda e: self.on_enter_press(e, iid, name_entry, value_entry)
        )
        name_entry.place(x=bbox[0], y=bbox[1], width=bbox[2] // 2, height=bbox[3])
        value_entry.place(
            x=bbox[0] + bbox[2] // 2, y=bbox[1], width=bbox[2] // 2, height=bbox[3]
        )

    def on_focus_out(
        self, event: tk.Event, iid: str, name_entry: ttk.Entry, value_entry: ttk.Entry
    ):
        if event.widget.focus_get() in [name_entry, value_entry]:
            return
        name_entry.destroy()
        value_entry.destroy()
        self.tree.focus(iid)
        self.tree.selection_set(iid)

    def on_enter_press(
        self, event: tk.Event, iid: str, name_entry: ttk.Entry, value_entry: ttk.Entry
    ):
        new_name = name_entry.get()
        new_value = value_entry.get()
        self.edit_variable(iid, new_name, new_value)
        name_entry.destroy()
        value_entry.destroy()

    def edit_variable(self, iid: str, name: str, value: str):
        if not iid:
            return
        elem_parent = self.tree.parent(iid)
        old_item = self.tree.item(iid)
        old_name = old_item.get("text", "")

        if elem_parent == "const":
            try:
                # If renaming
                if name != old_name and old_name:
                    # Validate value before removing old
                    _ = float(value)
                    calculator.remove_constant(old_name)
                calculator.set_constant(name, value)
            except Exception:
                return
        elif elem_parent == "var":
            try:
                new_expr = (
                    value if value != "" else (old_item.get("values", [""])[0] or name)
                )
                if name != old_name and old_name:
                    calculator.remove_variable(old_name)
                calculator.set_variable(name, new_expr)
            except Exception:
                return
        # Update UI after successful calculator change
        self.tree.item(iid, text=name, values=(value,))

    def reinitialize(self):
        self.cC = 0
        self.cV = 0
        for child in list(self.tree.get_children("const")):
            self.tree.delete(child)
        for child in list(self.tree.get_children("var")):
            self.tree.delete(child)

    def save_variables(self, data: dict):
        data["constants"] = {}
        data["variables"] = {}
        for child in self.tree.get_children("const"):
            name = self.tree.item(child).get("text", "")
            value = self.tree.item(child).get("values", [""])[0]
            if name:
                data["constants"][name] = value
        for child in self.tree.get_children("var"):
            name = self.tree.item(child).get("text", "")
            value = self.tree.item(child).get("values", [""])[0]
            if name:
                data["variables"][name] = value

    def load_variables(self, data: dict):
        self.reinitialize()
        for name, value in data.get("constants", {}).items():
            self.add_constant(name, value)
        for name, value in data.get("variables", {}).items():
            self.add_variable(name, value)
        # Rebuild the calculator state from loaded variables
        calculator.constants = data.get("constants", {})
        calculator.variables = data.get("variables", {})
        calculator._update_tokens()
