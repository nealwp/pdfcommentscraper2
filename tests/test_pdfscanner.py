from modules.pdfscanner import *

file_path = r'.\\tests\\fakes\\fake-medical-record.pdf'

def test_Page_dataclass():
    page = Page(number=1, text='test text', comments=['comment 1', 'comment 2'])
    assert(page.number) == 1
    assert(page.text) == 'test text'
    assert(page.comments) == ['comment 1', 'comment 2']

def test_PDFData_dataclass():
    page_1 = Page(number=1, text='test text', comments=['comment 1', 'comment 2'])
    page_2 = Page(number=2, text='test text 2', comments=['comment 3', 'comment 4'])
    pdfData = PDFData(outlines=['outline 1', 'outline 2'], pages=[page_1,page_2])
    assert(pdfData.outlines) == ['outline 1', 'outline 2']
    assert(pdfData.pages) == [page_1,page_2]
 

def test_read_medical_record():
    medical_record = MedicalRecord(file_path)
    assert(medical_record)

def test_get_exhibits_from_medical_record():
    medical_record = MedicalRecord(file_path)
    exhibits = medical_record.exhibits