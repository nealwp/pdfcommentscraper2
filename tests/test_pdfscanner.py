from modules.pdfscanner import *

file_path = r'.\\tests\\fakes\\fake-medical-record.pdf'

def test_page_dataclass():
    page = Page(number=1, text='test text', comments=['comment 1', 'comment 2'])
    assert(page.number) == 1
    assert(page.text) == 'test text'
    assert(page.comments) == ['comment 1', 'comment 2']

def test_read_medical_record():
    medical_record = MedicalRecord(file_path)
    assert(medical_record)

def test_get_exhibits_from_medical_record():
    medical_record = MedicalRecord(file_path)
    exhibits = medical_record.exhibits