from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")


class FrameBase(ttk.Frame):
    """
    A base class for displaying numerous labels, entries, buttons, or plots.
    """

    def __init__(
        self,
        master: ttk.Frame,
        layout_config: dict,
        label_options: dict = None,
        entry_options: dict = None,
        button_options: dict = None,
        plot_options: dict = None,
        combobox_options: dict = None,
        checkbox_options: dict = None,
        radio_options: dict = None,
    ):
        """Initializes the FrameBase with a layout configuration and widget options.

        Args:
            master (ttk.Frame): Frame in which this frame is embedded.
            layout_config (dict): Configuration for widget layout.
            label_options (dict, optional): Options for labels. Defaults to None.
            entry_options (dict, optional): Options for entries. Defaults to None.
            button_options (dict, optional): Options for buttons. Defaults to None.
            plot_options (dict, optional): Options for plots. Defaults to None.
            combobox_options (dict, optional): Options for comboboxes. Defaults to None.
            checkbox_options (dict, optional): Options for checkboxes. Defaults to None.
            radio_options (dict, optional): Options for radio buttons. Defaults to None.
        """
        super().__init__(master)
        self.layout_config = layout_config
        self.entries = {}
        self.labels = {}
        self.plots = {}
        self.buttons = {}
        self.combobox = {}
        self.checkbox = {}
        self.radios = {}

        self.label_options = label_options or {}
        self.entry_options = entry_options or {}
        self.button_options = button_options or {}
        self.plot_options = plot_options or {}
        self.combobox_options = combobox_options or {}
        self.checkbox_options = checkbox_options or {}
        self.radio_options = radio_options or {}

        self.place_widgets()
        self.columnconfigure(0, weight=1)

    def delete_all(self):
        """Deletes all widgets from the frame."""
        for widget_dict in [
            self.labels,
            self.entries,
            self.plots,
            self.buttons,
            self.combobox,
            self.checkbox,
            self.radios,
        ]:
            for widget in widget_dict.values():
                widget.grid_forget()
                widget.destroy()
            widget_dict.clear()

    def place_widgets(self):
        """Places the widgets in the frame based on the layout configuration."""
        for widget_id, config in self.layout_config.items():
            widget_type = config.get("type")
            options = getattr(self, f"{widget_type}_options", {}).get(widget_id, {})
            grid_options = config.get("grid", {})
            self.create_widget(widget_type, widget_id, options, grid_options)

    def create_widget(self, widget_type, widget_id, options, grid_options):
        """Creates and places a widget in the frame based on its type."""
        widget_creation_map = {
            "label": self.create_label,
            "entry": self.create_entry,
            "plot": self.create_plot,
            "button": self.create_button,
            "combobox": self.create_combobox,
            "checkbox": self.create_checkbox,
            "radio": self.create_radio,
        }
        creation_func = widget_creation_map.get(widget_type)
        if creation_func:
            creation_func(widget_id, options, grid_options)

    def create_label(self, key, options, grid_options):
        """Creates and places a label widget."""
        label = tk.Label(self, text=options.get("text", ""))
        label.grid(**grid_options)
        self.labels[key] = label

    def create_entry(self, key, options, grid_options):
        """Creates and places an entry widget."""
        sv = tk.StringVar(value=options.get("insert", ""))
        sv.trace_add("write", lambda *_: options.get("bindfunc", lambda _: None)(sv))
        entry = tk.Entry(self, textvariable=sv)
        entry.grid(**grid_options)
        self.entries[key] = entry

    def create_plot(self, key, options, grid_options):
        """Creates and places a plot widget."""
        fig = Figure(figsize=(2, 1.5), dpi=options.get("dpi", 100), tight_layout=True)
        subplot = fig.add_subplot(111)
        subplot.plot(*options.get("xy", ([], [])))
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(**grid_options)
        self.plots[key] = canvas.get_tk_widget()

    def create_button(self, key, options, grid_options):
        """Creates and places a button widget."""
        button = ttk.Button(
            self,
            text=options.get("text", ""),
            command=options.get("bindfunc", lambda: None),
        )
        button.grid(**grid_options)
        self.buttons[key] = button

    def create_combobox(self, key, options, grid_options):
        """Creates and places a combobox widget."""
        combobox = ttk.Combobox(
            self, values=options.get("values", []), state="readonly"
        )
        combobox.grid(**grid_options)
        combobox.current(0)
        combobox.bind("<<ComboboxSelected>>", options.get("bindfunc", lambda _: None))
        self.combobox[key] = combobox

    def create_checkbox(self, key, options, grid_options):
        """Creates and places a checkbox widget."""
        var = tk.IntVar(value=options.get("onoff", 0))
        checkbox = ttk.Checkbutton(
            self,
            text=options.get("text", ""),
            variable=var,
            command=lambda: options.get("command", lambda _: None)(var),
        )
        checkbox.grid(**grid_options)
        self.checkbox[key] = checkbox

    def create_radio(self, key, options, grid_options):
        """Creates and places a radio button widget."""
        radio_frame = ttk.Frame(self)
        var = tk.IntVar(value=options.get("value", 0))
        for text, value in zip(options.get("texts", []), options.get("values", [])):
            radio_button = tk.Radiobutton(
                radio_frame,
                text=text,
                variable=var,
                value=value,
                command=lambda: options.get("command", lambda _: None)(var),
            )
            radio_button.pack(side=tk.LEFT)
        radio_frame.grid(**grid_options)
        self.radios[key] = radio_frame
