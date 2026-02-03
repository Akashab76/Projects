# subjects_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

def create_subjects_tab(parent, data):
    ttk.Label(parent, text="Semester:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sem_combo = ttk.Combobox(parent, values=[str(i) for i in range(1,9)], width=5); sem_combo.grid(row=0, column=1)
    ttk.Label(parent, text="Code:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    code_entry = ttk.Entry(parent, width=15); code_entry.grid(row=1, column=1)
    ttk.Label(parent, text="Name:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    name_entry = ttk.Entry(parent, width=25); name_entry.grid(row=2, column=1)
    ttk.Label(parent, text="Elective:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    ele_combo = ttk.Combobox(parent, values=["yes", "no"], width=5); ele_combo.grid(row=3, column=1)
    ttk.Label(parent, text="Open Elective:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
    open_ele_combo = ttk.Combobox(parent, values=["yes", "no"], width=5); open_ele_combo.grid(row=4, column=1)
    ttk.Label(parent, text="Lab:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
    lab_combo = ttk.Combobox(parent, values=["yes", "no"], width=5); lab_combo.grid(row=5, column=1)
    ttk.Label(parent, text="L:").grid(row=6, column=0, sticky='w', padx=5, pady=2); l_entry = ttk.Entry(parent, width=5); l_entry.grid(row=6, column=1, sticky='w')
    ttk.Label(parent, text="T:").grid(row=7, column=0, sticky='w', padx=5, pady=2); t_entry = ttk.Entry(parent, width=5); t_entry.grid(row=7, column=1, sticky='w')
    ttk.Label(parent, text="P:").grid(row=8, column=0, sticky='w', padx=5, pady=2); p_entry = ttk.Entry(parent, width=5); p_entry.grid(row=8, column=1, sticky='w')

    listbox = tk.Listbox(parent, height=20, width=90, font=("Courier", 9)); listbox.grid(row=0, column=2, rowspan=12, padx=10, pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        for sem in data.subjects:
            for s in data.subjects[sem]:
                open_ele_str = s.get('open_elective', 'no')
                listbox.insert(tk.END, f"Sem {sem} | {s['code']} | {s['name']} | Ele:{s['elective']} OpenEle:{open_ele_str} Lab:{s['islab']} L-T-P:{s['l']}-{s['t']}-{s['p']}")

    def load():
        sel = listbox.curselection()
        if not sel: return
        parts = listbox.get(sel[0]).split(" | ")
        sem = parts[0].split()[1]; code = parts[1].strip()
        sub = next(s for s in data.subjects[sem] if s['code'] == code)
        sem_combo.set(sem); code_entry.delete(0, tk.END); code_entry.insert(0, sub['code'])
        name_entry.delete(0, tk.END); name_entry.insert(0, sub['name'])
        ele_combo.set(sub['elective'])
        open_ele_combo.set(sub.get('open_elective', 'no'))
        lab_combo.set(sub['islab'])
        l_entry.delete(0, tk.END); l_entry.insert(0, sub['l'])
        t_entry.delete(0, tk.END); t_entry.insert(0, sub['t'])
        p_entry.delete(0, tk.END); p_entry.insert(0, sub['p'])

    def save():
        sem = sem_combo.get(); code = code_entry.get().strip(); name = name_entry.get().strip()
        ele = ele_combo.get(); open_ele = open_ele_combo.get(); lab = lab_combo.get()
        try: l, t, p = int(l_entry.get()), int(t_entry.get()), int(p_entry.get())
        except: messagebox.showerror("Error", "L/T/P must be numbers"); return
        if not all([sem, code, name, ele, open_ele, lab]): messagebox.showerror("Error", "Fill all fields"); return
        sub = {"code": code, "name": name, "elective": ele, "open_elective": open_ele, "islab": lab, "l": l, "t": t, "p": p}
        existing = next((i for i, s in enumerate(data.subjects[sem]) if s['code'] == code), None)
        if existing is not None: data.subjects[sem][existing] = sub
        else: data.subjects[sem].append(sub)
        refresh(); data.save_to_file()
        data.save_to_file()

    def delete():
        sel = listbox.curselection()
        if not sel: return
        parts = listbox.get(sel[0]).split(" | ")
        sem = parts[0].split()[1]; code = parts[1].strip()
        data.subjects[sem] = [s for s in data.subjects[sem] if s['code'] != code]
        refresh(); data.save_to_file()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=9, column=1, pady=10)
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=load).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=5)
    listbox.bind('<Double-1>', lambda e: load())
    refresh()
