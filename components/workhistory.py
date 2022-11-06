from dataclasses import dataclass

@dataclass
class WorkHistoryEntry:
    job_title: str
    intensity: str
    skill_level: str

class WorkHistory:
    def __init__(self):
        self._entries = []

    def add(self, entry: WorkHistoryEntry):
        self._entries.append(entry)

    @property
    def entries(self):
        return self._entries