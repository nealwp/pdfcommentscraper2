from pdfscanner import *

file_path = r'.\\files\\2909274-cecilia_phillips-case_file_exhibited_bookmarked-8-10-2022- w notes.pdf'

def test_read_medical_record():
    medical_record = MedicalRecord(file_path)
    assert(medical_record)

def test_get_exhibits_from_medical_record():
    medical_record = MedicalRecord(file_path)
    exhibits = medical_record.exhibits