from datetime import datetime
import random
import re
from sqlite3 import Date
from time import perf_counter
from csv import writer, DictWriter
from tkinter import BOTH, END, LEFT, Canvas, LabelFrame, Listbox, Scrollbar, StringVar, Text, Tk, Button, Label, Entry, Toplevel, Menu, Frame, SUNKEN, N, S, E, W, BOTTOM, X, messagebox
from tkinter.ttk import Combobox
from tkcalendar import Calendar, DateEntry
from commentscraper import scrape_comments
from pdfscanner import scan_for_keywords, scan_for_comments, scan_pdf_for_summary
from docwriter import generate_chronological_medical_summary, generate_tablular_medical_summary
from pathlib import Path
import subprocess
import requests

from configparser import ConfigParser
import json

from helpers import write_csv, get_file_path, get_save_path, get_age, get_age_at_onset

config = ConfigParser()

class App(Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.attributes('-alpha', 0.0)
        self.geometry('809x500')
        self.title('disabilitydude')

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=BOTTOM, fill=X)

        self.menubar = MenuBar(self)        
        self.config(menu=self.menubar)
        
        self._center()
        self.attributes('-alpha', 1.0)

    def _center(self):
        """
        centers a tkinter window
        :param win: the main window or Toplevel window to center
        """
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.deiconify()

class SummaryForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.work_history = []
        self.pdf_comments = []
        self.pdf_path = ""
        self.attributes('-alpha', 0.0)
        self.title('New Summary')
        
        self.detect_client_btn = Button(self, text="Get Data from PDF", command=self._get_summary_data)
        self.detect_client_btn.bind("<Enter>", on_enter)
        self.detect_client_btn.bind("<Leave>", on_leave)
        self.detect_client_btn.grid(column=0, row=0, sticky='w', padx=10, pady=2)

        self.comment_count_label = Label(self, text="Comments Found: N/A", width=18)
        self.comment_count_label.grid(column=1, row=0, sticky='w', padx=10, pady=2)
        #self.view_comments_btn = Button(self, text="View PDF Comments", width=18, state='disabled', command=self._view_comments)
        #self.view_comments_btn.grid(column=4, row=1, sticky='w', padx=10, pady=2)

        self.name_label = Label(self, text="Client Name:")
        self.name_label.grid(column=0, row=1, sticky='w', padx=10, pady=2)
        
        self.name_entry = Entry(self, bd=1, width=32)
        self.name_entry.grid(column=1, row=1, sticky='e', padx=10, pady=2)
        
        self.ssn_label = Label(self, text="SSN:")
        self.ssn_label.grid(column=0, row=2, sticky='w', padx=10, pady=2)
        
        self.ssn_entry = Entry(self, bd=1, width=32)
        self.ssn_entry.grid(column=1, row=2, sticky='e', padx=10, pady=2)

        self.title_label = Label(self, text="Title:")
        self.title_label.grid(column=0, row=3, sticky='w', padx=10, pady=2)
        
        self.title_entry = Entry(self, bd=1, width=32)
        self.title_entry.grid(column=1, row=3, sticky='e', padx=10, pady=2)

        self.application_date_label = Label(self, text="Application Date:")
        self.application_date_label.grid(column=0, row=4, sticky='w', padx=10, pady=2)

        #application_date_entry = Calendar(win, selectmode='day')
        self.application_date_entry = Entry(self, bd=1, width=32)
        self.application_date_entry.grid(column=1, row=4, sticky='e', padx=10, pady=2)

        self.onset_date_label = Label(self, text="Alleged Onset Date:")
        self.onset_date_label.grid(column=0, row=5, sticky='w', padx=10, pady=2)

        self.onset_date_entry = Entry(self, bd=1, width=32)
        self.onset_date_entry.grid(column=1, row=5, sticky='e', padx=10, pady=2)

        self.insured_date_label = Label(self, text="Last Insured Date:")
        self.insured_date_label.grid(column=0, row=6, sticky='w', padx=10, pady=2)

        self.insured_date_entry = Entry(self, bd=1, width=32)
        self.insured_date_entry.grid(column=1, row=6, sticky='e', padx=10, pady=2)

        self.prior_label = Label(self, text="Prior Applications?")
        self.prior_label.grid(column=0, row=7, sticky='w', padx=10, pady=2)

        self.prior_txtVar = StringVar()
        self.prior_combo = Combobox(self, width=6, textvariable=self.prior_txtVar, justify='left')
        self.prior_combo['values'] = ('No', 'Yes')
        self.prior_combo.grid(column=1, row=7, sticky='e', padx=10, pady=2)
        self.prior_combo.current(0)

        self.birthday_label = Label(self, text="Date of Birth:")
        self.birthday_label.grid(column=0, row=8, sticky='w', padx=10, pady=2)

        self.birthday_entry = Entry(self, bd=1, width=32)
        self.birthday_entry.grid(column=1, row=8, sticky='e', padx=10, pady=2)

        self.education_label = Label(self, text="Education:")
        self.education_label.grid(column=0, row=9, sticky='w', padx=10, pady=2)

        self.education_entry = Entry(self, bd=1, width=32)
        self.education_entry.grid(column=1, row=9, sticky='e', padx=10, pady=2)

        self.drugs_label = Label(self, text="Drug Use?")
        self.drugs_label.grid(column=0, row=10, sticky='w', padx=10, pady=2)

        self.drugs_txtVar = StringVar()
        self.drugs_combo = Combobox(self, width=6, textvariable=self.drugs_txtVar, justify='left')
        self.drugs_combo['values'] = ('No', 'Yes')
        self.drugs_combo.grid(column=1, row=10, sticky='e', padx=10, pady=2)
        self.drugs_combo.current(0)

        self.criminal_label = Label(self, text="Criminal History?")
        self.criminal_label.grid(column=0, row=11, sticky='w', padx=10, pady=2)

        self.criminal_txtVar = StringVar()
        self.criminal_combo = Combobox(self, width=6, textvariable=self.criminal_txtVar, justify='left')
        self.criminal_combo['values'] = ('No', 'Yes')
        self.criminal_combo.grid(column=1, row=11, sticky='e', padx=10, pady=2)
        self.criminal_combo.current(0)

        self.overview_label = Label(self, text="Evaluation:")
        self.overview_label.grid(column=0, row=12, sticky='w', padx=10, pady=2)

        self.overview_text = Text(self, height=4, font='Calibri', wrap='word')
        self.overview_text.grid(column=0, row=13, columnspan=4, rowspan=2, padx=10, pady=2)

        self.add_work_history_btn = Button(self, text="Add Work History", command=self._open_work_history_form)
        self.add_work_history_btn.bind("<Enter>", on_enter)
        self.add_work_history_btn.bind("<Leave>", on_leave)
        self.add_work_history_btn.grid(column=2, row=0, columnspan=2)
        
        self.work_history_frame = LabelFrame(self, text="Work History")
        self.work_history_frame.grid(column=2, row=1, columnspan=2, rowspan=12, sticky='n', pady=10)

        cancel_btn = Button(self, text='Cancel', width=20, command=self.destroy)
        cancel_btn.bind("<Enter>", on_enter)
        cancel_btn.bind("<Leave>", on_leave)
        cancel_btn.grid(column=0, row=99, columnspan=2, padx=10, pady=4)

        done_btn = Button(self, text='Generate Summary', width=20, command=self._save_to_file)
        done_btn.bind("<Enter>", on_enter)
        done_btn.bind("<Leave>", on_leave)
        done_btn.grid(column=1, row=99, columnspan=2, padx=10, pady=4)

        center(self)
        self.attributes('-alpha', 1.0)

    def _open_work_history_form(self):
        self.work_history_form = WorkHistoryForm(self)

    def _detect_client_info(self):
        if not self.pdf_path:
            self.pdf_path = get_file_path()

        client_info = "" #scan_for_client_info(self.pdf_path)
        self.name_entry.insert(0, client_info['Claimant'])
        self.ssn_entry.insert(0, client_info['SSN'])
        self.onset_date_entry.insert(0, client_info['Alleged Onset'])
        self.title_entry.insert(0, client_info['Claim Type'])
        self.application_date_entry.insert(0, client_info['Application'])
        self.update()
        self.deiconify()

    def _paint_work_history(self):
        for i, entry in enumerate(self.work_history, start=1):
            entry_text = f'{i}. {entry["job_title"]} : {entry["intensity"]} : {entry["skill_level"]}'
            label = Label(self.work_history_frame, text=entry_text)
            label.grid(column=0, row=i+1, padx=10, pady=2, sticky='w')

    def _scan_for_comments(self):
        if not self.pdf_path:
            self.pdf_path = get_file_path()
        
        self.pdf_comments = scan_for_comments(self.pdf_path)
        
        comment_count = len(self.pdf_comments)
        self.comment_count_label.configure(text=f'Comments Found: {comment_count}')
        #self.view_comments_btn.configure(state='normal')
        #self.view_comments_btn.bind("<Enter>", on_enter)
        #self.view_comments_btn.bind("<Leave>", on_leave)
        
        self.update()
        self.deiconify()

    def _get_summary_data(self):
        if not self.pdf_path:
            self.pdf_path = get_file_path()
        self.deiconify()
        self.summary_data = scan_pdf_for_summary(self.pdf_path)
        self._fill_entry_fields()
        self.update()
        
        

    def _fill_entry_fields(self):
        client = self.summary_data['client']
        self.pdf_comments = self.summary_data['comments']
        self.work_history = self.summary_data['work_history']

        self.name_entry.insert(0, client['Claimant'])
        self.ssn_entry.insert(0, client['SSN'])
        self.onset_date_entry.insert(0, client['Alleged Onset'])
        self.title_entry.insert(0, client['Claim Type'])
        self.application_date_entry.insert(0, client['Application'])
        self.birthday_entry.insert(0, client['Date of Birth'])
        self.insured_date_entry.insert(0, client['Last Insured'])

        comment_count = len(self.pdf_comments)
        self.comment_count_label.configure(text=f'Comments Found: {comment_count}')
        self._paint_work_history()

    def _view_comments(self):
        self.comment_viewer = CommentViewer(self)

    def _save_to_file(self):
        
        client_name = self.name_entry.get()
        client_ssn = self.ssn_entry.get()
        title = self.title_entry.get()
        application_date = self.application_date_entry.get()
        onset_date = self.onset_date_entry.get()
        insured_date = self.insured_date_entry.get()
        prior_applications = self.prior_txtVar.get()
        birthdate = self.birthday_entry.get()
        education = self.education_entry.get()
        work_history = self.work_history
        drug_use = self.drugs_txtVar.get()
        criminal_history = self.criminal_txtVar.get()
        overview = self.overview_text.get('1.0', 'end-1c')
        comments = self.pdf_comments

        if birthdate:
            age = get_age(birthdate)
        else: age = ''

        if birthdate and onset_date:
            age_at_onset = get_age_at_onset(birthdate, onset_date)
        else: age_at_onset =''

        data = {
            'client_name': client_name,
            'client_ssn': client_ssn,
            'title': title,
            'application_date': application_date,
            'onset_date': onset_date,
            'insured_date': insured_date,
            'prior_applications': prior_applications,
            'birthdate': birthdate,
            'age': age,
            'age_at_onset': age_at_onset,
            'education': education,
            'work_history': work_history,
            'drug_use': drug_use,
            'criminal_history': criminal_history,
            'overview': overview,
            'comments': comments
        }

        doc = generate_tablular_medical_summary(data)
        output_path = get_save_path('docx')
        doc.save(output_path)

        self.parent.parent.status_bar._set_status('Data Saved')
        self.destroy()
        return

class CommentViewer(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Work History')

        self.container = Frame(self)
        self.canvas = Canvas(self.container)
        self.scrollbar = Scrollbar(self.container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        for row, comment in enumerate(self.parent.pdf_comments):
            txtbox = Label(self.scrollable_frame, wraplength=500, justify=LEFT, bg="white", borderwidth=1)
            txtbox.configure(text=comment['text'])
            txtbox.pack()
            #txtbox.configure(state='disabled')

        self.container.pack()
        self.canvas.pack(side='left', fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.close_btn = Button(self, text='Close', width=12, command=self.destroy)
        self.close_btn.pack()

        center(self)
        self.attributes('-alpha', 1.0)

class WorkHistoryForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.intensity_options = ('Light', 'Medium', 'Heavy', 'Sedentary')
        self.skill_level_options = ('Unskilled', 'Semi-Skilled', 'Skilled')
        self.attributes('-alpha', 0.0)
        self.title('Work History')

        self.job_title_label = Label(self, text="Job Title")
        self.job_title_label.grid(column=0, row=0, padx=10, pady=2, sticky='w')

        self.job_title_entry = Entry(self, bd=1)
        self.job_title_entry.grid(column=0, row=1, padx=10, pady=2)

        self.intensity_label = Label(self, text="Intensity")
        self.intensity_label.grid(column=1, row=0, padx=10, pady=2, sticky='w')

        self.intensity_txtVar = StringVar()
        self.intensity_combo = Combobox(self, textvariable=self.intensity_txtVar, justify='left')
        self.intensity_combo['values'] = self.intensity_options
        self.intensity_combo.grid(column=1, row=1, padx=10, pady=2)
        self.intensity_combo.current(0)

        self.skill_level_label = Label(self, text="Skill Level")
        self.skill_level_label.grid(column=2, row=0, padx=10, pady=2, sticky='w')

        self.skill_level_txtVar = StringVar()
        self.skill_level_combo = Combobox(self, textvariable=self.skill_level_txtVar, justify='left')
        self.skill_level_combo['values'] = self.skill_level_options
        self.skill_level_combo.grid(column=2, row=1, padx=10, pady=2)
        self.skill_level_combo.current(0)

        self.add_entry_btn = Button(self, text='Add', command=self._add_entry)
        self.add_entry_btn.grid(column=3, row=1, padx=10, pady=2)

        self.close_btn = Button(self, text='Close', width=12, command=self.destroy)
        self.close_btn.grid(column=0, row=2, columnspan=4, pady=4)

        center(self)
        self.attributes('-alpha', 1.0)
    
    def _add_entry(self):
        entry = {
            'job_title': self.job_title_entry.get(),
            'intensity': self.intensity_txtVar.get(),
            'skill_level': self.skill_level_txtVar.get()
        }

        self.parent.work_history.append(entry)
        self.parent._paint_work_history()
        self.parent.update()

class KeywordSettingsForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)

        self.parent = parent
        self.attributes('-alpha', 0.0)
        self.title('Keyword Settings')

        self.leftFrame = Frame(self)
        self.leftFrame.grid(column=0, row=1)

        self.entrylabel = Label(self.leftFrame, text='New Keyword')
        self.entrylabel.grid(column=0, row=0, sticky='sw', rowspan=1, padx=10)

        self.entrybox = Entry(self.leftFrame, width=24, bd=1)
        self.entrybox.grid(column=0, row=1, sticky='nw', rowspan=1, columnspan=1, padx=10)

        self.addBtn = Button(self.leftFrame, text='Add', command=self._add_keyword)
        self.addBtn.grid(column=0, row=2, pady=10)
        self.addBtn.bind("<Enter>", on_enter)
        self.addBtn.bind("<Leave>", on_leave)

        
        # self.importKeywordsBtn = Button(
        #     self.leftFrame, 
        #     text='Import Keywords from File', 
        #     command=self._select_keywords_file
        #     )
        #     
        # self.importKeywordsBtn.grid(column=0, row=3, pady=10)
        # self.importKeywordsBtn.bind("<Enter>", on_enter)
        # self.importKeywordsBtn.bind("<Leave>", on_leave)

        self.rightFrame = Frame(self)
        self.rightFrame.grid(column=1, row=1, pady=10)
        
        self._get_keywords()

        self.keywordboxlabel = Label(self.rightFrame, text='Active Keywords')
        self.keywordboxlabel.grid(column=0, row=0, sticky='nw', rowspan=1)

        self.listbox = Listbox(self.rightFrame, height=16, selectmode='single', activestyle='none')
        for i, kw in enumerate(self.keywords):
            self.listbox.insert(i, kw)

        self.listbox.grid(column=0, row=1, sticky='nw')

        self.scrollbar = Scrollbar(self.rightFrame, orient='vertical', command=self.listbox.yview)
        self.scrollbar.grid(column=1, row=1, sticky='nsw')
        self.listbox['yscrollcommand'] = self.scrollbar.set

        self.deleteBtn = Button(self.rightFrame, text='Delete Selected', command=self._delete_keyword)
        self.deleteBtn.grid(column=0, row=2, pady=10)
        self.deleteBtn.bind("<Enter>", on_enter)
        self.deleteBtn.bind("<Leave>", on_leave)
        
        doneBtn = Button(self, text='Done', command=self.destroy)
        doneBtn.bind("<Enter>", on_enter)
        doneBtn.bind("<Leave>", on_leave)
        doneBtn.grid(column=0, row=3, columnspan=2, pady=10)
     
        center(self)
        self.attributes('-alpha', 1.0)

    def _add_keyword(self):
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        word = self.entrybox.get()
        self.entrybox.delete(0, END)
        with open(kw_file_path, "a") as keyword_file:
            keyword_file.write(word + '\n')
        self._refresh_keyword_listbox()

    def _get_keywords(self):
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        with open(kw_file_path, "r") as keyword_file:
            file_content = keyword_file.read()
            keywords = file_content.split('\n')
            keywords = [w for w in keywords if w]
            keywords.sort()
            self.keywords = keywords

    def _select_keywords_file(self):
        custom_keywords_path = get_file_path()


    def _refresh_keyword_listbox(self):
        self.listbox.delete(0, END)
        self._get_keywords()
        for i, kw in enumerate(self.keywords):
            self.listbox.insert(i, kw)

    def _delete_keyword(self):
        idx = self.listbox.curselection()
        word = self.listbox.get(idx)
        for i, kw in enumerate(self.keywords):
            if kw == word:
                self.keywords.pop(i)
        config.read('./config/config.ini')
        kw_file_path = config['Keywords']['Path']
        with open(kw_file_path, "w") as keyword_file:
            keyword_file.writelines(kw + '\n' for kw in self.keywords)
        self.listbox.delete(idx)

class ContextSizeForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.attributes('-alpha', 0.0)
        self.title('Context Size Settings')

        words_minus_label = Label(self, text="Words Before Keyword:")
        words_minus_label.grid(column=0, row=0, sticky='w', padx=10, pady=3)
        
        self.words_minus_entry = Entry(self, width=3, bd=1)
        self.words_minus_entry.grid(column=1, row=0, sticky='e', padx=10, pady=3)
        
        words_plus_label = Label(self, text="Words After Keyword:")
        words_plus_label.grid(column=0, row=1, sticky='w', padx=10, pady=3)
        
        self.words_plus_entry = Entry(self, width=3, bd=1)
        self.words_plus_entry.grid(column=1, row=1, sticky='e', padx=10, pady=3)

        done_btn = Button(self, text='Apply', command=self._set_context_settings)
        done_btn.bind("<Enter>", on_enter)
        done_btn.bind("<Leave>", on_leave)
        done_btn.grid(column=0, row=3, columnspan=2, pady=3)
        
        self._get_context_settings()
        center(self)
        self.attributes('-alpha', 1.0)

    def _get_context_settings(self):
        config.read('./config/config.ini')
        self.words_minus_entry.insert(0, config['Keywords']['ContextBefore'])
        self.words_plus_entry.insert(0, config['Keywords']['ContextAfter'])

    def _set_context_settings(self):
        context_before = self.words_minus_entry.get()
        context_after = self.words_plus_entry.get()

        config.read('./config/config.ini')
        config['Keywords']['ContextBefore'] = context_before
        config['Keywords']['ContextAfter'] = context_after
        with open('./config/config.ini', 'w') as configfile:
            config.write(configfile)

class StatusBar(Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bd=1, relief=SUNKEN)
        self.parent = parent
                
        self.status = Label(self, text='Ready', anchor=W, padx=5)
        self.status.grid(column=0, row=0, sticky='w', columnspan=1)
        
        self.version = Label(self, text='error', anchor=E, padx=5)
        self.version.grid(column=1, row=0, sticky="e", columnspan=1)
        self._get_app_version()

        self.columnconfigure(0, weight=1)

    def _set_status(self, message):
        self.status.configure(text=message)

    def _reset_status(self):
        self.status.configure(text='Ready')
    
    def _get_app_version(self):
        version = get_app_version()
        self.version.config(text=f"v{version}")

class MenuBar(Menu):
    def __init__(self, parent) -> None:
        super().__init__(parent, bd=5)
        self.parent = parent

        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label='New Summary', command=self._new_summary_form)
        self.filemenu.add_command(label='Check for Updates', command=self._check_for_updates)
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
        
        self.add_command(label="Help", command=self._get_help)

    def _new_summary_form(self):
        self.summary_form = SummaryForm(self)

    def _check_for_updates(self):
        r = requests.get('https://prestonneal.com/v1/apps/disabilitydude/latest')
        response = r.json()
        url = response['url']
        prompt_response = messagebox.askyesno('Update Available', 'A new update is available. Would you like to install now?')
        if prompt_response == True:
            messagebox.showinfo('Path', Path().absolute())
            app_path = Path().absolute()
            download_path = '%userprofile%\\AppData\\Local\\Temp\\disabilitydude.zip'
            extract_path = '%userprofile%\\AppData\\Local\\Temp\\disabilitydude'
            install_path = '%userprofile%\\AppData\\Local\\disabilitydude'
            subprocess.Popen(f'{app_path}\install.bat {url} {download_path} {extract_path} {install_path}',
                creationflags=subprocess.CREATE_NEW_CONSOLE)
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
        output = scan_for_keywords(pdf_path, self.parent)
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
        comments = scan_for_comments(pdf_path)
        print(comments)

    def set_app_status(self, message):
        self.parent.set_status(message)

def findWholeWord(w):
    return re.compile(r'\b^({0})$\b'.format(w), flags=re.IGNORECASE).search

def run_commentscraper():
    scrape_comments()
    return

def on_enter(e):
    e.widget['background'] = '#ddd'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

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

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def check_for_updates():
    r = requests.get('http://localhost:3000/apps/disabilitydude/latest')
    response = r.json()
    url = response['url']
    release = get_app_release()
    if release < datetime.strptime(response['release_date'], '%Y-%m-%dT%H:%M:%S'):
        prompt_response = messagebox.askyesno('Update Available', f'A new update is available. Would you like to install now?')
        if prompt_response == True:
            app_path = Path().absolute()
            download_path = '%userprofile%\\AppData\\Local\\Temp\\disabilitydude.zip'
            extract_path = '%userprofile%\\AppData\\Local\\Temp\\disabilitydude'
            install_path = '%userprofile%\\AppData\\Local\\disabilitydude'
            subprocess.Popen(f'{app_path}\install.bat {url} {download_path} {extract_path} {install_path}',
                creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
    return False

if __name__ == '__main__':
    updating = check_for_updates()
    if updating:
        exit()
    app = App()
    app.mainloop()