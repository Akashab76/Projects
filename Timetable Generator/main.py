# main.py - Updated with Enhanced AI Assistant, Open Electives, and Teacher Timetables
import tkinter as tk
from tkinter import ttk
from data import Data
from teachers_tab import create_teachers_tab
from subjects_tab import create_subjects_tab
from classrooms_tab import create_classrooms_tab
from sections_tab import create_sections_tab
from mapping_tab import create_mapping_tab
from open_elective_tab import create_open_elective_tab
from timings_tab import create_timings_tab
from generation_tab import create_generation_tab
from teacher_timetable_tab import create_teacher_timetable_tab
from enhanced_ai_assistant import create_enhanced_ai_tab
from teacher_availability_tab import create_availability_tab

root = tk.Tk()
root.title("Timetable Generator - Complete System")
root.geometry("1200x780")

data = Data()
nb = ttk.Notebook(root)

for name, func in [
    ("Teachers", create_teachers_tab), ("Subjects", create_subjects_tab),
    ("Classrooms", create_classrooms_tab), ("Sections", create_sections_tab),("⏰ Availability", create_availability_tab),
    ("Mapping", create_mapping_tab), ("Open Electives", create_open_elective_tab),
    ("Timings", create_timings_tab), ("Generate", create_generation_tab),
    ("👨‍🏫 Teacher Timetables", create_teacher_timetable_tab),
    ("🤖 AI Assistant", create_enhanced_ai_tab),
]:
    f = ttk.Frame(nb)
    func(f, data)
    nb.add(f, text=name)

nb.pack(expand=True, fill='both', padx=10, pady=10)
root.mainloop()