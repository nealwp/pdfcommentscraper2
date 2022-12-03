from tkinter import Menu, messagebox
from time import perf_counter
from csv import writer, DictWriter
import subprocess
import requests
from pathlib import Path

import random

from SummaryForm import SummaryForm
from components.contextsettings import ContextSizeForm
from components.keywordsettings import KeywordSettingsForm
from helpers import get_file_path, get_save_path
from datetime import datetime

from configparser import ConfigParser

config = ConfigParser()

class MenuBar(Menu):
    def __init__(self, parent) -> None:
        super().__init__(parent, bd=5)
        self.parent = parent

        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label='New Summary', command=self._new_summary_form)
        self.filemenu.add_command(label='Check for Updates', command=self._check_for_updates, state='disabled')
        self.filemenu.add_command(label="Exit", command=self.parent.destroy)
        self.add_cascade(label="File", menu=self.filemenu)

        self.actions_menu = Menu(self, tearoff=0)
        self.actions_menu.add_command(label="Scan PDF for Keywords", command=self._run_keyword_scan, state='disabled')
        self.actions_menu.add_command(label="Scrape Comments from PDF", command=self._run_comment_scrape, state='disabled')
        self.add_cascade(label="Actions", menu=self.actions_menu)
        
        self.settingsmenu = Menu(self, tearoff=0)
        self.settingsmenu.add_command(label="Keywords", command=self._open_keywords_menu, state='disabled')
        self.settingsmenu.add_command(label="Context Size", command=self._open_context_size_menu)
        self.add_cascade(label="Settings", menu=self.settingsmenu)
        
        self.add_command(label="Help", command=self._get_help)

    def _new_summary_form(self):
        self.summary_form = SummaryForm(self)

    def _check_for_updates(self):
        updating = check_for_updates()
        if not updating:
            messagebox.showinfo('Updates', 'You\'re up-to-date!')
            return
        self.parent.destroy()
        
    def _open_keywords_menu(self):
        self.keyword_settings_form = KeywordSettingsForm(self)

    def _open_context_size_menu(self):
        self.context_size_form = ContextSizeForm(self)

    def _get_help(self):
        quotes = [
            "Do or do not. There is no try.",
            "Whether you think you can or think you can't...you're right!",
            "The optimist sees opportunity in every difficulty.",
            "The secret of getting ahead is getting started.",
            "It's hard to beat a person who never gives up.",
            "Impossible is just an opinion.",
            "Have you tried turning it off and back on again?",
            "There are no problems; only solutions.",
            "Ready."
        ]
        self.parent.status_bar._set_status(random.choice(quotes))

    def _run_keyword_scan(self):
        pdf_path = get_file_path()
        debut = perf_counter()
        output = 'TODO' #scan_for_keywords(pdf_path, self.parent)
        fin = perf_counter()
        output_path = get_save_path('csv')
        with open(output_path,'w',encoding='utf-8', newline='') as f:
            fieldnames = ['keyword', 'page', 'text', 'exhibit', 'provider', 'exhibit_page']
            csvdw = DictWriter(f, fieldnames=fieldnames)
            csvdw.writeheader()
            csvdw.writerows(output)
        print(f"Completed in {fin - debut:0.4f}s")

    def _run_comment_scrape(self):
        # run_commentscraper()
        pdf_path = get_file_path()
        comments = 'TODO'  #scan_for_comments(pdf_path)
        if len(comments) > 0:
            output_path = get_save_path('csv')
            with open(output_path,'w',encoding='utf-8', newline='') as f:
                fieldnames = ['page', 'date', 'text', 'provider', 'pagehead', 'ref']
                csvdw = DictWriter(f, fieldnames=fieldnames)
                csvdw.writeheader()
                csvdw.writerows(comments)

    def set_app_status(self, message):
        self.parent.set_status(message)

def check_for_updates():
    r = requests.get('https://prestonneal.com/v1/apps/disabilitydude/latest')
    response = r.json()
    url = response['url']
    release = get_app_release()
    if release < datetime.strptime(response['release_date'], '%Y-%m-%dT%H:%M:%S'):
        prompt_response = messagebox.askyesno('Update Available', f'A new update is available. Would you like to install now?')
        if prompt_response == True:
            app_path = Path().absolute()
            subprocess.Popen(f'{app_path}\install.bat {url}',
                creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
    return False

def get_app_version():
    app_path = Path().absolute()
    config_path = app_path / "config/config.ini"
    config.read(config_path)
    version = config['Application']['version']
    return version

def get_app_release():
    app_path = Path().absolute()
    config_path = app_path / "config/config.ini"
    config.read(config_path)
    release = datetime.strptime(config['Application']['release'], '%Y-%m-%dT%H:%M:%S')
    return release