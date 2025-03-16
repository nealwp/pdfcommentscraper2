from tkinter import Tk, LEFT, Canvas, Scrollbar, Button, Label, Toplevel, Frame

class CommentViewer(Toplevel):
    def __init__(self, parent, comments):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Comments')

        self.container = Frame(self)
        self.canvas = Canvas(self.container)
        self.scrollbar = Scrollbar(self.container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        for row, comment in enumerate(comments):
            txtbox = Label(self.scrollable_frame, wraplength=350, justify=LEFT, borderwidth=1)
            txtbox.configure(text=comment)
            txtbox.pack(padx=15, pady=15, anchor='w')
            #txtbox.configure(state='disabled')

        self.container.pack()
        self.canvas.pack(side='left', fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.close_btn = Button(self, text='Close', width=12, command=self.destroy)
        self.close_btn.pack()

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

def main():

    app = Tk()
    comments = [
        "this is a comment",
        "this is another comment",
        "this is a third comment",
        "this is a really long comment with lots of things to say, could potentially be as long as \
        a whole paragraph, longest thing you've ever seen. Maybe longer than that. Who knows? \
        Not me, I'm not much of comment measurer myself."
        ]
    comment_viewer = CommentViewer(app, comments)
    app.mainloop()
    return

if __name__ == '__main__':
    main()