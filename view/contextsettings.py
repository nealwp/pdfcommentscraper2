from tkinter import Tk, Button, Label, Entry, Toplevel
from shared.helpers import on_enter, on_leave, center

class ContextSizeForm(Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent, padx=15, pady=15)
        self.attributes('-alpha', 0.0)
        self.title('Context Size Settings')

        words_minus_label = Label(self, text="Words Before Keyword:")
        words_minus_label.grid(column=0, row=0, sticky='w', padx=10, pady=3)
        
        self.words_minus_entry = Entry(self, width=3, bd=1)
        self.words_minus_entry.grid(column=1, row=0, sticky='e', padx=10, pady=3)
        self.words_minus_entry.insert(0, config.keywords_context_before)
          
        words_plus_label = Label(self, text="Words After Keyword:")
        words_plus_label.grid(column=0, row=1, sticky='w', padx=10, pady=3)
        
        self.words_plus_entry = Entry(self, width=3, bd=1)
        self.words_plus_entry.grid(column=1, row=1, sticky='e', padx=10, pady=3)
        self.words_plus_entry.insert(0, config.keywords_context_after)

        done_btn = Button(self, text='Apply', command=self.save_context_settings)
        done_btn.bind("<Enter>", on_enter)
        done_btn.bind("<Leave>", on_leave)
        done_btn.grid(column=0, row=3, columnspan=2, pady=3)
        
        center(self)
        self.attributes('-alpha', 1.0)

    def save_context_settings(self):
        keywords_context_before = self.words_minus_entry.get()
        keywords_context_after = self.words_plus_entry.get()
        # do something with these values before close
        self.destroy()

def main():

    class MockConfig:
        keywords_context_before = 5
        keywords_context_after = 5

    app = Tk()
    config = MockConfig()
    context_settings = ContextSizeForm(app, config)
    app.mainloop()
    return

if __name__ == '__main__':
    main()