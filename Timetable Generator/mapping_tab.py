# mapping_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

def create_mapping_tab(parent, data):
    ttk.Label(parent, text="Semester:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sem_combo = ttk.Combobox(parent, values=[str(i) for i in range(1, 9)], width=5)
    sem_combo.grid(row=0, column=1, sticky='w')
    sem_combo.bind("<<ComboboxSelected>>", lambda e: update_sections())

    ttk.Label(parent, text="Section:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    sec_combo = ttk.Combobox(parent, width=10)
    sec_combo.grid(row=1, column=1, sticky='w')
    sec_combo.bind("<<ComboboxSelected>>", lambda e: update_subjects())

    ttk.Label(parent, text="Subject:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    sub_combo = ttk.Combobox(parent, width=15)
    sub_combo.grid(row=2, column=1, sticky='w')
    sub_combo.bind("<<ComboboxSelected>>", lambda e: update_lab_fields())

    ttk.Label(parent, text="Theory Teacher:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    theory_combo = ttk.Combobox(parent, width=25)
    theory_combo.grid(row=3, column=1, sticky='w')

    # Lab teachers - 2 mandatory, 2 optional
    lab1_label = ttk.Label(parent, text="Lab Teacher 1 (Required):")
    lab1_combo = ttk.Combobox(parent, width=25)
    lab2_label = ttk.Label(parent, text="Lab Teacher 2 (Required):")
    lab2_combo = ttk.Combobox(parent, width=25)
    lab3_label = ttk.Label(parent, text="Lab Teacher 3 (Optional):")
    lab3_combo = ttk.Combobox(parent, width=25)
    lab4_label = ttk.Label(parent, text="Lab Teacher 4 (Optional):")
    lab4_combo = ttk.Combobox(parent, width=25)

    lab1_label.grid_remove(); lab1_combo.grid_remove()
    lab2_label.grid_remove(); lab2_combo.grid_remove()
    lab3_label.grid_remove(); lab3_combo.grid_remove()
    lab4_label.grid_remove(); lab4_combo.grid_remove()

    listbox = tk.Listbox(parent, height=20, width=95, font=("Courier", 9))
    listbox.grid(row=0, column=2, rowspan=12, padx=10, pady=5)

    def update_sections():
        sem = sem_combo.get()
        sec_combo['values'] = data.sections.get(sem, [])
        update_teachers()
        refresh()

    def update_subjects():
        sem = sem_combo.get()
        sub_combo['values'] = [s['code'] for s in data.subjects.get(sem, [])]
        update_lab_fields()

    def update_teachers():
        teachers = [t['short'] for t in data.teachers]
        theory_combo['values'] = teachers
        lab1_combo['values'] = teachers
        lab2_combo['values'] = teachers
        lab3_combo['values'] = teachers
        lab4_combo['values'] = teachers

    def update_lab_fields():
        sem = sem_combo.get(); sub_code = sub_combo.get()
        if not sem or not sub_code:
            hide_lab_fields(); return
        subject = next((s for s in data.subjects[sem] if s['code'] == sub_code), None)
        if subject and subject['islab'] == 'yes':
            show_lab_fields()
        else:
            hide_lab_fields()

    def show_lab_fields():
        lab1_label.grid(row=4, column=0, sticky='w', padx=5, pady=2)
        lab1_combo.grid(row=4, column=1, sticky='w')
        lab2_label.grid(row=5, column=0, sticky='w', padx=5, pady=2)
        lab2_combo.grid(row=5, column=1, sticky='w')
        lab3_label.grid(row=6, column=0, sticky='w', padx=5, pady=2)
        lab3_combo.grid(row=6, column=1, sticky='w')
        lab4_label.grid(row=7, column=0, sticky='w', padx=5, pady=2)
        lab4_combo.grid(row=7, column=1, sticky='w')

    def hide_lab_fields():
        lab1_label.grid_remove(); lab1_combo.grid_remove()
        lab2_label.grid_remove(); lab2_combo.grid_remove()
        lab3_label.grid_remove(); lab3_combo.grid_remove()
        lab4_label.grid_remove(); lab4_combo.grid_remove()

    def refresh():
        listbox.delete(0, tk.END)
        for sem in data.mappings:
            for sec in data.mappings[sem]:
                for sub, m in data.mappings[sem][sec].items():
                    lab_str = ', '.join(m['lab']) if m['lab'] else "—"
                    listbox.insert(tk.END, f"Sem {sem} | Sec {sec} | {sub:7} | Theory: {m['theory']:5} | Lab: {lab_str}")

    def load_selected():
        sel = listbox.curselection()
        if not sel: return
        parts = listbox.get(sel[0]).split(" | ")
        sem = parts[0].split()[1]; sec = parts[1].split()[1]; sub = parts[2].strip()
        sem_combo.set(sem); update_sections(); sec_combo.set(sec); update_subjects(); sub_combo.set(sub); update_lab_fields()
        m = data.mappings[sem][sec][sub]
        theory_combo.set(m['theory'])
        if m['lab']:
            lab1_combo.set(m['lab'][0] if len(m['lab']) > 0 else "")
            lab2_combo.set(m['lab'][1] if len(m['lab']) > 1 else "")
            lab3_combo.set(m['lab'][2] if len(m['lab']) > 2 else "")
            lab4_combo.set(m['lab'][3] if len(m['lab']) > 3 else "")
        else:
            lab1_combo.set(""); lab2_combo.set("")
            lab3_combo.set(""); lab4_combo.set("")

    def save():
        sem = sem_combo.get(); sec = sec_combo.get(); sub = sub_combo.get(); theory = theory_combo.get()
        if not all([sem, sec, sub, theory]):
            messagebox.showerror("Error", "Required fields missing.")
            return
        subject = next((s for s in data.subjects[sem] if s['code'] == sub), None)
        if not subject: messagebox.showerror("Error", "Subject not found."); return

        is_lab_sub = subject['islab'] == 'yes'
        lab = []
        if is_lab_sub:
            lab1 = lab1_combo.get().strip()
            lab2 = lab2_combo.get().strip()
            lab3 = lab3_combo.get().strip()
            lab4 = lab4_combo.get().strip()
            
            # Validate: Lab1 and Lab2 are REQUIRED
            if not lab1 or not lab2:
                messagebox.showerror("Error", "Lab subjects need at least Lab Teacher 1 and Lab Teacher 2.")
                return
            
            # Check Lab1 and Lab2 are different
            if lab1 == lab2:
                messagebox.showerror("Error", "Lab Teacher 1 and Lab Teacher 2 must be different.")
                return
            
            # Build lab list: always include lab1 and lab2
            lab = [lab1, lab2]
            
            # Add lab3 if provided and different from lab1 and lab2
            if lab3 and lab3 not in lab:
                lab.append(lab3)
            elif lab3 and lab3 in lab:
                messagebox.showwarning("Warning", "Lab Teacher 3 is same as Lab Teacher 1 or 2. Skipping...")
            
            # Add lab4 if provided and different from all previous
            if lab4 and lab4 not in lab:
                lab.append(lab4)
            elif lab4 and lab4 in lab:
                messagebox.showwarning("Warning", "Lab Teacher 4 is same as previous teachers. Skipping...")

        if sem not in data.mappings: data.mappings[sem] = {}
        if sec not in data.mappings[sem]: data.mappings[sem][sec] = {}
        data.mappings[sem][sec][sub] = {'theory': theory, 'lab': lab}
        refresh()
        data.save_to_file()
        
        lab_count = len(lab) if lab else 0
        if is_lab_sub and lab_count > 2:
            messagebox.showinfo("Success", f"Saved! {lab_count} lab teachers assigned (2 required + {lab_count-2} optional)")
        else:
            messagebox.showinfo("Success", "Saved!")

    def delete():
        sel = listbox.curselection()
        if not sel: return
        if messagebox.askyesno("Delete", "Remove this mapping?"):
            parts = listbox.get(sel[0]).split(" | ")
            sem = parts[0].split()[1]; sec = parts[1].split()[1]; sub = parts[2].strip()
            del data.mappings[sem][sec][sub]
            if not data.mappings[sem][sec]: del data.mappings[sem][sec]
            if not data.mappings[sem]: del data.mappings[sem]
            refresh()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=8, column=0, columnspan=2, pady=10)
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit", command=load_selected).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=5)
    
    info_label = ttk.Label(parent, 
                          text="💡 Lab Teachers: First 2 are REQUIRED, last 2 are OPTIONAL",
                          foreground="#3498db", font=("Arial", 9, "italic"))
    info_label.grid(row=9, column=0, columnspan=2, pady=5)
    
    listbox.bind('<Double-1>', lambda e: load_selected())
    update_teachers()
    refresh()