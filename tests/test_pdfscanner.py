from pdfscanner import *

file_path = r'./tests/fakes/fake-pdf.pdf'

def test_Page_should_store_page_number_and_comments():
    page = Page(number=1, raw_page='fake', comments=['comment 1', 'comment 2'])
    assert(page.number) == 1
    assert(page.comments) == ['comment 1', 'comment 2']

def test_PDFData_should_store_outlines_and_pages():
    page_1 = Page(number=1, raw_page='fake', comments=['comment 1', 'comment 2'])
    page_2 = Page(number=2, raw_page='fake 2', comments=['comment 3', 'comment 4'])
    pdfData = PDFData(outlines=['outline 1', 'outline 2'], pages=[page_1,page_2])
    assert(pdfData.outlines) == ['outline 1', 'outline 2']
    assert(pdfData.pages) == [page_1,page_2]

def test_PDFReader_should_read_a_pdf():
    with open(file_path, 'rb') as file_obj:
        pdf_reader = PDFReader(file_obj)
        pdf_data = pdf_reader.read()
        assert(len(pdf_data.outlines)) > 0
        assert(pdf_data.pages[0].comments[0]) == 'hello from comment'
        assert(pdf_data.pages[0].comments[1]) == 'hello from comment 2' 
        assert(pdf_data.pages[1].comments[0]) == 'page 2 comment'
    

