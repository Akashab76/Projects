import json
import os
from utils import min_to_time_12h

STORAGE_FILE = "latest_schedules.json"

def save_schedule(sem, schedule, time_slots, sections, days):
    """
    Save schedule data for a semester.
    Converts schedule dict keys to strings for JSON compatibility.
    """
    # Load existing data
    all_data = load_all_schedules()
    
    # Build class list for this semester
    classes = []
    
    for key, entry in schedule.items():
        if entry.get("skip"):
            continue
        
        sec, day, idx = key
        
        # Get time from time_slots
        slots_key = (sec, day)
        if slots_key not in time_slots or idx >= len(time_slots[slots_key]):
            continue
        
        start, end = time_slots[slots_key][idx]
        time_str = f"{min_to_time_12h(start)}-{min_to_time_12h(end)}"
        
        # Handle lab spans (takes 2 slots)
        if entry.get("lab_span") and idx + 1 < len(time_slots[slots_key]):
            _, end = time_slots[slots_key][idx + 1]
            time_str = f"{min_to_time_12h(start)}-{min_to_time_12h(end)}"
        
        classes.append({
            "sem": sem,
            "section": sec,
            "day": day,
            "time": time_str,
            "time_start": start,
            "subject": entry.get("code", "???"),
            "teacher": entry.get("teacher", "???"),
            "room": entry.get("room", "???"),
            "type": entry.get("type", "theory")
        })
    
    # Store for this semester
    all_data[sem] = classes
    
    # Save to file
    with open(STORAGE_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"✅ Saved {len(classes)} classes for Semester {sem}")


def load_all_schedules():
    """Load all saved schedules"""
    if not os.path.exists(STORAGE_FILE):
        return {}
    
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def get_all_classes():
    """Get all classes from all semesters"""
    data = load_all_schedules()
    all_classes = []
    for sem, classes in data.items():
        all_classes.extend(classes)
    return all_classes


def get_classes_for_semester(sem):
    """Get classes for a specific semester"""
    data = load_all_schedules()
    return data.get(str(sem), [])


def get_classes_for_teacher(teacher_short, semesters=None):
    """
    Get all classes for a specific teacher.
    If semesters is None, gets from all semesters.
    If semesters is a list like ["3", "5"], gets only from those.
    """
    all_classes = get_all_classes()
    
    classes = [c for c in all_classes if c["teacher"] == teacher_short]
    
    if semesters:
        classes = [c for c in classes if c["sem"] in semesters]
    
    return classes


def clear_all():
    """Clear all stored schedules"""
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)