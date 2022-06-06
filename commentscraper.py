from time import perf_counter
from PyPDF2 import PdfFileReader
from PyPDF2.generic import ByteStringObject

from os import path
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox

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


def scrape_comments():
    summary_data = SummaryData()
    summary_data.set_bookmarks()
    summary_data.set_comments()
    summary_data.export()
    return