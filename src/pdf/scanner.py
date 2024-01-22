import re
import sys
from io import StringIO
from datetime import datetime
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

from src.pdf import MedicalRecord, Claimant, Comment, Exhibit, PageDetail


def scan_for_comments(pdf_path):

    comments = []
    with open(pdf_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)

        try:
            outlines = doc.get_outlines()
            index = 1
            provider = ''
            exhibit_data = {index: {'provider': '', 'ref': ''}}
            for (level, title, dest, a, se) in outlines:
                if level == 2:
                    provider = title
                if level == 3:
                    index += 1
                    ref = f'{provider.split(":")[0]}-{title.split()[1]}'
                    exhibit_data[index] = {'provider': provider, 'ref': ref}
        except PDFNoOutlines:
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
                        except UnicodeDecodeError:
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


def scan_pdf_for_summary(pdf_path):

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
    return mr


def parse_client_info(page_text):

    lines = page_text.splitlines()
    lines = [line for line in lines if line]
    client_data = lines[:7]
    client_info = {}
    for e in client_data:
        e = e.split(':')
        client_info[e[0]] = e[1].lstrip()
    return client_info


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
                    'skill_level': '',
                    }
    return work_history


def get_exhibits_from_pdf(doc):
    exhibits = {}
    outlines = doc.get_outlines()
    sys.setrecursionlimit(999999999)
    index = 1
    for (level, title, dest, a, se) in outlines:
        if level == 2:
            id, provider_name, from_date, to_date = parse_title(title)
            ex = Exhibit(provider_name=provider_name, from_date=from_date, to_date=to_date, comments=[])
            exhibits[id] = ex
        if level == 3:
            index += 1
    exhibits = {}

    sys.setrecursionlimit(1000)
    return exhibits


def parse_title(title):
    split_title = title.split(":")
    id = split_title[0]
    provider_name = split_title[1].replace("Doc. Dt.", "").replace("Tmt. Dt.", "").strip()

    # if no dates, return empty
    if len(split_title) == 2:
        provider_name = re.sub(r"\(\d* page.*", "", provider_name).strip()
        return (id, provider_name, "", "")

    provider_dates = re.sub(r"\(\d* page.*", "", split_title[2]).strip().split("-")

    # if one date, return both as date
    if len(provider_dates) == 1:
        date = provider_dates[0]
        return (id, provider_name, date, date)

    from_date = provider_dates[0]
    to_date = provider_dates[1]

    return (id, provider_name, from_date, to_date)


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
                pg = PageDetail(exhibit_id=exhibit_id, exhibit_page=exhibit_page)
                pages[index] = pg
    except PDFNoOutlines:
        sys.setrecursionlimit(1000)
        pages = {}
        print('PDF has no outlines to reference.')

    sys.setrecursionlimit(1000)
    return pages
