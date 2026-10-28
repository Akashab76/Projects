"""
Teacher Availability - TEACHERS TAB STYLE LAYOUT
Left: List of teachers
Right: Selected teacher's availability details
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime

class TeacherAvailabilityTab:
    def __init__(self, parent, data):
        self.data = data
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load availability data
        self.availability_data = self.load_availability()
        
        # Track currently selected teacher
        self.current_teacher = None
        
        # Auto-populate from teachers data on first load
        self.auto_populate_from_teachers()
        
        # Create UI
        self.create_ui()
    
    def load_availability(self):
        """Load teacher availability from file"""
        try:
            with open('teacher_availability.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_availability(self):
        """Save teacher availability to file"""
        try:
            with open('teacher_availability.json', 'w', encoding='utf-8') as f:
                json.dump(self.availability_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return False
    
    def auto_populate_from_teachers(self):
        """Auto-populate availability from teachers data if not already saved"""
        if not hasattr(self.data, 'teachers'):
            return
        
        for teacher in self.data.teachers:
            short = teacher.get('short')
            if not short or short in self.availability_data:
                continue  # Skip if already has data
            
            # Get start_time
            start_time = teacher.get('start_time', '9:00')
            start_12h = self.convert_to_12h(start_time)
            
            # EVERYONE ends at 5:00 PM
            end_12h = "05:00 PM"
            
            # Create default availability
            self.availability_data[short] = {
                'daily_hours': {
                    'Monday': {'start': start_12h, 'end': end_12h, 'off': False},
                    'Tuesday': {'start': start_12h, 'end': end_12h, 'off': False},
                    'Wednesday': {'start': start_12h, 'end': end_12h, 'off': False},
                    'Thursday': {'start': start_12h, 'end': end_12h, 'off': False},
                    'Friday': {'start': start_12h, 'end': end_12h, 'off': False},
                    'Saturday': {'start': start_12h, 'end': end_12h, 'off': False}
                },
                'constraints': [],
                'preference': 'No Preference',
                'max_classes': 'No Limit',
                'notes': ''
            }
        
        # Save the auto-populated data
        if self.availability_data:
            self.save_availability()
    
    def convert_to_12h(self, time_24h):
        """Convert 24-hour time to 12-hour format"""
        try:
            parts = time_24h.split(':')
            hour = int(parts[0])
            minute = parts[1] if len(parts) > 1 else "00"
            
            if hour == 0:
                return f"12:{minute} AM"
            elif hour < 12:
                return f"{hour:02d}:{minute} AM"
            elif hour == 12:
                return f"12:{minute} PM"
            else:
                return f"{hour-12:02d}:{minute} PM"
        except:
            return "09:00 AM"
    
    def create_ui(self):
        """Create left-right split layout"""
        
        # Title
        title_label = ttk.Label(self.frame, text="👨‍🏫 Teacher Availability & Constraints", 
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Main container with two columns
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill='both', expand=True)
        
        # LEFT SIDE - Teacher List
        left_frame = ttk.LabelFrame(main_container, text="📋 Teachers", padding=5)
        left_frame.pack(side='left', fill='both', expand=False, padx=(0, 5))
        
        # Teacher listbox
        self.teacher_listbox = tk.Listbox(left_frame, width=25, height=35, font=("Courier", 10))
        self.teacher_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=self.teacher_listbox.yview)
        self.teacher_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection
        self.teacher_listbox.bind('<<ListboxSelect>>', self.on_teacher_select)
        
        # Refresh teacher list
        self.refresh_teacher_list()
        
        # RIGHT SIDE - Availability Details
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Info label
        self.info_label = ttk.Label(right_frame, text="← Select a teacher to view/edit availability", 
                                    foreground='gray', font=("Arial", 10))
        self.info_label.pack(anchor='w', pady=5)
        
        # Scrollable details area
        canvas = tk.Canvas(right_frame, bg='white')
        details_scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=canvas.yview)
        self.details_frame = ttk.Frame(canvas)
        
        self.details_frame.bind('<Configure>', 
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.details_frame, anchor="nw")
        canvas.configure(yscrollcommand=details_scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
        
        # Enable mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def refresh_teacher_list(self):
        """Refresh the teacher list"""
        self.teacher_listbox.delete(0, tk.END)
        
        if not hasattr(self.data, 'teachers'):
            return
        
        for teacher in sorted(self.data.teachers, key=lambda t: t.get('short', '')):
            short = teacher.get('short', '')
            if short:
                # Check if has saved data
                status = " ✅" if short in self.availability_data else " 📝"
                self.teacher_listbox.insert(tk.END, f"{short}{status}")
    
    def on_teacher_select(self, event=None):
        """Handle teacher selection"""
        selection = self.teacher_listbox.curselection()
        if not selection:
            return
        
        # Get teacher short name
        text = self.teacher_listbox.get(selection[0])
        teacher = text.split()[0]  # Remove status emoji
        
        # Store current teacher
        self.current_teacher = teacher
        
        # Update info label
        self.info_label.config(text=f"Editing availability for: {teacher}")
        
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Show details
        self.show_teacher_details(teacher)
    
    def show_teacher_details(self, teacher):
        """Show detailed availability for selected teacher"""
        
        # Store current teacher
        self.current_teacher = teacher
        
        # Update info label
        self.info_label.config(text=f"Editing availability for: {teacher}")
        
        # Keep teacher selected in listbox
        for i in range(self.teacher_listbox.size()):
            text = self.teacher_listbox.get(i)
            if text.split()[0] == teacher:
                self.teacher_listbox.selection_clear(0, tk.END)
                self.teacher_listbox.selection_set(i)
                self.teacher_listbox.see(i)
                break
        
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        if teacher not in self.availability_data:
            ttk.Label(self.details_frame, text=f"No data for {teacher}", 
                     foreground='red').pack(pady=20)
            return
        
        data = self.availability_data[teacher]
        
        # Daily Hours Section
        hours_frame = ttk.LabelFrame(self.details_frame, text="⏰ Daily Working Hours", padding=10)
        hours_frame.pack(fill='x', padx=5, pady=5)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_hours = data.get('daily_hours', {})
        
        for day in days:
            day_data = daily_hours.get(day, {'start': '09:00 AM', 'end': '05:00 PM', 'off': False})
            
            day_frame = ttk.Frame(hours_frame)
            day_frame.pack(fill='x', pady=2)
            
            # Day label
            ttk.Label(day_frame, text=f"{day}:", width=12, anchor='w').pack(side='left', padx=5)
            
            # Show time or OFF
            if day_data.get('off'):
                ttk.Label(day_frame, text="[OFF DAY]", foreground='red', width=25).pack(side='left')
            else:
                start = day_data.get('start', '09:00 AM')
                end = day_data.get('end', '05:00 PM')
                ttk.Label(day_frame, text=f"[{start} - {end}]", width=25).pack(side='left')
            
            # Edit button
            ttk.Button(day_frame, text="✏️ Edit", width=8,
                      command=lambda t=teacher, d=day: self.edit_day(t, d)).pack(side='left', padx=2)
            
            # Delete (set to OFF) button
            ttk.Button(day_frame, text="🗑️ Set OFF", width=10,
                      command=lambda t=teacher, d=day: self.set_day_off(t, d)).pack(side='left', padx=2)
        
        # Quick Actions
        quick_frame = ttk.Frame(hours_frame)
        quick_frame.pack(fill='x', pady=10)
        
        ttk.Button(quick_frame, text="Set All: 9AM-5PM",
                  command=lambda: self.quick_set_all(teacher, "09:00 AM", "05:00 PM")).pack(side='left', padx=5)
        ttk.Button(quick_frame, text="Set All: 8AM-4PM",
                  command=lambda: self.quick_set_all(teacher, "08:00 AM", "04:00 PM")).pack(side='left', padx=5)
        
        # Constraints Section
        constraints_frame = ttk.LabelFrame(self.details_frame, text="🚫 Personal Constraints", padding=10)
        constraints_frame.pack(fill='x', padx=5, pady=5)
        
        constraints = data.get('constraints', [])
        
        if not constraints:
            ttk.Label(constraints_frame, text="No constraints defined", foreground='gray').pack(pady=5)
        else:
            for i, constraint in enumerate(constraints):
                c_frame = ttk.Frame(constraints_frame)
                c_frame.pack(fill='x', pady=2)
                
                text = f"{constraint['day']}: {constraint['start']} - {constraint['end']} ({constraint['reason']})"
                ttk.Label(c_frame, text=text, width=60).pack(side='left', padx=5)
                
                ttk.Button(c_frame, text="🗑️ Delete", width=10,
                          command=lambda t=teacher, idx=i: self.delete_constraint(t, idx)).pack(side='left', padx=2)
        
        # Add constraint button
        ttk.Button(constraints_frame, text="➕ Add Constraint",
                  command=lambda: self.add_constraint(teacher)).pack(pady=5)
        
        # Preferences Section
        prefs_frame = ttk.LabelFrame(self.details_frame, text="⭐ Preferences", padding=10)
        prefs_frame.pack(fill='x', padx=5, pady=5)
        
        pref_text = f"Time Preference: {data.get('preference', 'No Preference')}"
        ttk.Label(prefs_frame, text=pref_text).pack(anchor='w', padx=5, pady=2)
        
        max_text = f"Max Classes Per Day: {data.get('max_classes', 'No Limit')}"
        ttk.Label(prefs_frame, text=max_text).pack(anchor='w', padx=5, pady=2)
        
        notes = data.get('notes', '')
        if notes:
            ttk.Label(prefs_frame, text=f"Notes: {notes}", wraplength=400).pack(anchor='w', padx=5, pady=2)
        
        ttk.Button(prefs_frame, text="✏️ Edit Preferences",
                  command=lambda: self.edit_preferences(teacher)).pack(pady=5)
    
    def edit_day(self, teacher, day):
        """Edit a specific day's hours"""
        if teacher not in self.availability_data:
            return
        
        data = self.availability_data[teacher]
        day_data = data['daily_hours'].get(day, {'start': '09:00 AM', 'end': '05:00 PM', 'off': False})
        
        # Create dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"Edit {day} for {teacher}")
        dialog.geometry("350x220")  # Increased from 200 to 220
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Set working hours for {day}", 
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        # Start time
        start_frame = ttk.Frame(dialog)
        start_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(start_frame, text="Start Time:").pack(side='left')
        start_var = tk.StringVar(value=day_data.get('start', '09:00 AM'))
        start_combo = ttk.Combobox(start_frame, textvariable=start_var,
                                   values=self.get_time_slots(), width=12, state='readonly')
        start_combo.pack(side='right')
        
        # End time
        end_frame = ttk.Frame(dialog)
        end_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(end_frame, text="End Time:").pack(side='left')
        end_var = tk.StringVar(value=day_data.get('end', '05:00 PM'))
        end_combo = ttk.Combobox(end_frame, textvariable=end_var,
                                 values=self.get_time_slots(), width=12, state='readonly')
        end_combo.pack(side='right')
        
        # Off day checkbox
        off_frame = ttk.Frame(dialog)
        off_frame.pack(fill='x', padx=20, pady=5)
        off_var = tk.BooleanVar(value=day_data.get('off', False))
        ttk.Checkbutton(off_frame, text="Mark as OFF day", variable=off_var).pack(anchor='w')
        
        def save_day():
            data['daily_hours'][day] = {
                'start': start_var.get(),
                'end': end_var.get(),
                'off': off_var.get()
            }
            self.save_availability()
            self.show_teacher_details(teacher)  # Instant refresh!
            dialog.destroy()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="💾 Save", command=save_day).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def set_day_off(self, teacher, day):
        """Set a day as OFF"""
        if teacher not in self.availability_data:
            return
        
        self.availability_data[teacher]['daily_hours'][day]['off'] = True
        self.save_availability()
        self.show_teacher_details(teacher)  # Instant refresh!
    
    def quick_set_all(self, teacher, start, end):
        """Set all days to same hours"""
        if teacher not in self.availability_data:
            return
        
        for day in self.availability_data[teacher]['daily_hours']:
            self.availability_data[teacher]['daily_hours'][day] = {
                'start': start,
                'end': end,
                'off': False
            }
        
        self.save_availability()
        self.show_teacher_details(teacher)  # Instant refresh!
    
    def add_constraint(self, teacher):
        """Add a constraint"""
        if teacher not in self.availability_data:
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"Add Constraint for {teacher}")
        dialog.geometry("400x280")  # Increased from 250 to 280
        dialog.grab_set()
        
        ttk.Label(dialog, text="Add Personal Constraint", 
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        # Day
        day_frame = ttk.Frame(dialog)
        day_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(day_frame, text="Day:").pack(side='left')
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(day_frame, textvariable=day_var,
                                values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'All Days'],
                                width=15, state='readonly')
        day_combo.pack(side='right')
        day_combo.current(0)
        
        # Start time
        start_frame = ttk.Frame(dialog)
        start_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(start_frame, text="Start Time:").pack(side='left')
        start_var = tk.StringVar(value="12:00 PM")
        start_combo = ttk.Combobox(start_frame, textvariable=start_var,
                                   values=self.get_time_slots(), width=12, state='readonly')
        start_combo.pack(side='right')
        
        # End time
        end_frame = ttk.Frame(dialog)
        end_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(end_frame, text="End Time:").pack(side='left')
        end_var = tk.StringVar(value="01:00 PM")
        end_combo = ttk.Combobox(end_frame, textvariable=end_var,
                                 values=self.get_time_slots(), width=12, state='readonly')
        end_combo.pack(side='right')
        
        # Reason
        reason_frame = ttk.Frame(dialog)
        reason_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(reason_frame, text="Reason:").pack(side='left')
        reason_var = tk.StringVar()
        ttk.Entry(reason_frame, textvariable=reason_var, width=25).pack(side='right')
        
        # Status label
        status_label = ttk.Label(dialog, text="", foreground="green", font=("Arial", 9, "bold"))
        status_label.pack(pady=5)
        
        def save_constraint():
            day = day_var.get()
            start = start_var.get()
            end = end_var.get()
            reason = reason_var.get()
            
            if not all([day, start, end, reason]):
                status_label.config(text="⚠️ Please fill all fields", foreground="red")
                return
            
            if day == "All Days":
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            else:
                days = [day]
            
            for d in days:
                self.availability_data[teacher]['constraints'].append({
                    'day': d,
                    'start': start,
                    'end': end,
                    'reason': reason
                })
            
            self.save_availability()
            self.show_teacher_details(teacher)  # Instant refresh!
            
            # Clear fields for next constraint
            day_combo.current(0)
            start_var.set("12:00 PM")
            end_var.set("01:00 PM")
            reason_var.set("")
            
            # Show success status
            status_label.config(text="✅ Constraint added! Add another or close.", foreground="green")
            # Don't destroy dialog - keep it open!
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="💾 Save", command=save_constraint).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def delete_constraint(self, teacher, index):
        """Delete a constraint"""
        if teacher not in self.availability_data:
            return
        
        if messagebox.askyesno("Confirm", "Delete this constraint?"):
            self.availability_data[teacher]['constraints'].pop(index)
            self.save_availability()
            self.show_teacher_details(teacher)  # Instant refresh!
    
    def edit_preferences(self, teacher):
        """Edit preferences"""
        if teacher not in self.availability_data:
            return
        
        data = self.availability_data[teacher]
        
        # Create dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"Edit Preferences for {teacher}")
        dialog.geometry("450x320")  # Increased height from 250 to 320
        dialog.grab_set()
        
        ttk.Label(dialog, text="Teaching Preferences", 
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        # Time preference
        pref_frame = ttk.Frame(dialog)
        pref_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(pref_frame, text="Time Preference:").pack(side='left')
        pref_var = tk.StringVar(value=data.get('preference', 'No Preference'))
        pref_combo = ttk.Combobox(pref_frame, textvariable=pref_var,
                                  values=["No Preference", "Prefer Before Lunch", 
                                         "Prefer After Lunch", "Prefer Early Morning"],
                                  width=30, state='readonly')
        pref_combo.pack(side='right')
        
        # Max classes
        max_frame = ttk.Frame(dialog)
        max_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(max_frame, text="Max Classes Per Day:").pack(side='left')
        max_var = tk.StringVar(value=data.get('max_classes', 'No Limit'))
        max_combo = ttk.Combobox(max_frame, textvariable=max_var,
                                values=["No Limit", "1", "2", "3", "4", "5", "6"],
                                width=15, state='readonly')
        max_combo.pack(side='right')
        
        # Notes
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(notes_frame, text="Notes:").pack(anchor='w')
        notes_text = tk.Text(notes_frame, height=4, width=50)
        notes_text.pack()
        notes_text.insert('1.0', data.get('notes', ''))
        
        def save_prefs():
            data['preference'] = pref_var.get()
            data['max_classes'] = max_var.get()
            data['notes'] = notes_text.get('1.0', 'end').strip()
            
            self.save_availability()
            self.show_teacher_details(teacher)  # Instant refresh!
            dialog.destroy()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="💾 Save", command=save_prefs).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def get_time_slots(self):
        """Generate time slots every 15 minutes"""
        slots = []
        for hour in range(7, 22):
            for minute in ['00', '15', '30', '45']:  # Changed from just '00', '30'
                h = hour if hour <= 12 else hour - 12
                h = 12 if h == 0 else h
                ampm = "AM" if hour < 12 else "PM"
                slots.append(f"{h:02d}:{minute} {ampm}")
        return slots

def create_availability_tab(parent, data):
    """Create and return the availability tab"""
    tab_manager = TeacherAvailabilityTab(parent, data)
    return tab_manager.frame