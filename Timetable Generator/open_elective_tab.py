# open_elective_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

def create_open_elective_tab(parent, data):
    ttk.Label(parent, text="Semester:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    sem_combo = ttk.Combobox(parent, values=[str(i) for i in range(1, 9)], width=5)
    sem_combo.grid(row=0, column=1, sticky='w')
    sem_combo.bind("<<ComboboxSelected>>", lambda e: update_sections_and_subjects())

    ttk.Label(parent, text="Section:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    sec_combo = ttk.Combobox(parent, width=10)
    sec_combo.grid(row=1, column=1, sticky='w')
    sec_combo.bind("<<ComboboxSelected>>", lambda e: update_subject_info())

    ttk.Label(parent, text="Open Elective:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    oe_combo = ttk.Combobox(parent, width=20)
    oe_combo.grid(row=2, column=1, sticky='w')
    oe_combo.bind("<<ComboboxSelected>>", lambda e: update_subject_info())

    # Status label showing slots scheduled vs needed (based on L value)
    status_label = ttk.Label(parent, text="", foreground="#e74c3c", font=("Arial", 10, "bold"))
    status_label.grid(row=3, column=0, columnspan=2, pady=5)

    ttk.Label(parent, text="Day:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
    day_combo = ttk.Combobox(parent, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], width=12)
    day_combo.grid(row=4, column=1, sticky='w')
    day_combo.bind("<<ComboboxSelected>>", lambda e: update_slots())

    ttk.Label(parent, text="Time Slot:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
    slot_combo = ttk.Combobox(parent, width=15)
    slot_combo.grid(row=5, column=1, sticky='w')

    ttk.Label(parent, text="Room:").grid(row=6, column=0, sticky='w', padx=5, pady=2)
    room_combo = ttk.Combobox(parent, width=15)
    room_combo.grid(row=6, column=1, sticky='w')

    listbox = tk.Listbox(parent, height=20, width=100, font=("Courier", 9))
    listbox.grid(row=0, column=2, rowspan=12, padx=10, pady=5)

    def get_slots_needed(sem, oe_code):
        """Get number of slots needed based on L (Lecture hours) from L-T-P"""
        sub = next((s for s in data.subjects.get(sem, []) if s['code'] == oe_code), None)
        if sub:
            return sub.get('l', 0)
        return 0

    def get_scheduled_count(sem, sec, oe_code):
        """Get how many slots are already scheduled"""
        if sem not in data.open_elective_schedule:
            return 0
        if sec not in data.open_elective_schedule[sem]:
            return 0
        if oe_code not in data.open_elective_schedule[sem][sec]:
            return 0
        return len(data.open_elective_schedule[sem][sec][oe_code])

    def update_subject_info():
        """Update status label showing slots scheduled vs needed"""
        sem = sem_combo.get()
        sec = sec_combo.get()
        oe_code = oe_combo.get()
        
        if not all([sem, sec, oe_code]):
            status_label.config(text="")
            return
        
        needed = get_slots_needed(sem, oe_code)
        scheduled = get_scheduled_count(sem, sec, oe_code)
        
        if needed == 0:
            status_label.config(
                text=f"⚠ This subject has L=0 (no lecture slots needed)",
                foreground="#e67e22"
            )
        elif scheduled < needed:
            status_label.config(
                text=f"⚠ Scheduled: {scheduled}/{needed} slots (Need {needed - scheduled} more) [L={needed}]",
                foreground="#e74c3c"
            )
        elif scheduled == needed:
            status_label.config(
                text=f"✓ Complete: {scheduled}/{needed} slots scheduled [L={needed}]",
                foreground="#27ae60"
            )
        else:
            status_label.config(
                text=f"⚠ Warning: {scheduled}/{needed} slots (Too many!) [L={needed}]",
                foreground="#e67e22"
            )

    def update_sections_and_subjects():
        sem = sem_combo.get()
        sec_combo['values'] = data.sections.get(sem, [])
        
        # Get open electives for this semester
        open_electives = [s['code'] for s in data.subjects.get(sem, []) if s.get('open_elective') == 'yes']
        oe_combo['values'] = open_electives
        
        # Update room list
        room_combo['values'] = [r['name'] for r in data.classrooms]
        
        update_subject_info()

    def update_slots():
        sem = sem_combo.get()
        sec = sec_combo.get()
        day = day_combo.get()
        
        if not sem or not sec or not day:
            return
        
        # Get time slots for this section and day
        cfg = data.timings.get(sem, {}).get(sec, {}).get(day)
        if not cfg:
            slot_combo['values'] = []
            return
        
        # Calculate available slots
        from utils import parse_time, min_to_time
        current = parse_time(cfg["start_time"])
        duration = cfg["class_dur"]
        num = cfg["num_classes"]
        breaks = cfg.get("breaks", [])
        
        slots = []
        for i in range(num):
            for brk in breaks:
                bs = parse_time(brk["start"])
                be = parse_time(brk["end"])
                if bs <= current < be:
                    current = be
            slot_start = min_to_time(current)
            slot_end = min_to_time(current + duration)
            slots.append(f"Slot {i+1}: {slot_start}-{slot_end}")
            current += duration
        
        slot_combo['values'] = slots

    def refresh():
        listbox.delete(0, tk.END)
        for sem in data.open_elective_schedule:
            for sec in data.open_elective_schedule[sem]:
                for oe_code, slot_list in data.open_elective_schedule[sem][sec].items():
                    needed = get_slots_needed(sem, oe_code)
                    scheduled = len(slot_list)
                    status = f"[{scheduled}/{needed}]"
                    
                    for idx, schedule_info in enumerate(slot_list):
                        day = schedule_info['day']
                        slot = schedule_info['slot_index']
                        room = schedule_info['room']
                        listbox.insert(tk.END, f"Sem {sem} | Sec {sec} | {oe_code} {status} | #{idx+1}: {day} Slot {slot+1} | Room: {room}")
        
        update_subject_info()

    def load_selected():
        sel = listbox.curselection()
        if not sel: return
        
        line = listbox.get(sel[0])
        parts = line.split(" | ")
        sem = parts[0].split()[1]
        sec = parts[1].split()[1]
        
        oe_part = parts[2].strip()
        oe_code = oe_part.split()[0]
        
        slot_info = parts[3].strip()
        slot_num = int(slot_info.split(":")[0].replace("#", "")) - 1
        
        sem_combo.set(sem)
        update_sections_and_subjects()
        sec_combo.set(sec)
        oe_combo.set(oe_code)
        update_subject_info()
        
        schedule_info = data.open_elective_schedule[sem][sec][oe_code][slot_num]
        day_combo.set(schedule_info['day'])
        update_slots()
        
        slot_idx = schedule_info['slot_index']
        slot_values = list(slot_combo['values'])
        if slot_idx < len(slot_values):
            slot_combo.set(slot_values[slot_idx])
        
        room_combo.set(schedule_info['room'])

    def save():
        sem = sem_combo.get()
        sec = sec_combo.get()
        oe_code = oe_combo.get()
        day = day_combo.get()
        slot_str = slot_combo.get()
        room = room_combo.get()
        
        if not all([sem, sec, oe_code, day, slot_str, room]):
            messagebox.showerror("Error", "Fill all fields")
            return
        
        try:
            slot_index = int(slot_str.split(":")[0].split()[1]) - 1
        except:
            messagebox.showerror("Error", "Invalid slot format")
            return
        
        # Check for duplicate day+slot
        if sem in data.open_elective_schedule:
            if sec in data.open_elective_schedule[sem]:
                if oe_code in data.open_elective_schedule[sem][sec]:
                    for existing in data.open_elective_schedule[sem][sec][oe_code]:
                        if existing['day'] == day and existing['slot_index'] == slot_index:
                            messagebox.showerror("Error", f"This slot is already scheduled for {oe_code}!\nChoose a different day or time slot.")
                            return
        
        # Initialize nested dicts
        if sem not in data.open_elective_schedule:
            data.open_elective_schedule[sem] = {}
        if sec not in data.open_elective_schedule[sem]:
            data.open_elective_schedule[sem][sec] = {}
        if oe_code not in data.open_elective_schedule[sem][sec]:
            data.open_elective_schedule[sem][sec][oe_code] = []
        
        # Add slot
        data.open_elective_schedule[sem][sec][oe_code].append({
            'day': day,
            'slot_index': slot_index,
            'room': room
        })
        
        refresh(); data.save_to_file()
        
        needed = get_slots_needed(sem, oe_code)
        scheduled = len(data.open_elective_schedule[sem][sec][oe_code])
        
        if scheduled < needed:
            messagebox.showinfo("Success", f"Slot added! Need {needed - scheduled} more slot(s) for {oe_code} (L={needed})")
        elif scheduled == needed:
            messagebox.showinfo("Complete!", f"All {needed} slots scheduled for {oe_code}! ✓ (L={needed})")
        else:
            messagebox.showwarning("Warning", f"You've scheduled {scheduled} slots but only need {needed} (L={needed})")

    def delete():
        sel = listbox.curselection()
        if not sel: return
        
        if messagebox.askyesno("Delete", "Remove this slot?"):
            line = listbox.get(sel[0])
            parts = line.split(" | ")
            sem = parts[0].split()[1]
            sec = parts[1].split()[1]
            
            oe_part = parts[2].strip()
            oe_code = oe_part.split()[0]
            
            slot_info = parts[3].strip()
            slot_num = int(slot_info.split(":")[0].replace("#", "")) - 1
            
            data.open_elective_schedule[sem][sec][oe_code].pop(slot_num)
            
            if not data.open_elective_schedule[sem][sec][oe_code]:
                del data.open_elective_schedule[sem][sec][oe_code]
            if not data.open_elective_schedule[sem][sec]:
                del data.open_elective_schedule[sem][sec]
            if not data.open_elective_schedule[sem]:
                del data.open_elective_schedule[sem]
            
            refresh(); data.save_to_file()

    button_frame = ttk.Frame(parent)
    button_frame.grid(row=7, column=0, columnspan=2, pady=10)
    ttk.Button(button_frame, text="Add/Update Slot", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Edit Slot", command=load_selected).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Delete Slot", command=delete).grid(row=0, column=2, padx=5)
    
    info_label = ttk.Label(parent, 
                          text="⚡ Slots needed = L value from L-T-P\n"
                               "Example: L=3 means you need to schedule 3 separate slots",
                          foreground="#16a085", font=("Arial", 10, "italic"))
    info_label.grid(row=8, column=0, columnspan=2, pady=10)
    
    listbox.bind('<Double-1>', lambda e: load_selected())
    refresh()