import tkinter as tk
from lupa.GUI.drawingboard import DrawingBoard
import os
import sys
import argparse
import logging
from importlib.metadata import version as pkg_version

# App metadata
APP_NAME = "LUPA"
try:
    APP_VERSION = pkg_version(APP_NAME)
except Exception:
    APP_VERSION = "0.1.0"

# Recent files location (user data dir)
try:
    from platformdirs import user_data_dir
except Exception:
    # Minimal fallback for environments without platformdirs
    def user_data_dir(appname: str, appauthor: bool = False):
        return os.path.join(os.path.expanduser("~/.local/share"), appname)


class MainWindow(tk.Tk):

    ICON_PATHS = [
        "img/icons/LUPA_16.png",
        "img/icons/LUPA_32.png",
        "img/icons/LUPA_48.png",
        "img/icons/LUPA_64.png",
        "img/icons/LUPA_128.png",
        "img/icons/LUPA_256.png",
    ]
    RECENT_FILES_BASENAME = "recent_files.log"
    MAX_RECENT_FILES = 10

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)

        # Set app ID for Windows taskbar grouping
        if sys.platform == "win32":
            try:
                import ctypes

                myappid = f"{APP_NAME}.{APP_VERSION}"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except ImportError:
                pass  # ctypes not available

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.drbd = DrawingBoard(self)
        self.recent_files = []
        self.filename = None
        self.read_recent_files()
        self.set_icons()
        self.set_menubars()

    @property
    def recent_files_path(self) -> str:
        data_dir = user_data_dir(APP_NAME, appauthor=False)
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, self.RECENT_FILES_BASENAME)

    def set_icons(self):
        icons = [tk.PhotoImage(file=path) for path in self.ICON_PATHS]
        self.iconphoto(False, *icons)

    def set_menubars(self):
        self.option_add("*tearOff", False)
        menubar = tk.Menu(self)
        self["menu"] = menubar
        menu_file = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")
        menubar.add_cascade(menu=menu_edit, label="Edit")

        menu_file.add_command(label="New", command=self.new_file)
        self.menu_recent = tk.Menu(menu_file)
        menu_file.add_cascade(menu=self.menu_recent, label="Open Recent")
        self._rebuild_recent_menu()

        menu_file.add_command(label="Open", command=self.open_file)
        menu_file.add_command(
            label="Save", command=self.save_file, accelerator="Ctrl+s"
        )
        menu_file.add_command(
            label="Close", command=self.close_file, accelerator="Ctrl+x"
        )
        self.bind("<Control-s>", lambda e: self.save_file(self.filename))
        self.bind("<Control-o>", lambda e: self.open_most_recent_file())
        self.bind("<Control-x>", lambda e: self.close_file())

    def _rebuild_recent_menu(self):
        self.menu_recent.delete(0, "end")
        existing = [
            f for f in self.recent_files if isinstance(f, str) and os.path.exists(f)
        ]
        self.recent_files = existing[-self.MAX_RECENT_FILES :]
        for i, f in enumerate(reversed(self.recent_files)):
            accelerator = "Ctrl+o" if i == 0 else None
            self.menu_recent.add_command(
                label=os.path.basename(f),
                command=lambda f=f: self.open_file(f),
                accelerator=accelerator,
            )

    def read_recent_files(self):
        try:
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, "r") as f:
                    lines = [line.strip() for line in f if line.strip()]
                seen = set()
                ordered = []
                for p in lines:
                    ap = os.path.abspath(p)
                    if ap not in seen and os.path.exists(ap):
                        seen.add(ap)
                        ordered.append(ap)
                self.recent_files = ordered[-self.MAX_RECENT_FILES :]
        except Exception as e:
            logging.getLogger(APP_NAME).warning("Failed to read recent files: %s", e)
            self.recent_files = []

    def write_recent_files(self):
        try:
            with open(self.recent_files_path, "w") as f:
                for filename in self.recent_files[-self.MAX_RECENT_FILES :]:
                    f.write(filename + "\n")
        except Exception as e:
            logging.getLogger(APP_NAME).warning("Failed to write recent files: %s", e)

    def add_recent_file(self, filename=None):
        if not filename:
            return
        filename = os.path.abspath(filename)
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.append(filename)
        if len(self.recent_files) > self.MAX_RECENT_FILES:
            self.recent_files = self.recent_files[-self.MAX_RECENT_FILES :]
        self._rebuild_recent_menu()
        self.write_recent_files()

    def new_file(self):
        self.drbd.destroy()
        self.filename = None
        self.drbd = DrawingBoard(self)

    def open_most_recent_file(self):
        if self.recent_files:
            self.open_file(self.recent_files[-1])
        else:
            self.open_file()

    def open_file(self, filename=None):
        self.drbd.destroy()
        self.drbd = DrawingBoard(self)
        self.filename = self.drbd.load(filename)
        self.add_recent_file(self.filename)

    def save_file(self, filename=None):
        self.filename = self.drbd.save(filename)
        self.add_recent_file(self.filename)

    def close_file(self):
        # Placeholder for actual close file logic
        pass


def main():
    """Entry point for the LUPA application."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    logger = logging.getLogger(APP_NAME)

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Lumped-Parameter Analysis", prog="lupa"
    )
    parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} {APP_VERSION}"
    )
    parser.add_argument("file", nargs="?", help="Circuit file to open on startup")

    args = parser.parse_args()

    try:
        root = MainWindow()

        # If a file was specified, try to open it
        if args.file:
            if os.path.exists(args.file):
                root.open_file(args.file)
            else:
                logger.warning("File not found: %s", args.file)

        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception:
        logging.getLogger(APP_NAME).exception("Error starting %s", APP_NAME)
        raise


if __name__ == "__main__":
    main()
