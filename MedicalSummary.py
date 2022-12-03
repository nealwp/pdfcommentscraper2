from datetime import date, datetime
from tkinter import StringVar
from components.workhistory import WorkHistory

from medrecparser import Claimant

class SummaryInterface:
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
        self.criminal_history = StringVar()
        self.drug_use = StringVar()

        self.overview: str = ''
        self.work_history: WorkHistory = None
        self.claimant: Claimant = None
        self.exhibits = None
        self.claimant = None

    def read(self):
        return MedicalSummary(self)


class MedicalSummary:
    def __init__(self, intfc: SummaryInterface) -> None:
        self.client_name = intfc.client_name.get()
        self.client_ssn = intfc.client_ssn.get()
        self.title = intfc.title.get()
        self.application_date = intfc.application_date.get()
        self.onset_date = intfc.onset_date.get()
        self.insured_date = intfc.insured_date.get()
        self.prior_applications = intfc.prior_applications.get()
        self.birthdate = intfc.birthdate.get()
        self.education = intfc.education.get()
        self.criminal_history = intfc.criminal_history.get()
        self.drug_use = intfc.drug_use.get()

        self.overview = intfc.overview
        self.work_history: WorkHistory = intfc.work_history
        self.claimant: Claimant = intfc.claimant
        self.exhibits = intfc.exhibits
        self.claimant = intfc.claimant

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
