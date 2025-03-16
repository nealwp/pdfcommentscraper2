from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def on_enter(e):
    e.widget['background'] = '#ddd'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

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