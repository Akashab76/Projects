# teacher_timetable_tab.py - SIMPLE VERSION
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
from teacher_timetable_generator_simple import generate_teacher_timetables_simple

def create_teacher_timetable_tab(parent, data):
    """Tab for generating teacher timetables - SIMPLE VERSION"""
    
    # Header
    header = ttk.Label(parent, 
                      text="👨‍🏫 Teacher Timetables (All Semesters)",
                      font=("Arial", 18, "bold"),
                      foreground="#2c3e50")
    header.pack(pady=20)
    
    # Info label
    info = ttk.Label(parent,
                    text="Generate combined timetables showing each teacher's schedule across ALL semesters (3, 5, 7)",
                    font=("Arial", 11),
                    foreground="#7f8c8d")
    info.pack(pady=10)
    
    # Important warning
    warning_frame = ttk.Frame(parent)
    warning_frame.pack(pady=15)
    
    warning = ttk.Label(warning_frame,
                       text="⚠️ IMPORTANT: Generate section timetables FIRST (in Generate tab)!",
                       font=("Arial", 12, "bold"),
                       foreground="#e74c3c",
                       background="#ffe6e6",
                       padding=15)
    warning.pack()
    
    # Controls frame
    controls_frame = ttk.LabelFrame(parent, text="  Generate Options  ", padding=20)
    controls_frame.pack(pady=20, padx=40, fill='x')
    
    # Teacher selection
    teacher_var = tk.StringVar(value="all")
    
    # All teachers radio
    all_frame = ttk.Frame(controls_frame)
    all_frame.pack(pady=10, fill='x')
    
    all_radio = ttk.Radiobutton(all_frame, 
                                text="All Teachers",
                                variable=teacher_var,
                                value="all")
    all_radio.pack(side=tk.LEFT, padx=5)
    
    all_desc = ttk.Label(all_frame,
                        text="(generates timetables for every teacher)",
                        font=("Arial", 9, "italic"),
                        foreground="#7f8c8d")
    all_desc.pack(side=tk.LEFT, padx=10)
    
    # Specific teacher radio
    specific_frame = ttk.Frame(controls_frame)
    specific_frame.pack(pady=10, fill='x')
    
    specific_radio = ttk.Radiobutton(specific_frame,
                                    text="Specific Teacher:",
                                    variable=teacher_var,
                                    value="specific")
    specific_radio.pack(side=tk.LEFT, padx=5)
    
    teacher_combo = ttk.Combobox(specific_frame, width=25, font=("Arial", 10))
    teacher_combo.pack(side=tk.LEFT, padx=10)
    
    def update_teacher_list():
        """Update teacher dropdown"""
        teacher_names = [t['short'] for t in data.teachers]
        teacher_combo['values'] = teacher_names
        if teacher_names:
            teacher_combo.set(teacher_names[0])
    
    update_teacher_list()
    
    # Status label
    status_label = ttk.Label(parent, text="", font=("Arial", 11, "bold"))
    status_label.pack(pady=15)
    
    # Progress bar
    progress = ttk.Progressbar(parent, length=500, mode='indeterminate')
    
    def generate():
        """Generate teacher timetables"""
        
        # Show progress
        status_label.config(text="🔄 Generating teacher timetables...", foreground="#3498db")
        progress.pack(pady=10)
        progress.start(10)
        parent.update()
        
        try:
            # Determine which teacher
            specific_teacher = None
            if teacher_var.get() == "specific":
                specific_teacher = teacher_combo.get()
                if not specific_teacher:
                    progress.stop()
                    progress.pack_forget()
                    messagebox.showerror("Error", "Please select a teacher!")
                    status_label.config(text="", foreground="#e74c3c")
                    return
            
            # Generate timetables
            result = generate_teacher_timetables_simple(specific_teacher)
            
            progress.stop()
            progress.pack_forget()
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                status_label.config(
                    text=f"❌ {error_msg}",
                    foreground="#e74c3c"
                )
                messagebox.showerror("Error", 
                                    f"{error_msg}\n\n"
                                    "Please:\n"
                                    "1. Go to 'Generate' tab\n"
                                    "2. Generate timetables for Semesters 3, 5, and 7\n"
                                    "3. Then come back here and try again")
                return
            
            # Save HTML
            filename = "teacher_timetables_ALL_SEMESTERS.html"
            if specific_teacher:
                filename = f"teacher_timetable_{specific_teacher}_ALL_SEMESTERS.html"
            
            filepath = os.path.abspath(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result["html"])
            
            # Success!
            teacher_count = result.get("teacher_count", 0)
            
            if specific_teacher:
                status_label.config(
                    text=f"✅ Timetable generated for {specific_teacher}!",
                    foreground="#27ae60"
                )
                messagebox.showinfo("Success!", 
                                  f"Teacher timetable generated for {specific_teacher}!\n\n"
                                  f"Combined schedule from all semesters (3, 5, 7)\n\n"
                                  f"File: {filename}\n\n"
                                  f"Opening in your browser...")
            else:
                status_label.config(
                    text=f"✅ Timetables generated for {teacher_count} teachers!",
                    foreground="#27ae60"
                )
                messagebox.showinfo("Success!", 
                                  f"Teacher timetables generated for {teacher_count} teachers!\n\n"
                                  f"Combined schedules from all semesters (3, 5, 7)\n\n"
                                  f"File: {filename}\n\n"
                                  f"Opening in your browser...")
            
            # Open in browser
            webbrowser.open(f'file://{filepath}')
        
        except Exception as e:
            progress.stop()
            progress.pack_forget()
            status_label.config(text=f"❌ Error: {str(e)}", foreground="#e74c3c")
            messagebox.showerror("Error", 
                                f"An error occurred:\n\n{str(e)}\n\n"
                                f"Make sure you've generated section timetables first!")
    
    # Generate button
    button_frame = ttk.Frame(parent)
    button_frame.pack(pady=25)
    
    generate_btn = ttk.Button(button_frame, 
                             text="🎯 Generate Teacher Timetables",
                             command=generate,
                             width=35)
    generate_btn.pack()
    
    # Instructions
    instructions = ttk.LabelFrame(parent, text="  📋 How to Use  ", padding=20)
    instructions.pack(pady=20, padx=40, fill='both', expand=True)
    
    inst_text = """
    STEP 1: Generate section timetables FIRST (if you haven't already)
            • Go to "Generate" tab
            • Generate for Semester 3, 5, and 7
            • This creates the data file that teacher timetables read from
    
    STEP 2: Come back here and choose:
            • "All Teachers" → generates for every teacher in your system
            • "Specific Teacher" → generates for just one teacher
    
    STEP 3: Click "Generate Teacher Timetables"
    
    STEP 4: HTML file opens in your browser showing:
            • Combined schedule from ALL semesters (3, 5, 7)
            • Organized by day (Monday-Saturday)
            • Each class shows: Time, Subject, Semester, Section, Room
            • Color-coded: Blue=Theory, Purple=Lab, Green=Open Elective
            • Total statistics at the top
    
    💡 Example Output:
    
        KKR
        📚 15 Theory | 🔬 3 Lab | 🌟 2 Open Elective | ⏰ 20 Total
        
        📅 Monday
          ⏰ 11:15-12:10   📖 COA    [Sem 3] Section: S3-A   🏫 CR-506
          ⏰ 13:05-14:00   📖 DBM    [Sem 5] Section: S5-B   🏫 CR-601
        
        📅 Tuesday
          ⏰ 08:55-10:45   🔬 COA Lab [Sem 3] Section: S3-C  🏫 LAB-301
          ...
    
    ✨ Benefits:
        • Teachers see their complete weekly schedule
        • Admin can identify workload imbalances
        • Shows which semesters each teacher is teaching in
        • Professional, print-ready format
    """
    
    inst_label = ttk.Label(instructions, 
                          text=inst_text,
                          justify=tk.LEFT,
                          font=("Courier New", 9),
                          foreground="#2c3e50")
    inst_label.pack()