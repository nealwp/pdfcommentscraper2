import re
from time import perf_counter
from csv import writer, DictWriter
from tkinter import END, Listbox, Scrollbar, StringVar, Tk, Button, Label, Entry, Toplevel, Menu, Frame, SUNKEN, N, S, E, W, BOTTOM, X

from commentscraper import scrape_comments
from keywordscan import scanforkeywords

from helpers import write_csv, get_file_path, get_save_path

def findWholeWord(w):
    return re.compile(r'\b^({0})$\b'.format(w), flags=re.IGNORECASE).search

def run_keyword_scan():

    fieldnames = ['keyword', 'page', 'text', 'exhibit', 'provider', 'exhibit_page']

    pdf_path = get_file_path()
    debut = perf_counter()
    output = scanforkeywords(pdf_path)
    fin = perf_counter()
    output_path = get_save_path()
    with open(output_path,'w',encoding='utf-8', newline='') as f:
        csvdw = DictWriter(f, fieldnames=fieldnames)
        csvdw.writeheader()
        csvdw.writerows(output)
    print(f"Completed in {fin - debut:0.4f}s")
    return

def read_keywords_file():
    with open(r".\\config\\keywords", "r") as keyword_file:
        file_content = keyword_file.read()
        keywords = file_content.split('\n')
        keywords = [w for w in keywords if w]
        keywords.sort()
    return keywords

def add_keyword(word, entrybox):
    entrybox.delete(0, END)
    with open(r".\\config\\keywords", "a") as keyword_file:
        keyword_file.write(word + '\n')
    return

def delete_keyword(word):
    keywords = read_keywords_file()
    for i, kw in enumerate(keywords):
        if kw == word:
            keywords.pop(i)
    
    with open(r".\\config\\keywords", "w") as keyword_file:
        keyword_file.writelines(kw + '\n' for kw in keywords)
    return

def run_commentscraper():
    scrape_comments()
    return

def on_enter(e):
    e.widget['background'] = '#ddd'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

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

def open_keywords_menu(root):

    keywords = read_keywords_file()

    win = Toplevel(root)
    win.attributes('-alpha', 0.0)
    win.title('Keywords Settings')

    leftFrame = Frame(win)
    leftFrame.grid(column=0, row=1)

    entrylabel = Label(leftFrame, text='New Keyword')
    entrylabel.grid(column=0, row=0, sticky='sw', rowspan=1, padx=10)

    entrybox = Entry(leftFrame, width=24, bd=1)
    entrybox.grid(column=0, row=1, sticky='nw', rowspan=1, columnspan=1, padx=10)

    addBtn = Button(leftFrame, text='Add', command=lambda: add_keyword(entrybox.get(), entrybox))
    addBtn.grid(column=0, row=2, pady=10)
    addBtn.bind("<Enter>", on_enter)
    addBtn.bind("<Leave>", on_leave)

    rightFrame = Frame(win)
    rightFrame.grid(column=1, row=1, pady=10)
    
    keywordboxlabel = Label(rightFrame, text='Active Keywords')
    keywordboxlabel.grid(column=0, row=0, sticky='nw', rowspan=1)

    listbox = Listbox(rightFrame, height=16, selectmode='single', activestyle='none')
    for i, kw in enumerate(keywords):
        listbox.insert(i, kw)

    listbox.grid(column=0, row=1, sticky='nw')

    scrollbar = Scrollbar(rightFrame, orient='vertical', command=listbox.yview)
    scrollbar.grid(column=1, row=1, sticky='nsw')
    listbox['yscrollcommand'] = scrollbar.set

    deleteBtn = Button(rightFrame, text='Delete Selected', command=lambda: delete_keyword(listbox.get(listbox.curselection())))
    deleteBtn.grid(column=0, row=2, pady=10)
    deleteBtn.bind("<Enter>", on_enter)
    deleteBtn.bind("<Leave>", on_leave)
    
    doneBtn = Button(win, text='Done', command=win.destroy)
    doneBtn.bind("<Enter>", on_enter)
    doneBtn.bind("<Leave>", on_leave)
    doneBtn.grid(column=0, row=3, columnspan=2, pady=10)
    center(win)
    win.attributes('-alpha', 1.0)
    win.mainloop()

def open_context_size_menu(root):
    win = Toplevel(root, padx=15, pady=15)
    win.attributes('-alpha', 0.0)
    win.title('Context Size Settings')

    words_minus_label = Label(win, text="Words Before Keyword:")
    words_minus_label.grid(column=0, row=0, sticky='w', padx=10)
    
    words_minus_entry = Entry(win, width=3, bd=1)
    words_minus_entry.grid(column=1, row=0, sticky='e', padx=10)
    
    words_plus_label = Label(win, text="Words After Keyword:")
    words_plus_label.grid(column=0, row=1, sticky='w', padx=10)
    
    words_plus_entry = Entry(win, width=3, bd=1)
    words_plus_entry.grid(column=1, row=1, sticky='e', padx=10)

    done_btn = Button(win, text='Done', command=win.destroy)
    done_btn.bind("<Enter>", on_enter)
    done_btn.bind("<Leave>", on_leave)
    done_btn.grid(column=0, row=3, columnspan=2)
    
    center(win)
    win.attributes('-alpha', 1.0)
    win.mainloop()
    return

def main() -> None:

    root = Tk()
    root.attributes('-alpha', 0.0)
    root.geometry('809x500')
    """ menu bar setup """
    menubar = Menu(root, bd=5)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)
    
    actions_menu = Menu(menubar, tearoff=0)
    actions_menu.add_command(label="Scan PDF for Keywords", command=run_keyword_scan)
    actions_menu.add_command(label="Scrape Comments from PDF", command=run_commentscraper)
    menubar.add_cascade(label="Actions", menu=actions_menu)

    settingsmenu = Menu(menubar, tearoff=0)
    settingsmenu.add_command(label="Keywords", command=lambda: open_keywords_menu(root))
    settingsmenu.add_command(label="Context Size", command=lambda: open_context_size_menu(root))
    menubar.add_cascade(label="Settings", menu=settingsmenu)

    menubar.add_command(label="Help")
    
    root.config(menu=menubar)

    status_bar = Frame(root, bd=1, relief=SUNKEN)
    
    status_message = Label(status_bar, text="Ready", anchor=W, padx=5)
    status_message.grid(column=0, row=0, sticky='w', columnspan=1)
    
    version_label = Label(status_bar, text='v1.0.0', anchor=E, padx=5)
    version_label.grid(column=1, row=0, sticky="e", columnspan=1)

    status_bar.columnconfigure(0, weight=1)

    status_bar.pack(side=BOTTOM, fill=X)

    root.title('disabilitydude')
    center(root)
    root.attributes('-alpha', 1.0)
    root.mainloop()
    return


if __name__ == '__main__':
    main()