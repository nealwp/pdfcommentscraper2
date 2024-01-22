from tkinter import Toplevel, Label, Listbox, Button, Scrollbar, Frame, Entry, END
from configparser import ConfigParser

config = ConfigParser()


class KeywordSettingsForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)

        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Keyword Settings')

        self.leftFrame = Frame(self)
        self.leftFrame.grid(column=0, row=1)

        self.entrylabel = Label(self.leftFrame, text='New Keyword')
        self.entrylabel.grid(column=0, row=0, sticky='sw', rowspan=1, padx=10)

        self.entrybox = Entry(self.leftFrame, width=24, bd=1)
        self.entrybox.grid(column=0, row=1, sticky='nw', rowspan=1, columnspan=1, padx=10)

        self.addBtn = Button(self.leftFrame, text='Add', command=self._add_keyword)
        self.addBtn.grid(column=0, row=2, pady=10)

        self.rightFrame = Frame(self)
        self.rightFrame.grid(column=1, row=1, pady=10)

        self._get_keywords()

        self.keywordboxlabel = Label(self.rightFrame, text='Active Keywords')
        self.keywordboxlabel.grid(column=0, row=0, sticky='nw', rowspan=1)

        self.listbox = Listbox(self.rightFrame, height=16, selectmode='single', activestyle='none')
        for i, kw in enumerate(self.keywords):
            self.listbox.insert(i, kw)

        self.listbox.grid(column=0, row=1, sticky='nw')

        self.scrollbar = Scrollbar(self.rightFrame, orient='vertical', command=self.listbox.yview)
        self.scrollbar.grid(column=1, row=1, sticky='nsw')
        self.listbox['yscrollcommand'] = self.scrollbar.set

        self.deleteBtn = Button(self.rightFrame, text='Delete Selected', command=self._delete_keyword)
        self.deleteBtn.grid(column=0, row=2, pady=10)

        doneBtn = Button(self, text='Done', command=self.destroy)
        doneBtn.grid(column=0, row=3, columnspan=2, pady=10)

        self.attributes('-alpha', 1.0)

    def _add_keyword(self):
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        word = self.entrybox.get()
        self.entrybox.delete(0, END)
        with open(kw_file_path, "a") as keyword_file:
            keyword_file.write(word + '\n')
        self._refresh_keyword_listbox()

    def _get_keywords(self):
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        with open(kw_file_path, "r") as keyword_file:
            file_content = keyword_file.read()
            keywords = file_content.split('\n')
            keywords = [w for w in keywords if w]
            keywords.sort()
            self.keywords = keywords

    def _refresh_keyword_listbox(self):
        self.listbox.delete(0, END)
        self._get_keywords()
        for i, kw in enumerate(self.keywords):
            self.listbox.insert(i, kw)

    def _delete_keyword(self):
        idx = self.listbox.curselection()
        word = self.listbox.get(idx)
        for i, kw in enumerate(self.keywords):
            if kw == word:
                self.keywords.pop(i)
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        with open(kw_file_path, "w") as keyword_file:
            keyword_file.writelines(kw + '\n' for kw in self.keywords)
        self.listbox.delete(idx)
