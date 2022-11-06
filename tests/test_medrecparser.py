from modules.medrecparser import *
from modules.pdfscanner import PDFData, Outline, Page

fake_outlines = [
    Outline(
        level=2,
        title='1F: Hospital Records - ACME HEALTH Tmt. Dt.: 1/1/2000-1/30/2000 (100 pages)',
        dest=None,
        a=None,
        se=None
    ),
    Outline(
        level=3,
        title='(page 1 of 2)',
        dest=None,
        a=None,
        se=None
    )
]


fake_pages = [
    Page(
        number=1,
        raw_page='Claimant: John Q Public\nSSN: 123-45-6789\nClaim Type: T2\nLast Change: 01/01/2021\nApplication: 01/02/2021\nAlleged Onset: 01/03/2021\nLast Insured: 01/31/2021',
        comments=["5/1/2022; here's a comment"]
    ),
    Page(
        number=2,
        raw_page='DATE OF BIRTH: 09/01/1970',
        comments=[]
    )
]

fake_pdf_data = PDFData(fake_outlines, fake_pages)

def test_MedicalRecordClass():
    mr = MedicalRecord(fake_pdf_data)

def test_MedicalRecord_exhibits():
    mr = MedicalRecord(fake_pdf_data)
    assert(mr.exhibits['1F'].provider_name) == 'Hospital Records - ACME HEALTH'
    assert(mr.exhibits['1F'].from_date) == '1/1/2000'
    assert(mr.exhibits['1F'].to_date) == '1/30/2000'
    assert(len(mr.exhibits['1F'].comments)) > 0

def test_MedicalRecord_claimant():
    mr = MedicalRecord(fake_pdf_data)
    assert(mr.claimant.name) == 'John Q Public'
    assert(mr.claimant.ssn) == '123-45-6789'
    assert(mr.claimant.claim) == 'T2'
    assert(mr.claimant.onset_date) == '01/03/2021'
    assert(mr.claimant.pdof) == datetime.strptime('01/02/2021', '%m/%d/%Y')
    assert(mr.claimant.last_insured_date) == '01/31/2021'
    assert(mr.claimant.birthdate) == '09/01/1970'
    assert(mr.claimant.age()) >= 52
    assert(mr.claimant.age_at_onset()) == 50

def test_MedicalRecord_comments():
    mr = MedicalRecord(fake_pdf_data)
    expected_comment = Comment(date='5/1/2022', text=' here\'s a comment', page=1, exhibit_page=1)
    assert(mr.exhibits['1F'].comments[0]) == expected_comment
