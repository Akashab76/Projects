# timings_tab.py - Updated with correct break times
import tkinter as tk
from tkinter import ttk, messagebox

def create_timings_tab(parent, data):
    ttk.Label(parent, text="Semester:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sem_combo = ttk.Combobox(parent, values=[str(i) for i in range(1,9)], width=5)
    sem_combo.grid(row=0, column=1)
    sem_combo.bind("<<ComboboxSelected>>", lambda e: update_sections())

    ttk.Label(parent, text="Section:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    sec_combo = ttk.Combobox(parent, width=10)
    sec_combo.grid(row=1, column=1)

    ttk.Label(parent, text="Day:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    day_combo = ttk.Combobox(parent, values=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], width=12)
    day_combo.grid(row=2, column=1)

    ttk.Label(parent, text="Start Time (HH:MM):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    start_entry = ttk.Entry(parent, width=10); start_entry.grid(row=3, column=1); start_entry.insert(0, "11:15")

    ttk.Label(parent, text="Class Duration (min):").grid(row=4, column=0, sticky='w', padx=5, pady=2)
    dur_entry = ttk.Entry(parent, width=5); dur_entry.grid(row=4, column=1); dur_entry.insert(0, "55")

    ttk.Label(parent, text="No. of Classes:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
    num_entry = ttk.Entry(parent, width=5); num_entry.grid(row=5, column=1); num_entry.insert(0, "6")

    # Global break info
    info = ttk.Label(parent, text="GLOBAL BREAKS (Automatic):\n"
                                 "Sem 3: Tea 10:45-11:15, Lunch 13:05-14:00\n"
                                 "Sem 5: Lunch 14:00-14:55 (no tea break)\n"
                                 "Sem 7: Tea 10:45-11:15, Lunch 14:00-14:55",
                     foreground="#d35400", font=("Arial", 11, "bold"), justify="left")
    info.grid(row=6, column=0, columnspan=2, pady=20, sticky='w')

    listbox = tk.Listbox(parent, height=22, width=100, font=("Courier", 9))
    listbox.grid(row=0, column=2, rowspan=15, padx=10, pady=5)

    def get_global_breaks(sem_str: str):
        sem = int(sem_str)
        breaks = []
        if sem == 3:
            # Sem 3: Tea 10:45-11:15, Lunch 13:05-14:00
            breaks.append({"start": "10:45", "end": "11:15"})
            breaks.append({"start": "13:05", "end": "14:00"})
        elif sem == 7:
            # Sem 7: Tea 10:45-11:15, Lunch 14:00-14:55
            breaks.append({"start": "10:45", "end": "11:15"})
            breaks.append({"start": "14:00", "end": "14:55"})
        elif sem == 5:
            # Sem 5: Only Lunch 14:00-14:55 (no tea break, starts at 11:15)
            breaks.append({"start": "14:00", "end": "14:55"})
        return breaks

    def update_sections():
        sem = sem_combo.get()
        sec_combo['values'] = data.sections.get(sem, [])
        if sem == "5":
            start_entry.delete(0, tk.END); start_entry.insert(0, "11:15")
        else:
            start_entry.delete(0, tk.END); start_entry.insert(0, "8:00")

    def refresh():
        listbox.delete(0, tk.END)
        for sem in sorted(data.timings.keys()):
            for sec in sorted(data.timings[sem]):
                for day in data.timings[sem][sec]:
                    t = data.timings[sem][sec][day]
                    breaks_str = '; '.join([f"{b['start']}-{b['end']}" for b in t.get('breaks', [])]) or 'none'
                    listbox.insert(tk.END, f"Sem {sem} | Sec {sec} | {day:<9} | Start {t['start_time']} | Dur {t['class_dur']} Classes {t['num_classes']} | Breaks -> {breaks_str}")

    def load():
        sel = listbox.curselection()
        if not sel: return
        line = listbox.get(sel[0])
        parts = line.split(" | ")
        sem = parts[0].split()[1]
        sec = parts[1].split()[1]
        day = parts[2].strip()

        sem_combo.set(sem)
        update_sections()
        sec_combo.set(sec)
        day_combo.set(day)
        t = data.timings[sem][sec][day]
        start_entry.delete(0, tk.END); start_entry.insert(0, t['start_time'])
        dur_entry.delete(0, tk.END); dur_entry.insert(0, t['class_dur'])
        num_entry.delete(0, tk.END); num_entry.insert(0, t['num_classes'])

    def save():
        sem = sem_combo.get()
        sec = sec_combo.get()
        day = day_combo.get()
        start = start_entry.get().strip()

        if not all([sem, sec, day]):
            messagebox.showerror("Error", "Fill Semester, Section, Day")
            return

        try:
            dur = int(dur_entry.get())
            num = int(num_entry.get())
            h, m = map(int, start.split(':'))
        except:
            messagebox.showerror("Error", "Invalid format")
            return

        if sem not in data.timings:
            data.timings[sem] = {}
        if sec not in data.timings[sem]:
            data.timings[sem][sec] = {}

        data.timings[sem][sec][day] = {
            'start_time': start,
            'class_dur': dur,
            'num_classes': num,
            'breaks': get_global_breaks(sem)
        }
        refresh()
        data.save_to_file()
        messagebox.showinfo("Success", f"Timing saved with correct global breaks!")

    def delete():
        sel = listbox.curselection()
        if not sel: return
        if messagebox.askyesno("Delete", "Remove this timing?"):
            line = listbox.get(sel[0])
            parts = line.split(" | ")
            sem = parts[0].split()[1]
            sec = parts[1].split()[1]
            day = parts[2].strip()
            del data.timings[sem][sec][day]
            if not data.timings[sem][sec]:
                del data.timings[sem][sec]
            if not data.timings[sem]:
                del data.timings[sem]
            refresh()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=10, column=0, columnspan=2, pady=15)
    ttk.Button(button_frame, text="Add / Update", command=save).grid(row=0, column=0, padx=8)
    ttk.Button(button_frame, text="Edit", command=load).grid(row=0, column=1, padx=8)
    ttk.Button(button_frame, text="Delete", command=delete).grid(row=0, column=2, padx=8)
    listbox.bind('<Double-1>', lambda e: load())
    refresh()