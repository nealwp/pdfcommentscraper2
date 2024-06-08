from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Claimant:
    '''individual the medical record pertains to'''
    name: str = None
    ssn: str = None
    birthdate: datetime = None
    education_years: int = None
    onset_date: datetime = None
    pdof: datetime = None
    claim: str = None
    last_insured_date: datetime = None
    work_history: list = None
    dds_rfc: dict = None
    claimed_mdsi: list = None

    def __eq__(self, o):
        if isinstance(self, o.__class__):
            return self.name == o.name \
                and self.ssn == o.ssn \
                and self.birthdate == o.birthdate \
                and self.education_years == o.education_years \
                and self.onset_date == o.onset_date \
                and self.pdof == o.pdof \
                and self.claim == o.claim \
                and self.last_insured_date == o.last_insured_date \
                and self.work_history == o.work_history \
                and self.dds_rfc == o.dds_rfc \
                and self.claimed_mdsi == o.claimed_mdsi

    def age(self) -> int:
        if self.birthdate:
            today = date.today()
            birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        else:
            return None

    def age_at_onset(self) -> int:

        if self.onset_date == "N/A":
            return None

        if self.birthdate and self.onset_date:
            birthdate = datetime.strptime(self.birthdate, '%m/%d/%Y')
            onset_date = datetime.strptime(self.onset_date, '%m/%d/%Y')
            return onset_date.year - birthdate.year - ((onset_date.month, onset_date.day) < (birthdate.month, birthdate.day))
        else:
            return None


@dataclass
class MedicalRecord:
    '''a social security pdf medical record'''
    claimant: Claimant
    exhibits: dict
    pages: dict

    def comment_count(self):
        count = 0
        for exhibit in self.exhibits.keys():
            count += len(self.exhibits[exhibit].comments)
        return count

    def comments(self):
        comments = []
        for exhibit in self.exhibits.keys():
            for c in self.exhibits[exhibit].comments:
                comments.append(c)
        return comments


@dataclass
class Comment:
    '''annotations made to the medical record by the reviewer'''
    date: datetime
    text: str
    page: int
    exhibit_page: int


@dataclass
class Exhibit:
    '''a section of the medical record'''
    provider_name: str
    from_date: str
    to_date: str
    comments: list

    def provider_handle(self):
        return ' '.join(self.provider_name.split(' - ')[1].split(' ')[1:]).title()


@dataclass
class PageDetail:
    '''detail for a page'''
    exhibit_id: str
    exhibit_page: int
