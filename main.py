import re
from tkinter import Tk, BOTTOM, X

from components.forms.statusbar import StatusBar
from components.forms.menubar import MenuBar
from components.forms.helpers import center

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

def findWholeWord(w):
    return re.compile(r'\b^({0})$\b'.format(w), flags=re.IGNORECASE).search

if __name__ == '__main__':
    app = App()
    app.mainloop()