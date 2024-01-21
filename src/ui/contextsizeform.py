from tkinter import Toplevel, Label, Entry, Button
from configparser import ConfigParser


config = ConfigParser()


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

        done_btn = Button(self, text='Apply', command=self._set_context_settings)
        done_btn.grid(column=0, row=3, columnspan=2, pady=3)

        self._get_context_settings()
        self.attributes('-alpha', 1.0)

    def _get_context_settings(self):
        config.read('./config/config.ini')
        self.words_minus_entry.insert(0, config['Keywords']['ContextBefore'])
        self.words_plus_entry.insert(0, config['Keywords']['ContextAfter'])

    def _set_context_settings(self):
        context_before = self.words_minus_entry.get()
        context_after = self.words_plus_entry.get()

        config.read('./config/config.ini')
        config['Keywords']['ContextBefore'] = context_before
        config['Keywords']['ContextAfter'] = context_after
        with open('./config/config.ini', 'w') as configfile:
            config.write(configfile)
