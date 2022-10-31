from modules.pdfscanner import *

file_path = r'./tests/fakes/fake-pdf.pdf'

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

def test_PDFReader():
    pdf_reader = PDFReader(file_path)
    pdf_data = pdf_reader.read()
    print(pdf_data.outlines)
    assert(len(pdf_data.outlines)) > 0
    assert(pdf_data.pages[0].text) == 'Hello world'
    assert(pdf_data.pages[0].comments[0]) == 'hello from comment' 

