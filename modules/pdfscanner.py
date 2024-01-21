from pydoc import pager
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

from datetime import date, datetime
from dataclasses import dataclass
from typing import List

class MedicalRecord2:
    
    def __init__(self, file_path):
        self.exhibits = {}
        with open(file_path, 'rb') as in_file: 
            self.parser = PDFParser(in_file)
            self.doc = PDFDocument(self.parser)
            self.rsrcmgr = PDFResourceManager()
            self.output_string = StringIO()
            self.device = TextConverter(self.rsrcmgr, self.output_string, laparams=LAParams())
            self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
            self.set_exhibits()

    def set_exhibits(self):
        self.outlines = self.doc.get_outlines()
        index = 1
        provider = ''
        sys.setrecursionlimit(2000)
        for (level, title, dest, a, se) in self.outlines:
            if level == 2:              
                provider = title
                id = provider.split(":")[0]
                provider_name = provider.split(":")[1].replace("Doc. Dt.","").replace("Tmt. Dt.", "").strip()
                provider_dates = re.sub(r"\(\d* page.*", "", provider.split(":")[2]).strip()
                from_date = provider_dates.split("-")[0]
                try:
                    to_date = provider_dates.split("-")[1]
                except IndexError as e:
                    to_date = from_date
                
                ex = Exhibit(provider_name=provider_name, from_date=from_date, to_date=to_date, comments=[])
                self.exhibits[id] = ex
            if level == 3:
                index += 1

@dataclass
class Claimant:
    '''individual the medical record pertains to'''
    name: str = None
    ssn: str = None
    birthdate: datetime = None
    education_years: int = None
    onset_date: datetime = None
    pdof: datetime = None
    claim: str = None
    last_insured_date: datetime = None
    work_history: list = None # TODO: need own class
    dds_rfc: dict = None #TODO: need own class
    claimed_mdsi: list = None #TODO: need own class

    def age(self) -> int:
        if self.birthdate:
            today = date.today()
            birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        else:
            return None

    def age_at_onset(self) -> int:
        if self.birthdate and self.onset_date:
            birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
            onset_date = datetime.strptime(self.onset_date, '%m/%d/%Y')
            return onset_date.year - birthdate.year - ((onset_date.month, onset_date.day) < (birthdate.month, birthdate.day))
        else: 
            return None

@dataclass
class Exhibit:
    '''a section of the medical record'''
    provider_name: str
    from_date: str
    to_date: str
    comments: list

@dataclass
class PageDetail:
    '''detail for a page'''
    exhibit_id: str
    exhibit_page: int

@dataclass
class Comment:
    '''annotations made to the medical record by the reviewer'''
    date: datetime
    text: str
    page: int
    exhibit_page: int

@dataclass
class MedicalRecord:
    '''a social security pdf medical record'''
    claimant: Claimant
    exhibits: dict
    pages: dict

    def comment_count(self):
        count = 0
        for exhibit in self.exhibits.keys():
            count += len(self.exhibits[exhibit].comments)
        return count

def parse_comment(comment):
    comment = comment.split(";")
    date = comment[0]
    text = comment[1].replace("\r", " ")
    try:
        provider = comment[2]
    except IndexError:
        provider = ""
    data = {
        'date': date,
        'text': text,
        'provider': provider
    }
    return data

def get_exhibits_from_pdf(doc):
    try:
        outlines = doc.get_outlines()
        sys.setrecursionlimit(999999999)
        index = 1
        provider = ''
        exhibits = {}
        for (level, title, dest, a, se) in outlines:
            if level == 2:              
                provider = title
                id = provider.split(":")[0]
                provider_name = provider.split(":")[1].replace("Doc. Dt.","").replace("Tmt. Dt.", "").strip()
                provider_dates = re.sub(r"\(\d* page.*", "", provider.split(":")[2]).strip()
                from_date = provider_dates.split("-")[0]
                try:
                    to_date = provider_dates.split("-")[1]
                except IndexError as e:
                    to_date = from_date
                
                ex = Exhibit(provider_name=provider_name, from_date=from_date, to_date=to_date, comments=[])
                exhibits[id] = ex
            if level == 3:
                index += 1
            
    except PDFNoOutlines as e:
        exhibits = {}
        sys.setrecursionlimit(1000)
        print('PDF has no outlines to reference.')

    sys.setrecursionlimit(1000)
    return exhibits

def get_page_details_from_pdf(doc):
    try:
        outlines = doc.get_outlines()
        index = 1
        provider = ''
        pages = {}
        sys.setrecursionlimit(2000)
        for (level, title, dest, a, se) in outlines:
            if level == 2:              
                provider = title
            if level == 3:
                index += 1
                exhibit_id = provider.split(":")[0]
                exhibit_page = int(title.split()[1])
                pg = PageDetail(exhibit_id=exhibit_id,exhibit_page=exhibit_page)           
                pages[index] = pg
    except PDFNoOutlines as e:
        sys.setrecursionlimit(1000)
        pages = {}
        print('PDF has no outlines to reference.')

    sys.setrecursionlimit(1000)
    return pages

def parse_client_info(page_text):

    lines = page_text.splitlines()
    lines = [line for line in lines if line]
    client_data = lines[:7]
    client_info = {}
    for e in client_data:
        e = e.split(':')
        client_info[e[0]] = e[1].lstrip()
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
    
    comments = sorted(comments, key=lambda el: el['ref'])
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

    mr = MedicalRecord(claimant=None, exhibits={}, pages={})  

    with open(pdf_path, 'rb') as in_file: 
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        output_string = StringIO()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        mr.exhibits = get_exhibits_from_pdf(doc)
        mr.pages = get_page_details_from_pdf(doc)             
        mr.claimant = Claimant(work_history=[])

        for pagenumber, page in enumerate(PDFPage.create_pages(doc), start=1):
            interpreter.process_page(page)            
            page_text = output_string.getvalue() 
            if pagenumber == 1:
                client_info = parse_client_info(page_text)
                mr.claimant.name = client_info['Claimant']
                mr.claimant.ssn = client_info['SSN']
                mr.claimant.onset_date = client_info['Alleged Onset']
                mr.claimant.claim = client_info['Claim Type']
                mr.claimant.pdof = datetime.strptime(client_info['Application'], '%m/%d/%Y')
                mr.claimant.last_insured_date = client_info['Last Insured']
                mr.claimant.birthdate = None
            if not mr.claimant.birthdate:
                mr.claimant.birthdate = parse_client_date_of_birth(page_text)
                if mr.claimant.birthdate:
                    break

            if len(mr.claimant.work_history) == 0:
                mr.claimant.work_history = parse_work_history(page_text)
            #parse_ability_ratings(page_text)
        
        for pagenumber, page in enumerate(PDFPage.create_pages(doc), start=1):
            if page.annots:
                page_comments = parse_page_comments(page.annots)
                if len(page_comments) > 0:
                    exhibit_id = mr.pages[pagenumber].exhibit_id
                    exhibit_page = mr.pages[pagenumber].exhibit_page
                    for comment in page_comments:
                        date = comment['date']
                        text = comment['text']
                        cm = Comment(date=date, text=text, page=pagenumber, exhibit_page=exhibit_page)
                        mr.exhibits[exhibit_id].comments.append(cm)
        checkpoint = perf_counter()
        print(f'comment scan done in {checkpoint - start:0.2f}s')   
    finish = perf_counter()
    print(f'summary scan complete in {finish - start:0.2f}s')
    return mr



def main():
    file_path = r'.\\files\\2909274-cecilia_phillips-case_file_exhibited_bookmarked-8-10-2022- w notes.pdf'
    scan_pdf_for_summary(file_path)

if __name__ == '__main__':
    main()
