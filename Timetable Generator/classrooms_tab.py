# classrooms_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

def create_classrooms_tab(parent, data):
    ttk.Label(parent, text="Room Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    name_entry = ttk.Entry(parent, width=20); name_entry.grid(row=0, column=1)
    ttk.Label(parent, text="Is Lab:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    islab_combo = ttk.Combobox(parent, values=["yes", "no"], width=5); islab_combo.grid(row=1, column=1)

    listbox = tk.Listbox(parent, height=20, width=50, font=("Courier", 9)); listbox.grid(row=0, column=2, rowspan=10, padx=10, pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        for c in data.classrooms:
            listbox.insert(tk.END, f"{c['name']} | Lab: {c['is_lab']}")

    def load():
        sel = listbox.curselection()
        if not sel: return
        c = data.classrooms[sel[0]]
        name_entry.delete(0, tk.END); name_entry.insert(0, c['name'])
        islab_combo.set(c['is_lab'])

    def save():
        name = name_entry.get().strip(); islab = islab_combo.get()
        if not name or not islab: messagebox.showerror("Error", "Fill all"); return
        room = {"name": name, "is_lab": islab}
        existing = next((i for i, c in enumerate(data.classrooms) if c['name'] == name), None)
        if existing is not None: data.classrooms[existing] = room
        else: data.classrooms.append(room)
        refresh()
        data.save_to_file()

    def delete():
        sel = listbox.curselection()
        data.save_to_file()
        if sel: data.classrooms.pop(sel[0]); refresh()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=2, column=1, pady=10)
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=load).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=5)
    listbox.bind('<Double-1>', lambda e: load())
    refresh()