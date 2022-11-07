from tkinter import Tk, LabelFrame, StringVar, Text, Button, Label, Entry, Toplevel
from tkinter.ttk import Combobox

from datetime import date, datetime

from CommentsForm import CommentViewer
from WorkHistoryForm import WorkHistoryForm
from helpers import on_enter, on_leave, center, get_save_path

class SummaryForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.work_history = []
        self.pdf_comments = []
        self.medical_record = None
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
            self.pdf_path = 'TODO' #get_file_path()

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
            self.pdf_path = 'TODO' #get_file_path()
        
        self.pdf_comments = 'TODO' #scan_for_comments(self.pdf_path)
        
        comment_count = len(self.pdf_comments)
        self.comment_count_label.configure(text=f'Comments Found: {comment_count}')
        #self.view_comments_btn.configure(state='normal')
        #self.view_comments_btn.bind("<Enter>", on_enter)
        #self.view_comments_btn.bind("<Leave>", on_leave)
        
        self.update()
        self.deiconify()

    def _get_summary_data(self):
        if not self.pdf_path:
            self.pdf_path = 'TODO' #get_file_path()
        self.deiconify()
        self.medical_record = 'TODO' #scan_pdf_for_summary(self.pdf_path)
        self._fill_entry_fields()
        self.update()
        
    def _fill_entry_fields(self):
        mr = self.medical_record
        self.work_history = mr.claimant.work_history

        self.name_entry.insert(0, mr.claimant.name)
        self.ssn_entry.insert(0, mr.claimant.ssn)
        self.onset_date_entry.insert(0, mr.claimant.onset_date)
        self.title_entry.insert(0, mr.claimant.claim)
        self.application_date_entry.insert(0, datetime.strftime(mr.claimant.pdof, '%m/%d/%Y'))
        self.birthday_entry.insert(0, mr.claimant.birthdate)
        self.insured_date_entry.insert(0, mr.claimant.last_insured_date)

        comment_count = mr.comment_count()
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
        exhibits = self.medical_record.exhibits
        pages = self.medical_record.pages

        claimant = self.medical_record.claimant

        if self.medical_record:
            age = self.medical_record.claimant.age()
        else: 
            age = get_age(birthdate)

        if self.medical_record:
            age_at_onset = self.medical_record.claimant.age_at_onset()
        else:
            age_at_onset = get_age_at_onset(birthdate, onset_date)

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
            'claimant': claimant,
            'exhibits': exhibits,
            'pages': pages
        }

        doc = 'TODO'  #generate_tablular_medical_summary(data)
        output_path = get_save_path('docx')
        doc.save(output_path)

        self.parent.parent.status_bar._set_status('Data Saved')
        self.destroy()
        return

def get_age(birthdate):
    today = date.today()
    birthdate = datetime.strptime(birthdate, '%m/%d/%Y')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def get_age_at_onset(birthdate, onset_date):
    birthdate = datetime.strptime(birthdate, '%m/%d/%Y')
    onset_date = datetime.strptime(onset_date, '%m/%d/%Y')
    age_at_onset = onset_date.year - birthdate.year - ((onset_date.month, onset_date.day) < (birthdate.month, birthdate.day))
    return age_at_onset

def main():
    app = Tk()
    summary_form = SummaryForm(app)
    app.mainloop()
    return

if __name__ == '__main__':
    main()