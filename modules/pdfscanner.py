import sys
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef
from pdfminer import pdftypes
from dataclasses import dataclass
from typing import Any

@dataclass
class Page:
    number: int
    raw_page: str
    comments: list

@dataclass
class Outline:
    level: int
    title: str
    dest: Any
    a: Any
    se: Any

@dataclass
class PDFData:
    outlines: list[Outline]
    pages: list[Page]

class PDFReader:

    def __init__(self, file_path, parse_page_text=False):
        with open(file_path, 'rb') as in_file:
            sys.setrecursionlimit(2000) 
            self.parser = PDFParser(in_file)
            self.doc = PDFDocument(self.parser)
            self.outlines = self.get_outlines()
            self.pages = self.get_pages()
            sys.setrecursionlimit(1000)

    def read(self):
        pdf_data = PDFData(outlines=self.outlines, pages=self.pages)
        return pdf_data

    def get_outlines(self):     
        outlines = []
        raw_outlines = self.doc.get_outlines()
        for (level, title, dest, a, se) in raw_outlines:
            outline = Outline(level=level, title=title, dest=dest, a=a, se=se)
            outlines.append(outline)
        return outlines

    def get_pages(self):
        pages = []
        for page_number, page in enumerate(PDFPage.create_pages(self.doc), start=1):
            if page.annots:
                page_comments = self.parse_page_comments(page)
            else:
                page_comments = []
            page = Page(number=page_number, raw_page=page, comments=page_comments)
            pages.append(page)
        return pages

    def parse_page_comments(self, page):
        page_comments = []
        for annot in pdftypes.resolve1(page.annots):
            por = PDFObjRef.resolve(annot)
            if 'Contents' in por.keys():
                try:
                    text = por['Contents'].decode('utf-8', 'ignore')
                except UnicodeDecodeError as e:
                    text = por['Contents']
                page_comments.append(text)
        return page_comments

def parse_page_text(raw_page):
    if type(raw_page) == PDFPage:
        rsrcmgr = PDFResourceManager()
        output_string = StringIO()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(raw_page)            
        page_text = output_string.getvalue()
        output_string.flush()
        page_text = page_text.replace('\x0c', '').replace('\n', '')
    else: page_text = raw_page
    return page_text

def main():
    file_path = r'.\\files\\2909274-cecilia_phillips-case_file_exhibited_bookmarked-8-10-2022- w notes.pdf'
    #file_path = r'./tests/fakes/fake-pdf.pdf'
    pdf_reader = PDFReader(file_path)
    pdf_data = pdf_reader.read()
    print(pdf_data.pages[0].raw_page)

if __name__ == '__main__':
    main()