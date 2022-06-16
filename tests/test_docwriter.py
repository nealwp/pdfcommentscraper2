import sys
import docx.document
sys.path.append('../')

import pdfcommentscraper2.docwriter as docwriter

def test_generate_medical_summary():
    """ Should return an obj of type docx """
    empty_data = {
            'client_name': '',
            'client_ssn': '',
            'title': '',
            'application_date': '',
            'onset_date': '',
            'insured_date': '',
            'prior_applications': '',
            'birthdate': '',
            'education': '',
            'work_history': '',
            'drug_use': '',
            'criminal_history': '',
            'overview': '',
            'comments': ''
        }
    
    assert type(docwriter.generate_medical_summary(empty_data)) == docx.document.Document
