from tkinter import Tk, X, BOTTOM
from ui.statusbar import StatusBar
from ui.menubar import MenuBar


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

        self.attributes('-alpha', 1.0)


if __name__ == '__main__':
    app = App()
    app.mainloop()
