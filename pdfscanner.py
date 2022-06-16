from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef

from datetime import datetime

def parse_comment(comment):
    comment = comment.split(";")
    date = datetime.strptime(comment[0], '%m/%d/%Y')
    text = comment[1].replace("\r", " ")
    provider = comment[2]
    data = {
        'date': date,
        'text': text,
        'provider': provider
    }
    return data

def scan_for_exhibit_data(pdf_path):
    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        try:
            outlines = doc.get_outlines()
            index = 1
            provider = ''
            exhibit_data = {index: {'provider': '','ref': ''}}
            for (level, title, dest, a, se) in outlines:
                if level == 2:
                    provider = title
                if level == 3:
                    index += 1
                    exhibit_data[index] = {'provider': provider,'ref': title}
        except PDFNoOutlines as e:
            exhibit_data = {}
            print('PDF has no outlines to reference.')
    return exhibit_data

def scan_for_client_info(pdf_path):
    
    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc)):
            if pagenumber > 0:
                break
            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)                                                    
            interpreter.process_page(page)            
            page_text = output_string.getvalue()
            lines = page_text.splitlines()
            lines = [line for line in lines if line]
            client_data = lines[:6]
            client = {}
            for e in client_data:
                e = e.split(':')
                client[e[0]] = e[1].lstrip()
            return client

def scan_for_comments(pdf_path):

    comments = []
    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)

        try:
            outlines = doc.get_outlines()
            index = 1
            provider = ''
            exhibit_data = {index: {'provider': '','ref': ''}}
            for (level, title, dest, a, se) in outlines:
                if level == 2:
                    provider = title
                if level == 3:
                    index += 1
                    ref = f'{provider.split(":")[0]}-{title.split()[1]}'
                    exhibit_data[index] = {'provider': provider,'ref': ref}
        except PDFNoOutlines as e:
            exhibit_data = {}
            print('PDF has no outlines to reference.')
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc), start=1):
            if page.annots:
                for annot in page.annots:
                    por = PDFObjRef.resolve(annot)
                    if 'Contents' in por.keys():
                        try:
                            text = por['Contents'].decode('utf-8', 'ignore')
                        except UnicodeDecodeError as e:
                            text = por['Contents']
                            print(por['Contents'])
                        comment = parse_comment(text)
                        data = {
                            'page': pagenumber,
                            'date': comment['date'], 
                            'text': comment['text'],
                            'provider': comment['provider'],
                            'pagehead': exhibit_data[pagenumber]['provider'],
                            'ref': exhibit_data[pagenumber]['ref']
                        }
                        comments.append(data)
    
    comments = sorted(comments, key=lambda el: el['date'])
    return comments                      

def scan_for_date_of_birth(pdf_path = "C:\\Users\\Owner\\Downloads\\2846269-richard_herrera-case_file_exhibited_bookmarked-6-07-2022-1654613771 (1).pdf"):
    
    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc)):
            if pagenumber < 2:
                continue
            elif pagenumber > 2:
                break

            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)                                                    
            interpreter.process_page(page)            
            page_text = output_string.getvalue()
            print(page_text)
            #lines = page_text.splitlines()
            #print(lines)

def scan_for_keywords(pdf_path, app):
    
    with open(r".\\config\\keywords\\default", "r") as keyword_file:
        file_content = keyword_file.read()
        keywords = file_content.split('\n') 
        keywords = [w for w in keywords if w]
    
    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        try:
            outlines = doc.get_outlines()
            index = 1
            provider = ''
            page_metadata = {index: {'provider': '','exhibit_page': ''}}
            for (level, title, dest, a, se) in outlines:
                if level == 2:
                    provider = title
                if level == 3:
                    index += 1
                    page_metadata[index] = {'provider': provider,'exhibit_page': title}
        except PDFNoOutlines as e:
            page_metadata = {}
            print('PDF has no outlines to reference.') 
                

        rsrcmgr = PDFResourceManager()

        output = []
        pge = 0
        resultCount = 0

        for page in PDFPage.create_pages(doc):
            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            if page.label:
                exhibit = page.label
            else:
                exhibit = ""
            
            #if page.attrs:
                #print(page.attrs)
                #print(PDFStream.decode(page.contents))
                #for x in page.attrs:
                    #por = PDFObjRef.resolve(x['Contents'])
                    #print(por)
                    #aid = por['T'].decode("utf-8")
                                     
            interpreter.process_page(page)
            pge += 1
            
            if pge > 3:
                break
            print(" [%d]\r"%pge, end="")
            app.status_bar.set_status(f'Processing page {pge}...')
            app.update()
            page_text = output_string.getvalue()
            list_text = list(page_text.split(" "))
            list_text = [w.lower() for w in list_text]
            for keyword in keywords:
                if keyword in list_text:
                    kw_idx = list_text.index(keyword)
                    if kw_idx > 10:
                        text_sample_list = list_text[kw_idx-10:kw_idx+10]
                    if kw_idx <= 10:
                        text_sample_list = list_text[kw_idx:kw_idx+10]
                                          
                    text_sample = ' '.join(text_sample_list).replace('\n', '_')
                    try:
                        provider = page_metadata[pge]['provider']
                        exhibit_page = page_metadata[pge]['exhibit_page']
                    except KeyError as e:
                        provider = ''
                        exhibit_page = ''
                    
                    pageData = {
                        'keyword': keyword,
                        'page': pge,
                        'text': text_sample,
                        'exhibit': exhibit,
                        'provider': provider,
                        'exhibit_page': exhibit_page
                    }
                        
                    output.append(pageData)
                    resultCount += 1
            output_string.close()
            
    app.set_status(f'Done. Pages Scanned: {pge} - Keyword Results: {resultCount}')
    app.update()
    print('\nfinds: ' + str(resultCount))
    print('done')
    return output


def scan_pdf_for_summary(pdf_path):
    return

def main():
    return

if __name__ == '__main__':
    main()