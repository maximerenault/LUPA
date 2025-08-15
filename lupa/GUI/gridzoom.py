import numpy as np
from tkinter import ttk, Event, Canvas, StringVar, Label, SUNKEN, PhotoImage


class GridZoom(ttk.Frame):
    """A class over tkinter Frame that contains
    a canvas, a dotted background and a moving
    and zooming function."""

    def __init__(self, mainframe: ttk.Frame) -> None:
        """Initialize the main Frame"""
        ttk.Frame.__init__(self, master=mainframe)
        # Create canvas
        self.canvas = Canvas(self.master, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nswe")
        self.canvas.update()  # wait till canvas is created
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind("<Configure>", self.resize)  # canvas is resized
        self.canvas.bind("<ButtonPress-1>", self.move_from)
        self.canvas.bind("<B1-Motion>", self.move_to)
        self.canvas.bind("<MouseWheel>", self.gridwheel)  # with Windows and MacOS
        self.canvas.bind("<Button-5>", self.gridwheel)  # with Linux, scroll down
        self.canvas.bind("<Button-4>", self.gridwheel)  # with Linux, scroll up
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.dotsize = 3
        self.prevx = 0
        self.prevy = 0
        self.x = int(self.width / 2) - self.dotsize // 2  # -1 to align with the grid
        self.y = int(self.height / 2) - self.dotsize // 2  # in the center of the window
        self.cx = 0
        self.cy = 0
        self.pixgrid = 50
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude between each scrolling tick
        self.resx = self.width % 2
        self.resy = self.height % 2
        # Drawing a reticle in the center
        self.reticle = [0 for _ in range(4)]
        self.draw_reticle()
        # Create a status bar
        self.status = StringVar()
        self.set_status()
        statusbar = Label(
            self.master, textvariable=self.status, anchor="w", relief=SUNKEN
        )
        statusbar.grid(row=1, column=0, sticky="we")
        self.show_background()
        # self.show_frontground()

    def set_status(self) -> None:
        self.cx, self.cy = self.pix2coord(int(self.width / 2), int(self.height / 2))
        self.status.set(
            f"Position : x = {-self.x-1+int(self.width/2)} , \
y = {-int(self.height/2)+self.y+1} , cx = {self.cx:.2f} , \
cy = {self.cy:.2f} , Scale : {self.imscale:.2f}"
        )

    def resize(self, event: Event = None) -> tuple[int, int]:
        dw = self.canvas.winfo_width() - self.width
        dh = self.canvas.winfo_height() - self.height
        dx = dw // 2
        dy = dh // 2
        # Correct drifting when resizing
        new_resx = (self.resx + dw % 2) % 2
        new_resy = (self.resy + dh % 2) % 2
        dx += ((self.resx - new_resx) + abs(self.resx - new_resx)) // 2
        dy += ((self.resy - new_resy) + abs(self.resy - new_resy)) // 2
        self.x += dx
        self.y += dy
        self.resx = new_resx
        self.resy = new_resy

        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.set_status()
        self.show_background()
        self.show_frontground()
        self.canvas.update()
        return dx, dy

    def move_from(self, event: Event) -> None:
        """Remember previous coordinates for scrolling with the mouse"""
        self.prevx = event.x
        self.prevy = event.y
        self.set_status()

    def move_to(self, event: Event) -> None:
        """Drag (move) canvas to the new position"""
        self.x += event.x - self.prevx
        self.y += event.y - self.prevy
        self.prevx = event.x
        self.prevy = event.y
        self.set_status()
        self.show_background()

    def gridwheel(self, event: Event) -> None:
        """Zoom with mouse wheel"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            sp = self.pixgrid
            self.pixgrid = int(sp / self.delta)
            if self.pixgrid < 20:
                self.pixgrid = 20
            self.imscale /= float(sp) / float(self.pixgrid)
            scale /= float(sp) / float(self.pixgrid)
        if event.num == 4 or event.delta == 120:  # scroll up
            sp = self.pixgrid
            self.pixgrid = int(sp * self.delta)
            if self.pixgrid > 400:
                self.pixgrid = 400
            self.imscale *= float(self.pixgrid) / float(sp)
            scale *= float(self.pixgrid) / float(sp)
        self.x = int(x + (self.x - x) * scale)
        self.y = int(y + (self.y - y) * scale)
        self.set_status()
        self.show_background()

    def show_background(self, event: Event = None) -> None:
        img = PhotoImage(width=self.width, height=self.height)
        sp = self.pixgrid
        ds = self.dotsize

        w1 = self.x % sp
        w2 = sp - w1
        w11 = (w1 == sp) * ds
        w12 = sp - ds - (w1 < (sp - ds)) * (sp - ds - w1)
        w21 = (w2 > 0) * ds
        w22 = (w2 > ds) * (w2 - ds)

        h1 = self.y % sp
        h2 = sp - h1
        h11 = (h1 == sp) * ds
        h12 = sp - ds - (h1 < (sp - ds)) * (sp - ds - h1)
        h21 = (h2 > 0) * ds
        h22 = (h2 > ds) * (h2 - ds)
        data = (
            "{{{}{}{}{}}} ".format(
                "gray50 " * w11, "white " * w12, "gray50 " * w21, "white " * w22
            )
            * h11
            + "{{{}}} ".format("white " * sp) * h12
            + "{{{}{}{}{}}} ".format(
                "gray50 " * w11, "white " * w12, "gray50 " * w21, "white " * w22
            )
            * h21
            + "{{{}}} ".format("white " * sp) * h22
        )
        img.put(data, to=(0, 0, self.width, self.height))
        imageid = self.canvas.create_image(0, 0, image=img, state="normal", anchor="nw")
        self.canvas.lower(imageid)  # set image into background
        self.canvas.bckgnd = img  # prevent garbage collection

    def draw_reticle(self, event: Event = None) -> None:
        w = self.width // 2
        h = self.height // 2
        for i in range(4):
            self.reticle[i] = self.canvas.create_line(
                w + 3 * (i == 2) - 10 * (i == 3),
                h + 3 * (i == 0) - 10 * (i == 1),
                w + 11 * (i == 2) - 2 * (i == 3),
                h + 11 * (i == 0) - 2 * (i == 1),
                fill="gray70",
                tags="reticle",
            )

    def show_frontground(self, event: Event = None) -> None:
        w = self.width // 2
        h = self.height // 2
        for i in range(4):
            id = self.reticle[i]
            self.canvas.coords(
                id,
                w + 3 * (i == 2) - 10 * (i == 3),
                h + 3 * (i == 0) - 10 * (i == 1),
                w + 11 * (i == 2) - 2 * (i == 3),
                h + 11 * (i == 0) - 2 * (i == 1),
            )
            self.canvas.lift(id)

    def coord2pix(self, coordarray: np.ndarray) -> np.ndarray:
        """
        Takes coordinates in 2D array like [x0,y0,x1,y1,...]
        and returns pixel coordinates array in same shape.
        """
        pixarray = np.zeros_like(coordarray, dtype=int)
        pixarray[0::2] = (
            coordarray[0::2] * self.pixgrid + self.x + self.dotsize // 2
        ).astype(int)
        pixarray[1::2] = (
            -coordarray[1::2] * self.pixgrid + self.y + self.dotsize // 2
        ).astype(int)
        return pixarray

    def pix2coord(self, pixx: int, pixy: int) -> tuple[float, float]:
        # 1 pixel difference because of the background
        coordx = (pixx - self.dotsize // 2 - self.x) / self.pixgrid
        # again Minus because y inverted
        coordy = -(pixy - self.dotsize // 2 - self.y) / self.pixgrid
        return coordx, coordy
