from tkinter import Tk, Toplevel
from tkinter.ttk import Button, Frame, Label
import traceback

from helpers import center

class ErrorDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Error')
        self.container = Frame(self)

        Label(
            self.container,
            text="An error occurred:",
            justify='left'
        ).grid(column=0, row=0, sticky='w', pady=2)

        Label(
            self.container, 
            text=traceback.format_exc(), 
            anchor='w', 
            justify='left', 
            font=('Consolas', 10),
            background='#fff'
        ).grid(column=0, row=1, sticky='w', pady=2)

        self.container.pack()
        Button(self, text='Close', width=12, command=self.destroy).pack(pady=2)

        center(self)
        self.attributes('-alpha', 1.0)

def main():
    app = Tk()
    try:
        dummy_list = ['just', 'kidding']
        bad_index = dummy_list[2]
        print(bad_index)
    except Exception as err:
        dialog = ErrorDialog(app)
    app.mainloop()
    return

if __name__ == '__main__':
    main()