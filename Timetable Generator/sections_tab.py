# sections_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

def create_sections_tab(parent, data):
    ttk.Label(parent, text="Semester:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sem_combo = ttk.Combobox(parent, values=[str(i) for i in range(1,9)], width=5); sem_combo.grid(row=0, column=1)
    ttk.Label(parent, text="Section:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    sec_entry = ttk.Entry(parent, width=10); sec_entry.grid(row=1, column=1)

    listbox = tk.Listbox(parent, height=20, width=50, font=("Courier", 9)); listbox.grid(row=0, column=2, rowspan=10, padx=10, pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        for sem in data.sections:
            for sec in data.sections[sem]:
                listbox.insert(tk.END, f"Sem {sem} | {sec}")

    def load():
        sel = listbox.curselection()
        if not sel: return
        parts = listbox.get(sel[0]).split(" | ")
        sem = parts[0].split()[1]; sec = parts[1].strip()
        sem_combo.set(sem); sec_entry.delete(0, tk.END); sec_entry.insert(0, sec)

    def save():
        sem = sem_combo.get(); sec = sec_entry.get().strip()
        if not sem or not sec: messagebox.showerror("Error", "Fill all"); return
        if sec in data.sections[sem]: data.sections[sem].remove(sec)
        data.sections[sem].append(sec)
        refresh()
        data.save_to_file()

    def delete():
        sel = listbox.curselection()
        if not sel: return
        parts = listbox.get(sel[0]).split(" | ")
        sem = parts[0].split()[1]; sec = parts[1].strip()
        if sec in data.sections[sem]: data.sections[sem].remove(sec)
        data.save_to_file()
        refresh()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=2, column=1, pady=10)
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=load).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=5)
    listbox.bind('<Double-1>', lambda e: load())
    refresh()