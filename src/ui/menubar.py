from tkinter import Menu
from csv import DictWriter
from time import perf_counter

from src.helpers import get_file_path, get_save_path
from src.pdf.scanner import scan_for_comments
from src.modules.pdfscanner import scan_for_keywords
from src.ui.summaryform import SummaryForm
from src.ui.keywordsettingsform import KeywordSettingsForm
from src.ui.contextsizeform import ContextSizeForm


class MenuBar(Menu):
    def __init__(self, parent) -> None:
        super().__init__(parent, bd=5)
        self.parent = parent

        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label='New Summary', command=self._new_summary_form)
        self.filemenu.add_command(label="Exit", command=self.parent.destroy)
        self.add_cascade(label="File", menu=self.filemenu)

        self.actions_menu = Menu(self, tearoff=0)
        self.actions_menu.add_command(label="Scan PDF for Keywords", command=self._run_keyword_scan)
        self.actions_menu.add_command(label="Scrape Comments from PDF", command=self._run_comment_scrape)
        self.add_cascade(label="Actions", menu=self.actions_menu)

        self.settingsmenu = Menu(self, tearoff=0)
        self.settingsmenu.add_command(label="Keywords", command=self._open_keywords_menu)
        self.settingsmenu.add_command(label="Context Size", command=self._open_context_size_menu)
        self.add_cascade(label="Settings", menu=self.settingsmenu)

    def _new_summary_form(self):
        self.summary_form = SummaryForm(self)

    def _open_keywords_menu(self):
        self.keyword_settings_form = KeywordSettingsForm(self)

    def _open_context_size_menu(self):
        self.context_size_form = ContextSizeForm(self)

    def _run_keyword_scan(self):
        pdf_path = get_file_path()
        debut = perf_counter()
        output = scan_for_keywords(pdf_path, self.parent)
        fin = perf_counter()
        output_path = get_save_path('csv')
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['keyword', 'page', 'text', 'exhibit', 'provider', 'exhibit_page']
            csvdw = DictWriter(f, fieldnames=fieldnames)
            csvdw.writeheader()
            csvdw.writerows(output)
        print(f"Completed in {fin - debut:0.4f}s")

    def _run_comment_scrape(self):
        pdf_path = get_file_path()
        comments = scan_for_comments(pdf_path)
        if len(comments) > 0:
            output_path = get_save_path('csv')
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['page', 'date', 'text', 'provider', 'pagehead', 'ref']
                csvdw = DictWriter(f, fieldnames=fieldnames)
                csvdw.writeheader()
                csvdw.writerows(comments)

    def set_app_status(self, message):
        self.parent.set_status(message)
