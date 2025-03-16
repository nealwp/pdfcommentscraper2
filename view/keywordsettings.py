from tkinter import Tk, END, Listbox, Scrollbar, Button, Label, Entry, Toplevel, Frame
from shared.helpers import on_enter, on_leave, center

class KeywordSettingsForm(Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent, padx=15, pady=15)

        self.parent = parent
        self.config = config
        self.attributes('-alpha', 0.0)
        self.title('Keyword Settings')

        self.leftFrame = Frame(self)
        self.leftFrame.grid(column=0, row=1)

        self.entrylabel = Label(self.leftFrame, text='New Keyword')
        self.entrylabel.grid(column=0, row=0, sticky='sw', rowspan=1, padx=10)

        self.entrybox = Entry(self.leftFrame, width=24, bd=1)
        self.entrybox.grid(column=0, row=1, sticky='nw', rowspan=1, columnspan=1, padx=10)

        self.addBtn = Button(self.leftFrame, text='Add', command=self.add_keyword)
        self.addBtn.grid(column=0, row=2, pady=10)
        self.addBtn.bind("<Enter>", on_enter)
        self.addBtn.bind("<Leave>", on_leave)
        self.rightFrame = Frame(self)
        self.rightFrame.grid(column=1, row=1, pady=10)

        self.keywordboxlabel = Label(self.rightFrame, text='Active Keywords')
        self.keywordboxlabel.grid(column=0, row=0, sticky='nw', rowspan=1)

        self.listbox = Listbox(self.rightFrame, height=16, selectmode='single', activestyle='none')
        for i, kw in enumerate(config.keywords):
            self.listbox.insert(i, kw)

        self.listbox.grid(column=0, row=1, sticky='nw')

        self.scrollbar = Scrollbar(self.rightFrame, orient='vertical', command=self.listbox.yview)
        self.scrollbar.grid(column=1, row=1, sticky='nsw')
        self.listbox['yscrollcommand'] = self.scrollbar.set

        self.deleteBtn = Button(self.rightFrame, text='Delete Selected', command=self.delete_keyword)
        self.deleteBtn.grid(column=0, row=2, pady=10)
        self.deleteBtn.bind("<Enter>", on_enter)
        self.deleteBtn.bind("<Leave>", on_leave)
        
        doneBtn = Button(self, text='Done', command=self.destroy)
        doneBtn.bind("<Enter>", on_enter)
        doneBtn.bind("<Leave>", on_leave)
        doneBtn.grid(column=0, row=3, columnspan=2, pady=10)
     
        center(self)
        self.attributes('-alpha', 1.0)

    def add_keyword(self):
        word = self.entrybox.get()
        self.entrybox.delete(0, END)
        self.config.keywords.append(word)
        self.refresh_keyword_listbox() 

    def refresh_keyword_listbox(self):
        self.listbox.delete(0, END)
        for i, kw in enumerate(self.config.keywords):
            self.listbox.insert(i, kw)

    def delete_keyword(self):
        selected = self.listbox.curselection()
        if selected:
            self.config.keywords.pop(selected[0])
            self.refresh_keyword_listbox()

def main():

    class MockConfig:
        def __init__(self):
            self.keywords = ["bob", "alice", "word", "something", "tool"]
        def __getitem__(self, item):
            return self.config[item]

    app = Tk()
    config = MockConfig()
    keyword_settings = KeywordSettingsForm(app, config)
    app.mainloop()
    return

if __name__ == '__main__':
    main()