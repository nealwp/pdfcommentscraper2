from tkinter import Frame, LabelFrame, Tk, StringVar, Button, Label, Entry, Toplevel, END
from tkinter.ttk import Combobox

import shared.helpers as helpers

class WorkHistoryForm(Toplevel):
    def __init__(self, parent, work_history):
        super().__init__(parent, padx=15, pady=15)
        self.parent = parent
        self.work_history = work_history
        self.intensity_options = ('Light', 'Medium', 'Heavy', 'Sedentary')
        self.skill_level_options = ('Unskilled', 'Semi-Skilled', 'Skilled')
        self.attributes('-alpha', 0.0)
        self.title('Work History')

        self.job_title_label = Label(self, text="Job Title")
        self.job_title_label.grid(column=0, row=0, sticky='w')

        self.job_title_entry = Entry(self, justify='left')
        self.job_title_entry.grid(column=0, row=1, sticky='w')

        self.intensity_label = Label(self, text="Intensity")
        self.intensity_label.grid(column=0, row=3, sticky='w')

        self.intensity_txtVar = StringVar()
        self.intensity_combo = Combobox(self, textvariable=self.intensity_txtVar, justify='left')
        self.intensity_combo['values'] = self.intensity_options
        self.intensity_combo.grid(column=0, row=4)
        self.intensity_combo.current(0)

        self.skill_level_label = Label(self, text="Skill Level")
        self.skill_level_label.grid(column=0, row=5, sticky='w')

        self.skill_level_txtVar = StringVar()
        self.skill_level_combo = Combobox(self, textvariable=self.skill_level_txtVar, justify='left')
        self.skill_level_combo['values'] = self.skill_level_options
        self.skill_level_combo.grid(column=0, row=6)
        self.skill_level_combo.current(0)

        self.add_entry_btn = Button(self, text='Add', command=self._add_entry)
        self.add_entry_btn.grid(column=0, row=7, pady=4, padx=6)

        self.button_frame = Frame(self)
        self.button_frame.grid(column=0, row=8, columnspan=2, pady=(32, 0))

        Button(self.button_frame, text='Save', command=self.destroy, width=8).grid(column=0, row=0, pady=4, padx=6, sticky='s')
        Button(self.button_frame, text='Cancel', command=self.destroy, width=8).grid(column=1, row=0, pady=4, padx=6, sticky='s')

        self.work_history_frame_label = Label(self, text="Work History")
        self.work_history_frame_label.grid(column=1, row=0, sticky='w')

        self.work_history_frame = Frame(self)
        self.work_history_frame.grid(column=1, row=1, columnspan=2, rowspan=12, sticky='n')

        self.refresh_work_history()

        helpers.center(self)
        self.attributes('-alpha', 1.0)
    
    def _add_entry(self):
        job_title = self.job_title_entry.get()
        intensity = self.intensity_txtVar.get()
        skill_level = self.skill_level_txtVar.get()
        entry = {
            "job_title": job_title,
            "intensity": intensity,
            "skill_level": skill_level
        }
        self.work_history.append(entry)
        self.refresh_work_history()
        self.reset()
        self.geometry("")
        self.update_idletasks()
        self.update()

    def reset(self):
        self.job_title_entry.delete(0, END)

    def refresh_work_history(self):
        for row, entry in enumerate(self.work_history):
            entry_text = f'{row+1}. {entry["job_title"]} : {entry["intensity"]} : {entry["skill_level"]}'
            Label(self.work_history_frame, text=entry_text).grid(column=0, row=row, padx=10, pady=2, sticky='w')

def main():

    app = Tk()
    work_history = []
    work_history = WorkHistoryForm(app, work_history) 
    app.mainloop()
    return

if __name__ == '__main__':
    main()