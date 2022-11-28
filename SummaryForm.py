from tkinter import Tk, LabelFrame, StringVar, Text, Button, Label, Entry, Toplevel
from tkinter.ttk import Combobox

from datetime import date, datetime

from CommentsForm import CommentViewer
from MedicalSummary import MedicalSummary, SummaryInterface
from WorkHistoryForm import WorkHistoryForm
from WorkHistory import WorkHistory, WorkHistoryEntry
from docwriter import generate_tablular_medical_summary
from helpers import get_file_path, on_enter, on_leave, center, get_save_path
from medrecparser import MedicalRecord
from pdfscanner import PDFReader

class SummaryForm(Toplevel):
    def __init__(self, parent):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.summary = SummaryInterface()
        self.work_history = WorkHistory()
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

        self.name_label = Label(self, text="Client Name:")
        self.name_label.grid(column=0, row=1, sticky='w', padx=10, pady=2)
        
        self.name_entry = Entry(self, bd=1, width=32, textvariable=self.summary.client_name)
        self.name_entry.grid(column=1, row=1, sticky='e', padx=10, pady=2)
        
        self.ssn_label = Label(self, text="SSN:")
        self.ssn_label.grid(column=0, row=2, sticky='w', padx=10, pady=2)
        
        self.ssn_entry = Entry(self, bd=1, width=32, textvariable=self.summary.client_ssn)
        self.ssn_entry.grid(column=1, row=2, sticky='e', padx=10, pady=2)

        self.title_label = Label(self, text="Title:")
        self.title_label.grid(column=0, row=3, sticky='w', padx=10, pady=2)
        
        self.title_entry = Entry(self, bd=1, width=32, textvariable=self.summary.title)
        self.title_entry.grid(column=1, row=3, sticky='e', padx=10, pady=2)

        self.application_date_label = Label(self, text="Application Date:")
        self.application_date_label.grid(column=0, row=4, sticky='w', padx=10, pady=2)

        #application_date_entry = Calendar(win, selectmode='day')
        self.application_date_entry = Entry(self, bd=1, width=32, textvariable=self.summary.application_date)
        self.application_date_entry.grid(column=1, row=4, sticky='e', padx=10, pady=2)

        self.onset_date_label = Label(self, text="Alleged Onset Date:")
        self.onset_date_label.grid(column=0, row=5, sticky='w', padx=10, pady=2)

        self.onset_date_entry = Entry(self, bd=1, width=32, textvariable=self.summary.onset_date)
        self.onset_date_entry.grid(column=1, row=5, sticky='e', padx=10, pady=2)

        self.insured_date_label = Label(self, text="Last Insured Date:")
        self.insured_date_label.grid(column=0, row=6, sticky='w', padx=10, pady=2)

        self.insured_date_entry = Entry(self, bd=1, width=32, textvariable=self.summary.insured_date)
        self.insured_date_entry.grid(column=1, row=6, sticky='e', padx=10, pady=2)

        self.prior_label = Label(self, text="Prior Applications?")
        self.prior_label.grid(column=0, row=7, sticky='w', padx=10, pady=2)

        self.prior_combo = Combobox(self, width=6, textvariable=self.summary.prior_applications, justify='left')
        self.prior_combo['values'] = ('No', 'Yes')
        self.prior_combo.grid(column=1, row=7, sticky='e', padx=10, pady=2)
        self.prior_combo.current(0)

        self.birthday_label = Label(self, text="Date of Birth:")
        self.birthday_label.grid(column=0, row=8, sticky='w', padx=10, pady=2)

        self.birthday_entry = Entry(self, bd=1, width=32, textvariable=self.summary.birthdate)
        self.birthday_entry.grid(column=1, row=8, sticky='e', padx=10, pady=2)

        self.education_label = Label(self, text="Education:")
        self.education_label.grid(column=0, row=9, sticky='w', padx=10, pady=2)

        self.education_entry = Entry(self, bd=1, width=32, textvariable=self.summary.education)
        self.education_entry.grid(column=1, row=9, sticky='e', padx=10, pady=2)

        self.drugs_label = Label(self, text="Drug Use?")
        self.drugs_label.grid(column=0, row=10, sticky='w', padx=10, pady=2)

        self.drugs_combo = Combobox(self, width=6, textvariable=self.summary.drug_use, justify='left')
        self.drugs_combo['values'] = ('No', 'Yes')
        self.drugs_combo.grid(column=1, row=10, sticky='e', padx=10, pady=2)
        self.drugs_combo.current(0)

        self.criminal_label = Label(self, text="Criminal History?")
        self.criminal_label.grid(column=0, row=11, sticky='w', padx=10, pady=2)

        self.criminal_combo = Combobox(self, width=6, textvariable=self.summary.criminal_history, justify='left')
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
        self._paint_work_history()
        self.attributes('-alpha', 1.0)

    def _open_work_history_form(self):
        self.work_history_form = WorkHistoryForm(self)

    def _paint_work_history(self):
        entry: WorkHistoryEntry
        for i, entry in enumerate(self.work_history.entries, start=1):
            entry_text = f'{i}. {entry.job_title} : {entry.intensity} : {entry.skill_level}'
            label = Label(self.work_history_frame, text=entry_text)
            label.grid(column=0, row=i+1, padx=10, pady=2, sticky='w')
        self.update_idletasks()
        self.update()

    def _get_summary_data(self):
        try:
            if not self.pdf_path:
                self.pdf_path = get_file_path()
            self.deiconify()

            with open(self.pdf_path, 'rb') as fp:
                pdf_reader = PDFReader(fp)
                pdf_data = pdf_reader.read()
                self.medical_record = MedicalRecord(pdf_data)

            self._fill_entry_fields()
            self.update()
        except Exception as e:
            print('An error occurred')
        
    def _fill_entry_fields(self):
        mr = self.medical_record
        self.work_history = mr.claimant.work_history
        self.summary.client_name.set(mr.claimant.name)
        self.summary.client_ssn.set(mr.claimant.ssn)
        self.summary.onset_date.set(mr.claimant.onset_date)
        self.summary.title.set(mr.claimant.claim)
        self.summary.application_date.set(datetime.strftime(mr.claimant.pdof, '%m/%d/%Y'))
        self.summary.birthdate.set(mr.claimant.birthdate)
        self.summary.insured_date.set(mr.claimant.last_insured_date)

        comment_count = mr.comment_count()
        self.comment_count_label.configure(text=f'Comments Found: {comment_count}')
        self._paint_work_history()

    def _view_comments(self):
        self.comment_viewer = CommentViewer(self)

    def _save_to_file(self):  
        try:
            self.summary.work_history = self.work_history
            self.summary.overview = self.overview_text.get('1.0', 'end-1c')
            self.summary.exhibits = self.medical_record.exhibits
            #pages = self.medical_record.pages
            self.summary.claimant = self.medical_record.claimant

            doc = generate_tablular_medical_summary(self.summary.read())
            output_path = get_save_path('docx')
            doc.save(output_path)

            self.parent.parent.status_bar._set_status('Data Saved')
            self.destroy()
        except Exception as e:
            print('An error occurred')
        return

def main():
    app = Tk()
    summary_form = SummaryForm(app)
    app.mainloop()
    return

if __name__ == '__main__':
    main()