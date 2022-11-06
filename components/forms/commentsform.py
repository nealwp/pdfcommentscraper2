from tkinter import Tk, LEFT, Canvas, Scrollbar, Button, Label, Toplevel, Frame

from .helpers import center

class CommentViewer(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Work History')

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
        
        for row, comment in enumerate(self.parent.pdf_comments):
            txtbox = Label(self.scrollable_frame, wraplength=500, justify=LEFT, bg="white", borderwidth=1)
            txtbox.configure(text=comment['text'])
            txtbox.pack()
            #txtbox.configure(state='disabled')

        self.container.pack()
        self.canvas.pack(side='left', fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.close_btn = Button(self, text='Close', width=12, command=self.destroy)
        self.close_btn.pack()

        center(self)
        self.attributes('-alpha', 1.0)

def main():
    return

if __name__ == '__main__':
    main()