import pytest

from model.workhistory import WorkHistory, WorkHistoryEntry

def test_new_work_history_should_be_empty():
    work_history = WorkHistory()
    assert(work_history.entries) == []

def test_should_allow_new_entry():
    work_history = WorkHistory()
    entry = WorkHistoryEntry("Manager","Light","Skilled")
    work_history.add(entry)
    assert(len(work_history.entries)) == 1

def test_new_entry_should_be_correct():
    work_history = WorkHistory()
    entry = WorkHistoryEntry("Manager","Light","Skilled")
    work_history.add(entry)
    result:WorkHistoryEntry = work_history.entries[0]
    assert(result.job_title) == entry.job_title
    assert(result.intensity) == entry.intensity
    assert(result.skill_level) == entry.skill_level

def test_should_allow_multiple_new_entry():
    work_history = WorkHistory()
    entry_1 = WorkHistoryEntry("Manager","Light","Skilled")
    work_history.add(entry_1)
    entry_2 = WorkHistoryEntry("Worker","Heavy","Unskilled")
    work_history.add(entry_2)
    assert(len(work_history.entries)) == 2

def test_should_not_allow_invalid_entries():
    work_history = WorkHistory()
    entry = 'gobbledygook'
    with pytest.raises(TypeError):
        work_history.add(entry) 
