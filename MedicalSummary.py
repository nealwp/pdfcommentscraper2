from datetime import date, datetime
from tkinter import StringVar


class MedicalSummary:
    def __init__(self) -> None:
        self.client_name = StringVar()
        self.client_ssn = StringVar()
        self.title = StringVar()
        self.application_date = StringVar()
        self.onset_date = StringVar()
        self.insured_date = StringVar()
        self.prior_applications = StringVar()
        self.birthdate = StringVar()
        self.education = StringVar()
        self.work_history = None
        self.drug_use = StringVar()
        self.criminal_history = StringVar()
        self.overview = StringVar()
        self.claimant = None
        self.exhibits = None
        self.claimant = None
        #self.pages = None

    @property
    def age(self):
        today = date.today()
        birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age

    @property
    def age_at_onset(self):
        birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
        onset_date = datetime.strptime(self.onset_date, '%m/%d/%Y')
        age_at_onset = onset_date.year - birthdate.year - ((onset_date.month, onset_date.day) < (birthdate.month, birthdate.day))
        return age_at_onset
