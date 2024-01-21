from tkinter import Frame, SUNKEN, Label, W


class StatusBar(Frame):

    def __init__(self, parent):
        super().__init__(parent, bd=1, relief=SUNKEN)
        self.parent = parent

        self.status = Label(self, anchor=W, padx=5)
        self.status.grid(column=0, row=0, sticky='w', columnspan=1)

        self.columnconfigure(0, weight=1)

    def set_status(self, message):
        self.status.configure(text=message)

    def clear_status(self):
        self.status.configure(text=None)
