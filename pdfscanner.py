import sys
import re
from io import StringIO
from time import perf_counter

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef
from pdfminer.high_level import extract_text_to_fp

from datetime import datetime

def parse_comment(comment):
    comment = comment.split(";")
    try:
        date = datetime.strptime(comment[0], '%m/%d/%Y')
    except ValueError as e:
        date = datetime.strptime(comment[0], '%m/%d/%y')
    text = comment[1].replace("\r", " ")
    provider = comment[2]
    data = {
        'date': date,
        'text': text,
        'provider': provider
    }
    return data

def parse_exhibit_data(doc):
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

    return exhibit_data

def parse_client_info(page_text):

    start = perf_counter()    
    lines = page_text.splitlines()
    lines = [line for line in lines if line]
    client_data = lines[:7]
    client_info = {}
    for e in client_data:
        e = e.split(':')
        client_info[e[0]] = e[1].lstrip()
    finish = perf_counter()
    
    print(f'client info done in {finish - start:0.2f}s')
    return client_info

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
                annotations = list(page.annots)
                for annot in annotations:
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


def parse_page_comments(annots):

    page_comments = []
    for annot in annots:
        por = PDFObjRef.resolve(annot)
        if 'Contents' in por.keys():
            text = por['Contents'].decode('utf-8', 'ignore')
            comment = parse_comment(text)
            page_comments.append(comment)

    return page_comments

def parse_client_date_of_birth(page_text):

    date_of_birth = None
    pattern = re.compile(r'date of birth: \d{1,2}\/\d{1,2}\/\d{4}', re.IGNORECASE)
    lines = page_text.splitlines()
    for line in lines:
        if 'date of birth: ' in line.lower():
            matchObj = re.search(pattern, page_text)
            if matchObj:
                dob = matchObj.group(0)
                date_of_birth = dob.split(": ")[1]
                break

    return date_of_birth

def parse_work_history(page_text):
    work_history = []
    pattern = re.compile(r'job title: \w+ \w+\b(?<!start)|job title: \w+\b(?<!start)', re.IGNORECASE)
    lines = page_text.splitlines()
    for line in lines:
        if 'job title:' in line.lower():
            work_history = re.findall(pattern, page_text)
            for i, e in enumerate(work_history):
                work_history[i] = {
                    'job_title': e.split(": ")[1],
                    'intensity': '',
                    'skill_level': '' 
                    }
            print(work_history)
    return work_history

def parse_ability_ratings(page_text):
    ability_ratings = {}
    occ_lift_carry_pattern = re.compile(r'occasionally \(occasionally is cumulatively 1\/3 or less of an 8 hour day\) lift and\/or carry \(including upward pulling\):.*', re.IGNORECASE)
    lines = page_text.splitlines()
    for line in lines:
        occ_lift_carry = re.search(occ_lift_carry_pattern, line)
        if occ_lift_carry:
            print(occ_lift_carry.group(0))
            break

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
            sys.setrecursionlimit(2000)
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
            
            #if pge > 3:
            #    break
            print(" [%d]\r"%pge, end="")
            app.status_bar._set_status(f'Processing page {pge}...')
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
            
    app.status_bar._set_status(f'Done. Pages Scanned: {pge} - Keyword Results: {resultCount}')
    app.update()
    print('\nfinds: ' + str(resultCount))
    print('done')
    sys.setrecursionlimit(1000)
    return output


def scan_pdf_for_summary(pdf_path):

    start = perf_counter()  
    summary_data = {}
    comments = []
    work_history = []

    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        output_string = StringIO()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        exhibit_data = parse_exhibit_data(doc)
        checkpoint = perf_counter()
        print(f'exhibit data done in {checkpoint - start:0.2f}s')
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc), start=1):
            interpreter.process_page(page)            
            page_text = output_string.getvalue() 
            if pagenumber == 1:
                client_info = parse_client_info(page_text)
                checkpoint = perf_counter()
                print(f'client data done in {checkpoint - start:0.2f}s')
                client_info['Date of Birth'] = None
            if not client_info['Date of Birth']:
                client_info['Date of Birth'] = parse_client_date_of_birth(page_text)
                if client_info['Date of Birth']:
                    checkpoint = perf_counter()
                    print(f'dob done in {checkpoint - start:0.2f}s')
                    break
            if len(work_history) == 0:
                work_history = parse_work_history(page_text)
            parse_ability_ratings(page_text)
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc), start=1):
            if page.annots:
                page_comments = parse_page_comments(page.annots)
                if len(page_comments) > 0:
                    for comment in page_comments:
                        data = {
                            'page': pagenumber,
                            'date': comment['date'], 
                            'text': comment['text'],
                            'provider': comment['provider'],
                            'pagehead': exhibit_data[pagenumber]['provider'],
                            'ref': exhibit_data[pagenumber]['ref']
                        }
                        comments.append(data)
        checkpoint = perf_counter()
        print(f'comment scan done in {checkpoint - start:0.2f}s')

        comments = sorted(comments, key=lambda el: el['date'])
        checkpoint = perf_counter()
        print(f'sort done in {checkpoint - start:0.2f}s')

        summary_data['client'] = client_info
        summary_data['comments'] = comments
        summary_data['exhibits'] = exhibit_data
        summary_data['work_history'] = work_history

    finish = perf_counter()
    print(f'summary scan complete in {finish - start:0.2f}s')
    return summary_data

def main():
    return

if __name__ == '__main__':
    main()