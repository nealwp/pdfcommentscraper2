from tkinter import Tk, LEFT, Canvas, Scrollbar, Button, Label, Toplevel, Frame

from helpers import center

class CommentViewer(Toplevel):
    def __init__(self, parent):
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
        
        for row, exhibit in enumerate(self.parent.medical_record.exhibits):
            #print(exhibit)
            for row, comment in enumerate(self.parent.medical_record.exhibits[exhibit].comments):
                txtbox = Label(self.scrollable_frame, wraplength=500, justify=LEFT, borderwidth=1)
                txtbox.configure(text=comment.text)
                txtbox.pack(padx=15, pady=15, anchor='w')
                #txtbox.configure(state='disabled')

        self.container.pack()
        self.canvas.pack(side='left', fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.close_btn = Button(self, text='Close', width=12, command=self.destroy)
        self.close_btn.pack()

        center(self)
        self.attributes('-alpha', 1.0)

def main():

    app = Tk()
    app.medical_record = {
        'exhibits': {
            '1A': {
                'comments': [
                    {'text': 'something something something'},
                    {'text': 'another couple words'}
                ]
            }
        }
    }
    comment_viewer = CommentViewer(app)
    app.mainloop()
    return

if __name__ == '__main__':
    main()