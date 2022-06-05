from io import StringIO
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
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox

def search_summary_keywords():
    
    with open(r"keywords.txt", "r") as keyword_file:
        file_content = keyword_file.read()
        keywords = file_content.split('\n') 
    
    fieldnames = ['keyword', 'page', 'text']

    #with open(r"D:\\Downloads\\2835258-amanda_lail-case_file_exhibited_bookmarked-7-08-2021-1625784254 w notes.pdf", 'rb') as in_file:
    with open(r"D:\Downloads\west ex file comp OCR.pdf", 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()

        output = []
        pge = 0
        resultCount = 0

        for page in PDFPage.create_pages(doc):
            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)                
            interpreter.process_page(page)
            pge += 1
            if pge > 100:
                break
            print("processing page [%d]\r"%pge, end="")
            page_text = output_string.getvalue()
            list_text = list(page_text.split(" "))
            list_text = [w.lower() for w in list_text]
            for keyword in keywords:
                #if findWholeWord(keyword)(page_text):
                if keyword in list_text:
                    kw_idx = list_text.index(keyword)
                    if kw_idx > 10:
                        text_sample_list = list_text[kw_idx-10:kw_idx+10]
                    if kw_idx <= 10:
                        text_sample_list = list_text[kw_idx:kw_idx+10]                      
                    text_sample = ' '.join(text_sample_list)
                    pageData = {
                        'keyword': keyword,
                        'page': pge,
                        'text': text_sample
                    }
                        
                    output.append(pageData)
                    resultCount += 1
            output_string.close()
    
    with open(path.join('./','pdfoutput.csv'),'w',encoding='utf-8', newline='') as f:
        csvdw = DictWriter(f, fieldnames=fieldnames)
        csvdw.writeheader()
        csvdw.writerows(output)
        #f.write(str(output))    
    
    print('\nfinds: ' + str(resultCount))
    print('done')
    #print(output_string.getvalue())