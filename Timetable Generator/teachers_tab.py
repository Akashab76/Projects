# teachers_tab.py - WITHOUT TIMINGS
import tkinter as tk
from tkinter import ttk, messagebox

def create_teachers_tab(parent, data):
    ttk.Label(parent, text="Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    name_entry = ttk.Entry(parent, width=25); name_entry.grid(row=0, column=1)
    
    ttk.Label(parent, text="Short:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    short_entry = ttk.Entry(parent, width=10); short_entry.grid(row=1, column=1)
    
    ttk.Label(parent, text="Designation:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    desig_combo = ttk.Combobox(parent, values=["Assistant Professor", "Associate Professor", "Head Professor", "Professor"], width=22)
    desig_combo.grid(row=2, column=1)
    
    ttk.Label(parent, text="Credits/Week:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    credits_spin = ttk.Spinbox(parent, from_=0, to=40, width=5); credits_spin.grid(row=3, column=1)

    listbox = tk.Listbox(parent, height=20, width=60, font=("Courier", 9))
    listbox.grid(row=0, column=2, rowspan=10, padx=10, pady=5)

    def refresh():
        listbox.delete(0, tk.END)
        for t in data.teachers:
            # Display without start_time
            listbox.insert(tk.END, f"{t['name']} ({t['short']}) | {t['desig']} | {t['credits']} cr")

    def load():
        sel = listbox.curselection()
        if not sel: return
        t = data.teachers[sel[0]]
        name_entry.delete(0, tk.END); name_entry.insert(0, t['name'])
        short_entry.delete(0, tk.END); short_entry.insert(0, t['short'])
        desig_combo.set(t['desig'])
        credits_spin.delete(0, tk.END); credits_spin.insert(0, t['credits'])

    def save():
        name = name_entry.get().strip()
        short = short_entry.get().strip()
        desig = desig_combo.get()
        
        try: 
            credits = int(credits_spin.get())
        except: 
            messagebox.showerror("Error", "Credits must be a number")
            return
        
        if not all([name, short, desig]): 
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Create teacher WITHOUT start_time
        teacher = {
            "name": name, 
            "short": short, 
            "desig": desig, 
            "credits": credits,
            "start_time": "8:00"  # Keep for backward compatibility but will be managed in Availability tab
        }
        
        sel = listbox.curselection()
        if sel: 
            data.teachers[sel[0]] = teacher
        else: 
            data.teachers.append(teacher)
        
        refresh()
        data.save_to_file()
        messagebox.showinfo("Success", f"Teacher '{short}' saved successfully!")

    def delete():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a teacher to delete")
            return
        
        teacher = data.teachers[sel[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete teacher '{teacher['short']}'?"):
            data.teachers.pop(sel[0])
            refresh()
            data.save_to_file()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=5, column=1, pady=10)
    
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=load).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=5)
    
    listbox.bind('<Double-1>', lambda e: load())
    
    # Info label
    info_frame = ttk.Frame(parent)
    info_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky='w', padx=5)
    ttk.Label(info_frame, text="ℹ️ Note: Teacher working hours and availability are now managed in the 'Availability' tab", 
             foreground='blue', wraplength=300).pack()
    
    refresh()