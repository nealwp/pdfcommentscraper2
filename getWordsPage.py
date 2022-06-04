#GetPageNumber.py
# -*- coding: utf-8 -*-

#import libs
import os
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

#parse pdf
def parsePDFtoTXT(pdf_path):
    fp = open(pdf_path, 'rb')
    parser = PDFParser(fp)  
    document= PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        rsrcmgr=PDFResourceManager()
        laparams=LAParams()
        device=PDFPageAggregator(rsrcmgr,laparams=laparams)
        interpreter=PDFPageInterpreter(rsrcmgr,device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout=device.get_result()
            # print(layout)
            output=str(layout)
            for x in layout:
                if (isinstance(x,LTTextBoxHorizontal)):
                    text=x.get_text()
                    print(text)
                    output+=text
                    output=re.sub('\s','',output)
            with open(os.path.join(base_dir,'pdfoutput.txt'),'a',encoding='utf-8') as f:
                f.write(output)

#get page
def get_word_page(word_list):
    f=open(os.path.join(base_dir,'pdfoutput.txt'),encoding='utf-8')
    text_list=f.read().split('<LTPage')
    f.close()
    n=len(text_list)
    for w in word_list:
        page_list=[]
        for i in range(1,n):
            if w in text_list[i]:
                page_list.append(i)
        with open(os.path.join(base_dir,'result.txt'),'a',encoding='utf-8') as f:
                f.write(w+str(page_list)+'\n')

if __name__=='__main__':
    base_dir = 'D:\\Downloads\\'   #pdf file directory    
    parsePDFtoTXT(os.path.join(base_dir,'2835258-amanda_lail-case_file_exhibited_bookmarked-7-08-2021-1625784254 w notes.pdf'))
    fl=open(os.path.join(base_dir,'list.txt'),encoding='utf-8-sig')
    word_list = list(fl)
    word_list = [x.strip() for x in word_list]
    print(word_list)
    fl.close()
    get_word_page(word_list)