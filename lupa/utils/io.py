import pandas as pd
import json
import numpy as np
from tkinter import filedialog
from tkinter.messagebox import showerror
from typing import Optional, Tuple


def readvalues(file_name: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Read values from a tab-separated CSV file and return time and value arrays.

    Args:
        file_name (str): The name of the CSV file.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Arrays of time and values.
    """
    df = pd.read_csv(file_name, sep="\t")
    time_column = df.columns[0]
    value_column = df.columns[1]
    return df[time_column].to_numpy(dtype=float), df[value_column].to_numpy(dtype=float)


def savetojson(data: dict, filename: Optional[str] = None) -> Optional[str]:
    """
    Save a dictionary to a JSON file.

    Args:
        data (dict): The data to save.
        filename (Optional[str]): The name of the file. If None, a file dialog
        will open.

    Returns:
        Optional[str]: The name of the file where data was saved, or None if
        the operation was canceled.
    """
    if filename is None:
        outfile = filedialog.asksaveasfile(
            initialfile="circuit.json",
            defaultextension=".json",
            filetypes=[("All Files", "*.*"), ("JSON", "*.json")],
        )
        if outfile is None:
            return None
    else:
        outfile = open(filename, "w")

    json_str = json.dumps(data, indent=4)
    outfile.write(json_str)
    outfile.close()
    return outfile.name if filename is None else filename


def loadfromjson(
    filename: Optional[str] = None,
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Load a dictionary from a JSON file.

    Args:
        filename (Optional[str]): The name of the file. If None, a file dialog
        will open.

    Returns:
        Tuple[Optional[dict], Optional[str]]: The loaded data and the filename,
        or (None, None) if the operation was canceled.
    """
    if filename is None:
        infile = filedialog.askopenfile(
            filetypes=[("All Files", "*.*"), ("JSON", "*.json")]
        )
        if infile is None:
            return None, None
    else:
        try:
            infile = open(filename, "r")
        except FileNotFoundError:
            showerror("File Not Found", f"The file {filename} does not exist.")
            return None, None

    data = json.load(infile)
    infile.close()
    return data, infile.name if filename is None else filename
