from tkinter import Tk, Button, Label, Entry, Toplevel
from .helpers import on_enter, on_leave, center
from controllers.appconfig import AppConfig

config = AppConfig()

class ContextSizeForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.attributes('-alpha', 0.0)
        self.title('Context Size Settings')

        words_minus_label = Label(self, text="Words Before Keyword:")
        words_minus_label.grid(column=0, row=0, sticky='w', padx=10, pady=3)
        
        self.words_minus_entry = Entry(self, width=3, bd=1)
        self.words_minus_entry.grid(column=1, row=0, sticky='e', padx=10, pady=3)
        
        words_plus_label = Label(self, text="Words After Keyword:")
        words_plus_label.grid(column=0, row=1, sticky='w', padx=10, pady=3)
        
        self.words_plus_entry = Entry(self, width=3, bd=1)
        self.words_plus_entry.grid(column=1, row=1, sticky='e', padx=10, pady=3)

        done_btn = Button(self, text='Apply', command=self.save_context_settings)
        done_btn.bind("<Enter>", on_enter)
        done_btn.bind("<Leave>", on_leave)
        done_btn.grid(column=0, row=3, columnspan=2, pady=3)
        
        self.get_context_settings()
        center(self)
        self.attributes('-alpha', 1.0)

    def get_context_settings(self):
        self.words_minus_entry.insert(0, config.keywords_context_before)
        self.words_plus_entry.insert(0, config.keywords_context_after)

    def save_context_settings(self):
        config.keywords_context_before = self.words_minus_entry.get()
        config.keywords_context_after = self.words_plus_entry.get()
        config.save()
        self.destroy()

def main():
    app = Tk()
    context_settings = ContextSizeForm(app)
    app.mainloop()
    return

if __name__ == '__main__':
    main()