import re
from tkinter import Tk, BOTTOM, X

from view.statusbar import StatusBar
from view.menubar import MenuBar

class App(Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.attributes('-alpha', 0.0)
        self.geometry('809x500')
        self.title('disabilitydude')

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=BOTTOM, fill=X)

        self.menubar = MenuBar(self)        
        self.config(menu=self.menubar)
        
        center(self)
        self.attributes('-alpha', 1.0)

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

def findWholeWord(w):
    return re.compile(r'\b^({0})$\b'.format(w), flags=re.IGNORECASE).search

if __name__ == '__main__':
    app = App()
    app.mainloop()