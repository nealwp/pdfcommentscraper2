from time import perf_counter

from csv import writer, DictWriter, QUOTE_MINIMAL

from os import path, remove, system
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

def write_csv(file_name: str, heads: list, rows: list) -> None:
    """ Take a path, header list, and 2D list of data rows and writes to CSV file """
    if path.exists(file_name):
        remove(file_name)

    with open(file_name, 'w', newline='') as cf:
        cw = writer(cf, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        cw.writerow(heads)
        [cw.writerow(row) for row in rows]
    return


def get_file_path() -> str:
    """ Displays open dialog and returns a file path """
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path


def get_save_path() -> str:
    """ Displays save as dialog and return a file path """
    Tk().withdraw()
    save_path = asksaveasfilename(filetypes=[("CSV Files", "*.csv")], defaultextension=[("CSV Files", "*.csv")])
    return save_path