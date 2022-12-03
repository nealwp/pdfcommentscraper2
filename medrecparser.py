import re
from datetime import date, datetime
from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List
from components.workhistory import WorkHistory
from pdfscanner import PDFData, parse_page_text


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
class Exhibit:
    '''a section of the medical record'''
    provider_name: str
    from_date: str
    to_date: str
    comments: list

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
    work_history: WorkHistory = WorkHistory()
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

class MedicalRecord:
    
    def __init__(self, pdf_data: PDFData):
        self.pdf_data = pdf_data
        self.exhibits: Dict[Exhibit] = {}
        self.claimant: Claimant = Claimant()
        self.page_details: Dict[PageDetail] = {}
        
        self.set_exhibits()
        self.set_claimant()
        self.set_comments()

    def set_exhibits(self):
        index = 1
        provider = ''
        for outline in self.pdf_data.outlines:
            if outline.level == 2:              
                provider = outline.title
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
            if outline.level == 3:
                exhibit_id = provider.split(":")[0]
                exhibit_page = int(outline.title.split()[1])
                page_detail = PageDetail(exhibit_id=exhibit_id,exhibit_page=exhibit_page)           
                self.page_details[index] = page_detail
                index += 1
    
    def set_claimant(self):       
        page_text = parse_page_text(self.pdf_data.pages[0].raw_page, clean=False)
        client_info = self.parse_client_info(page_text)
        self.claimant.name = client_info['Claimant']
        self.claimant.ssn = client_info['SSN']
        self.claimant.onset_date = client_info['Alleged Onset']
        self.claimant.claim = client_info['Claim Type']
        self.claimant.pdof = datetime.strptime(client_info['Application'], '%m/%d/%Y')
        self.claimant.last_insured_date = client_info['Last Insured']
                
        self.claimant.birthdate = self.find_client_date_of_birth()

        #self.claimant.work_history #TODO: parse work history
        #if len(mr.claimant.work_history) == 0:
        #    mr.claimant.work_history = parse_work_history(page_text)
        #parse_ability_ratings(page_text)
        # 

    def parse_client_info(self, page_text):
        lines = page_text.splitlines()
        lines = [line for line in lines if line]
        client_data = lines[:7]
        client_info = {}
        for e in client_data:
            e = e.split(':')
            client_info[e[0]] = e[1].lstrip()
        return client_info

    def find_client_date_of_birth(self):
        for page in self.pdf_data.pages:
            page_text = parse_page_text(page.raw_page)
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
            if date_of_birth:
                break
        return date_of_birth

    def set_comments(self):
        for index, page in enumerate(self.pdf_data.pages, start=1):
            print("Scanning page [%d] for comments...\r"%index, end="")
            if len(page.comments) > 0:
                exhibit_id = self.page_details[index].exhibit_id
                exhibit_page = self.page_details[index].exhibit_page
                for comment in page.comments:
                    comment = parse_comment(comment)
                    date = comment['date']
                    text = comment['text']
                    cm = Comment(date=date, text=text, page=index, exhibit_page=exhibit_page)
                    self.exhibits[exhibit_id].comments.append(cm)

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

#def scan_for_keywords(pdf_path, app):
#    
#    with open(r".\\config\\keywords\\default", "r") as keyword_file:
#        file_content = keyword_file.read()
#        keywords = file_content.split('\n') 
#        keywords = [w for w in keywords if w]
#    
#    with open(pdf_path, 'rb') as in_file: 
#        parser = PDFParser(in_file)
#        doc = PDFDocument(parser)
#        try:
#            outlines = doc.get_outlines()
#            sys.setrecursionlimit(2000)
#            index = 1
#            provider = ''
#            page_metadata = {index: {'provider': '','exhibit_page': ''}}
#            for (level, title, dest, a, se) in outlines:
#                if level == 2:
#                    provider = title
#                if level == 3:
#                    index += 1
#                    page_metadata[index] = {'provider': provider,'exhibit_page': title}
#        except PDFNoOutlines as e:
#            page_metadata = {}
#            print('PDF has no outlines to reference.') 
#                
#
#        rsrcmgr = PDFResourceManager()
#
#        output = []
#        pge = 0
#        resultCount = 0
#
#        for page in PDFPage.create_pages(doc):
#            output_string = StringIO()
#            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#            interpreter = PDFPageInterpreter(rsrcmgr, device)
#            if page.label:
#                exhibit = page.label
#            else:
#                exhibit = ""
#            
#            #if page.attrs:
#                #print(page.attrs)
#                #print(PDFStream.decode(page.contents))
#                #for x in page.attrs:
#                    #por = PDFObjRef.resolve(x['Contents'])
#                    #print(por)
#                    #aid = por['T'].decode("utf-8")
#                                     
#            interpreter.process_page(page)
#            pge += 1
#            
#            #if pge > 3:
#            #    break
#            print(" [%d]\r"%pge, end="")
#            app.status_bar._set_status(f'Processing page {pge}...')
#            app.update()
#            page_text = output_string.getvalue()
#            list_text = list(page_text.split(" "))
#            list_text = [w.lower() for w in list_text]
#            for keyword in keywords:
#                if keyword in list_text:
#                    kw_idx = list_text.index(keyword)
#                    if kw_idx > 10:
#                        text_sample_list = list_text[kw_idx-10:kw_idx+10]
#                    if kw_idx <= 10:
#                        text_sample_list = list_text[kw_idx:kw_idx+10]
#                                          
#                    text_sample = ' '.join(text_sample_list).replace('\n', '_')
#                    try:
#                        provider = page_metadata[pge]['provider']
#                        exhibit_page = page_metadata[pge]['exhibit_page']
#                    except KeyError as e:
#                        provider = ''
#                        exhibit_page = ''
#                    
#                    pageData = {
#                        'keyword': keyword,
#                        'page': pge,
#                        'text': text_sample,
#                        'exhibit': exhibit,
#                        'provider': provider,
#                        'exhibit_page': exhibit_page
#                    }
#                        
#                    output.append(pageData)
#                    resultCount += 1
#            output_string.close()
#            
#    app.status_bar._set_status(f'Done. Pages Scanned: {pge} - Keyword Results: {resultCount}')
#    app.update()
#    print('\nfinds: ' + str(resultCount))
#    print('done')
#    sys.setrecursionlimit(1000)
#    return output
#
