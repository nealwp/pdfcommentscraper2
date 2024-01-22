import sys
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


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
            page_metadata = {index: {'provider': '', 'exhibit_page': ''}}
            for (level, title, dest, a, se) in outlines:
                if level == 2:
                    provider = title
                if level == 3:
                    index += 1
                    page_metadata[index] = {'provider': provider, 'exhibit_page': title}
        except PDFNoOutlines:
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

            interpreter.process_page(page)
            pge += 1
            print(" [%d]\r" % pge, end="")
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
                    except KeyError:
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

    app.status_bar.set_status(f'Done. Pages Scanned: {pge} - Keyword Results: {resultCount}')
    app.update()
    print('\nfinds: ' + str(resultCount))
    print('done')
    sys.setrecursionlimit(1000)
    return output
