from tkinter import Toplevel, Label, LEFT, Button


class ErrorDialog(Toplevel):
    def __init__(self, parent, error):
        super().__init__(parent)
        self.title("Error")
        Label(self, text=error, anchor='w', justify=LEFT).pack(pady=5, padx=5)

        Button(self, text='Close', command=self.destroy).pack(pady=10)

        self.transient(parent)
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
