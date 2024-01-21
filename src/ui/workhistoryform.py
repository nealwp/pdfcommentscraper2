from tkinter import Toplevel, Label, Entry, StringVar, Button
from tkinter.ttk import Combobox


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
