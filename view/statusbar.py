from tkinter import BOTTOM, X, Tk, Label, Frame, SUNKEN, E, W

class StatusBar(Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bd=1, relief=SUNKEN)
        self.parent = parent
                
        self.status = Label(self, text='Ready', anchor=W, padx=5)
        self.status.grid(column=0, row=0, sticky='w', columnspan=1)
        
        self.version = Label(self, text='error', anchor=E, padx=5)
        self.version.grid(column=1, row=0, sticky="e", columnspan=1)
        self.get_app_version()

        self.columnconfigure(0, weight=1)

    def set_status(self, message):
        self.status.configure(text=message)

    def reset_status(self):
        self.status.configure(text='Ready')
    
    def get_app_version(self):
        version = 'Fix this later' # TODO: get_app_version() 
        self.version.config(text=f"v{version}")


def main():
    app = Tk()
    app.status_bar = StatusBar(app)
    app.status_bar.pack(side=BOTTOM, fill=X)
    app.mainloop()
    return

if __name__ == '__main__':
    main()