from csv import writer, QUOTE_MINIMAL
from os import path, remove
from re import sub
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from datetime import date, datetime


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
    file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path


def get_save_path(file_type) -> str:
    """ Displays save as dialog and return a file path """
    types = {
        'csv': ('CSV Files', '*.csv'),
        'docx': ('MS Word Files', '*.docx')
    }

    save_as_type = types[file_type]

    save_path = asksaveasfilename(filetypes=[save_as_type], defaultextension=[save_as_type])
    return save_path


def strip_non_printable_chars(str) -> str:
    fixed = sub('[^A-Za-z0-9\.\,\!\:\;\(\)\'\"\\n\-\/]+', ' ', str)
    return fixed


def get_age(birthdate):
    today = date.today()
    birthdate = datetime.strptime(birthdate, '%m/%d/%Y')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def get_age_at_onset(birthdate, onset_date):
    birthdate = datetime.strptime(birthdate, '%m/%d/%Y')
    onset_date = datetime.strptime(onset_date, '%m/%d/%Y')
    age_at_onset = onset_date.year - birthdate.year - ((onset_date.month, onset_date.day) < (birthdate.month, birthdate.day))
    return age_at_onset
