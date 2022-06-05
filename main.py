from io import StringIO
from pickle import HIGHEST_PROTOCOL
from time import perf_counter
import sys

from pdfminer.high_level import extract_text_to_fp

from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef, PDFStream

from csv import writer, DictWriter, QUOTE_MINIMAL
import re
from PyPDF2 import PdfFileReader
from PyPDF2.generic import ByteStringObject


from os import path, remove, system
from pathlib import Path
from tkinter import Listbox, Scrollbar, StringVar, Tk, Button, Label, Entry, Toplevel, Menu, Frame, SUNKEN, N, S, E, W, BOTTOM, X
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox

from keywordscan import scanforkeywords
from helpers import write_csv, get_file_path, get_save_path

class ErrorLog:
    """ Error log object """
    def __init__(self):
        self.errors = []
        self.dest = ""

    def __len__(self) -> int:
        return len(self.errors)

    def __set_dest(self, orig_dest) -> None:
        self.dest = str(Path(orig_dest).with_suffix('')) + "_errors.txt"
        return

    def get_dest(self) -> str:
        return self.dest

    def log(self, err_message: str) -> None:
        self.errors.append(err_message)
        return

    def to_string(self) -> str:
        output = ''.join(err for err in self.errors)
        # for err in self.errors:
        #    output = output + err
        return output

    def to_file(self, orig_dest: str) -> None:
        self.__set_dest(orig_dest)
        with open(self.dest, 'w') as err_file:
            err_file.writelines(self.errors)
        return


class SummaryData:

    def __init__(self):

        self.comments = []
        self.bookmarks = {}
        self.errors = ErrorLog()
        self.src = ""
        self.pdf = None
        self.page_count = 0
        self.outlines = []
        self.delimiter = ";"
        self.headers = ['date', 'note', 'provider', 'exhibit', 'page']
        self.dest = ""

        self.__set_src()
        if path.exists(self.src):
            self.__set_pdf()
            self.__set_page_count()
            self.__set_outlines()
        else:
            self.errors.log(''.join(["ERROR: File ", self.src, "not found!"]))

    def __set_src(self) -> None:
        Tk().withdraw()
        self.src = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        return

    def __set_pdf(self) -> None:
        self.pdf = PdfFileReader(self.src)
        return

    def __set_page_count(self) -> None:
        self.page_count = self.pdf.getNumPages()
        return

    def __set_outlines(self) -> None:
        self.outlines = self.pdf.getOutlines()
        return

    def __set_dest(self) -> None:
        """ Displays save as dialog and return a file path """
        Tk().withdraw()
        save_path = asksaveasfilename(filetypes=[("CSV Files", "*.csv")], defaultextension=[("CSV Files", "*.csv")])
        self.dest = save_path
        return

    def set_bookmarks(self) -> None:
        # self.bookmarks = find_bookmarks_in_pdf(self.pdf)
        self.bookmarks = get_bookmarks(self.pdf, self.outlines, self.errors)
        return

    def set_comments(self) -> None:

        for i in range(self.page_count):
            error_raised = False
            active_page = self.pdf.getPage(i)
            page_number = i + 1
            text = active_page.extractText().split()
            try:
                for annotation in active_page['/Annots']:
                    annot_dict = annotation.getObject()
                    raw_comment = annot_dict.get('/Contents', None)

                    if raw_comment is not None:
                        # decode the comments when they have weird chars that get interpreted as ByteStrings
                        if type(raw_comment) is ByteStringObject:
                            try:
                                comment = raw_comment.decode('utf-8')
                            except UnicodeDecodeError as ude:
                                comment = ""
                                error_raised = True
                                error_message = "".join(["Error in comment on page ",
                                                         str(page_number), ":\n",
                                                        "Try checking the comment for funky characters. ",
                                                         "Removing them should fix this error.\n",
                                                         "ERROR_MSG: ", str(ude), "\n\n"])
                                self.errors.log(error_message)
                        else:
                            comment = raw_comment

                        if comment.count(self.delimiter) > 2:
                            error_raised = True
                            error_message = "".join(["Error in comment on page ",
                                                     str(page_number), ":\n",
                                                     "Too many delimiter characters in comment. ",
                                                     "Try removing extra delimiters ( ", self.delimiter,
                                                     " )\n\n"])
                            self.errors.log(error_message)

                        if not error_raised:
                            comment = comment.replace("\r", " ").split(self.delimiter)
                            cmt_date = comment[0]

                            try:
                                cmt_text = comment[1]
                            except IndexError:
                                cmt_text = ""

                            try:
                                provider = comment[2]
                            except IndexError:
                                provider = ""

                            if not self.bookmarks.get(page_number)[0] == "(":
                                citation = self.bookmarks.get(page_number)
                            else:
                                citation = text[0]

                            row = [cmt_date, cmt_text, provider, citation, page_number]

                            self.comments.append(row)

            except KeyError as ke:
                error_message = "Error on page " + str(page_number) + ":\n" \
                    "Unable to parse comment. Do you have the comment formatted correctly? (Date;Comment;Provider)\n" \
                    "ERROR_MSG: " + str(ke) + "\n\n"
                self.errors.log(error_message)
                print("Error on page " + str(page_number))
        return

    def export(self) -> None:
        if len(self.comments) > 0:
            self.__set_dest()
            if self.dest != '':
                write_csv(self.dest, self.headers, self.comments)
                self.errors.to_file(self.dest)
                messagebox.showinfo("Information", "File saved to " + self.dest)
                if len(self.errors) > 0:
                    messagebox.showinfo("Errors", "The following errors occurred:\n\n" + self.errors.to_string() +
                                        "\nErrors are saved to: " + self.errors.get_dest())
            else:
                messagebox.showerror("Error", "File not saved!")
        else:
            messagebox.showwarning("Warning", "No comments found in " + self.src)

# this doesn't work -- causes overflow...figure it out later
#
#    def find_bookmarks_in_pdf(self, pdf) -> dict:
#        result = {}
#        for bookmark in self.outlines:
#            if isinstance(bookmark, list):
#                result.update(self.find_bookmarks_in_pdf(self.pdf))
#            else:
#                try:
#                    result[pdf.getDestinationPageNumber(bookmark) + 1] = bookmark.title
#                except Exception as e:
#                    self.errors.log(
#                        """
#                        A unexpected error occurred while getting the bookmarks from this file.
#                        Please send this PDF to Preston for analysis.\n
#                        """ + str(e))
#        return result


def get_bookmarks(pdf_reader, bookmarks: list, errs: ErrorLog) -> dict:
    """ takes a PDF reader object and list of bookmarks and return a dict of bookmarks """
    result = {}
    for item in bookmarks:
        if isinstance(item, list):
            # recursive call
            result.update(get_bookmarks(pdf_reader, item, errs))
        else:
            try:
                result[pdf_reader.getDestinationPageNumber(item)+1] = item.title
            except Exception as e:
                errs.log(
                    """
                    A unexpected error occurred while getting the bookmarks from this file.
                    Please send this PDF to Preston for analysis.\n
                    """ + str(e))
    return result


#def write_csv(file_name: str, heads: list, rows: list) -> None:
#    """ Take a path, header list, and 2D list of data rows and writes to CSV file"""
#    if path.exists(file_name):
#        remove(file_name)
#
#    with open(file_name, 'w', newline='') as cf:
#        cw = writer(cf, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
#        cw.writerow(heads)
#        [cw.writerow(row) for row in rows]
#    return
#
#
#def get_file_path() -> str:
#    """ Displays open dialog and returns a file path """
#    Tk().withdraw()
#    file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
#    return file_path
#
#
#def get_save_path() -> str:
#    """ Displays save as dialog and return a file path """
#    Tk().withdraw()
#    save_path = asksaveasfilename(filetypes=[("CSV Files", "*.csv")], defaultextension=[("CSV Files", "*.csv")])
#    return save_path

def findWholeWord(w):
    return re.compile(r'\b^({0})$\b'.format(w), flags=re.IGNORECASE).search

def run_keywordscan():
    pdf_path = get_file_path()
    debut = perf_counter()
    scanforkeywords(pdf_path)
    fin = perf_counter()
    print(f"Completed in {fin - debut:0.4f}s")
    return

def run_commentscraper():
    return

def on_enter(e):
    e.widget['background'] = '#ccc'

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

def key_words_menu():

    with open(r".\\config\\keywords", "r") as keyword_file:
        file_content = keyword_file.read()
        keywords = file_content.split('\n')

    win = Tk()
    win.attributes('-alpha', 0.0)
    win.geometry('300x300')
    win.title('Keywords Settings')

    win.columnconfigure(0, weight=1)
    win.columnconfigure(1, weight=1)
    win.rowconfigure(0, weight=1)
    
    listbox = Listbox(win, height=6, selectmode='single', activestyle='none')
    for i, kw in enumerate(keywords):
        listbox.insert(i, kw)

    scrollbar = Scrollbar(win, orient='vertical', command=listbox.yview)
    listbox['yscrollcommand'] = scrollbar.set

    entrybox = Entry(win)
    entrybox.grid(column=0, row=0, sticky=W)

    listbox.grid(column=1,
        row=0,
        sticky='nwes')

    scrollbar.grid(
        column=2,
        row=0,
        sticky='ns')

    doneBtn = Button(win, text='Done', font=('Segoe UI', 12), command=win.destroy)
    doneBtn.bind("<Enter>", on_enter)
    doneBtn.bind("<Leave>", on_leave)
    doneBtn.grid(column=0, row=1)
    center(win)
    win.attributes('-alpha', 1.0)
    win.mainloop()

def main() -> None:

    root = Tk()
    root.attributes('-alpha', 0.0)
    root.geometry('300x300')
    """ menu bar setup """
    menubar = Menu(root, relief='flat')
    filemenu = Menu(menubar, tearoff=0, relief='flat')
    filemenu.add_command(label="Exit", command=root.destroy,)
    menubar.add_cascade(label="File", menu=filemenu)
    
    settingsmenu = Menu(menubar, tearoff=0)
    settingsmenu.add_command(label="Keywords", command=key_words_menu)
    settingsmenu.add_command(label="Context Size")
    menubar.add_cascade(label="Settings", menu=settingsmenu)

    menubar.add_command(label="Help")
    
    root.config(menu=menubar)
    
    """ action buttons setup """
    scanBtn = Button(root, text='Scan PDF For Keywords', font=('Segoe UI', 12), border='0', command=run_keywordscan)
    scanBtn.bind("<Enter>", on_enter)
    scanBtn.bind("<Leave>", on_leave)
    scanBtn.pack(fill='x')
    
    scrapeBtn = Button(root, text='Scrape Comments From PDF', font=('Segoe UI', 12), border='0')
    scrapeBtn.bind("<Enter>", on_enter)
    scrapeBtn.bind("<Leave>", on_leave)
    scrapeBtn.pack(fill='x')
    
    
    # frm = Frame(root, bd=4)
    # frm.pack(fill='x')
    # lab = Label(frm, text='Hello World!', bd=4)
    # lab.pack(ipadx=4, padx=4, ipady=4, pady=4, fill='both')

    statusbar = Label(root, text="v1.0.0", bd=1, relief=SUNKEN, anchor=E)

    statusbar.pack(side=BOTTOM, fill=X)

    root.title('disabilitydude')
    center(root)
    root.attributes('-alpha', 1.0)
    root.mainloop()

    #summary_data = SummaryData()
    #summary_data.set_bookmarks()
    #summary_data.set_comments()
    #summary_data.export()

    #run_keywordscan()
    return


if __name__ == '__main__':
    main()