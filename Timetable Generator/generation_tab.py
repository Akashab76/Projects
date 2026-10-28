# generation_tab.py - CLEAN VERSION (Section Timetables Only)
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import tempfile
from scheduler import generate_timetable
import schedule_storage

def create_generation_tab(parent, data):
    """Create the generation tab for section timetables"""
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=15, pady=15)

    # Title
    title = ttk.Label(frame, text="Generate Timetables", font=("Arial", 18, "bold"))
    title.pack(pady=15)

    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    def show_html(html_content):
        """Show HTML in browser"""
        if not html_content.strip():
            html_content = "<h2>No timetable generated</h2>"
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        webbrowser.open('file://' + os.path.realpath(temp_path))

    # SECTION TIMETABLES
    def generate_sem3():
        """Generate Semester 3 timetable"""
        result = generate_timetable(data, "3")
        if result.get("success"):
            # SAVE the schedule for later use (for teacher timetables)
            schedule_storage.save_schedule("3", result.get("schedule", {}), 
                                          result.get("time_slots", {}),
                                          result.get("sections", []),
                                          result.get("days", []))
            messagebox.showinfo("Success", "✅ Semester 3 timetable generated successfully!")
        else:
            messagebox.showerror("Failed", "❌ Failed to generate Semester 3 timetable after 5 attempts.\n\nJust click the button again - it will likely work on the next try!")
        show_html(result.get("html", "<h2>No data for Sem 3</h2>"))

    def generate_sem5():
        """Generate Semester 5 timetable"""
        result = generate_timetable(data, "5")
        if result.get("success"):
            # SAVE the schedule for later use (for teacher timetables)
            schedule_storage.save_schedule("5", result.get("schedule", {}), 
                                          result.get("time_slots", {}),
                                          result.get("sections", []),
                                          result.get("days", []))
            messagebox.showinfo("Success", "✅ Semester 5 timetable generated successfully!")
        else:
            messagebox.showerror("Failed", "❌ Failed to generate Semester 5 timetable after 5 attempts.\n\nJust click the button again - it will likely work on the next try!")
        show_html(result.get("html", "<h2>No data for Sem 5</h2>"))

    def generate_sem7():
        """Generate Semester 7 timetable"""
        result = generate_timetable(data, "7")
        if result.get("success"):
            # SAVE the schedule for later use (for teacher timetables)
            schedule_storage.save_schedule("7", result.get("schedule", {}), 
                                          result.get("time_slots", {}),
                                          result.get("sections", []),
                                          result.get("days", []))
            messagebox.showinfo("Success", "✅ Semester 7 timetable generated successfully!")
        else:
            messagebox.showerror("Failed", "❌ Failed to generate Semester 7 timetable after 5 attempts.\n\nJust click the button again - it will likely work on the next try!")
        show_html(result.get("html", "<h2>No data for Sem 7</h2>"))

    def generate_all():
        """Generate all semester timetables in one page"""
        full_html = """<html><head><title>Complete Timetable - All Semesters</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 40px; }
            h1 { background: #c0392b; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
            h2 { background: #8e44ad; color: white; padding: 15px; border-radius: 8px; margin-top: 40px; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            td { padding: 12px; text-align: center; border: 1px solid #ddd; }
            .tea { background: #27ae60 !important; color: white; font-weight: bold; }
            .lunch { background: #e67e22 !important; color: white; font-weight: bold; }
            .day { background: #3498db; color: white; font-weight: bold; }
            .free { background: #f8f9fa; color: #7f8c8d; }
            .theory { background: white; }
            .lab { background: #9b59b6; color: white; font-weight: bold; }
        </style></head><body><h1>Complete Timetable - All Semesters</h1>"""
        
        success_count = 0
        fail_count = 0
        
        for sem in ["3", "5", "7"]:
            result = generate_timetable(data, sem)
            if result.get("success"):
                # SAVE the schedule for later use (for teacher timetables)
                schedule_storage.save_schedule(sem, result.get("schedule", {}), 
                                              result.get("time_slots", {}),
                                              result.get("sections", []),
                                              result.get("days", []))
                success_count += 1
            else:
                fail_count += 1
            
            if "html" in result:
                html = result["html"]
                start = html.find(f"<h1>SEMESTER {sem}</h1>")
                if start != -1:
                    end = html.find("</body>")
                    full_html += html[start:end]
            else:
                full_html += f"<h2 style='background:#e74c3c;'>SEMESTER {sem} - Failed to generate</h2>"
        
        full_html += "</body></html>"
        show_html(full_html)
        
        # Show summary
        if fail_count == 0:
            messagebox.showinfo("Success", f"✅ All {success_count} semesters generated successfully!")
        else:
            messagebox.showwarning("Partial Success", 
                                  f"✅ {success_count} semester(s) generated successfully\n"
                                  f"❌ {fail_count} semester(s) failed\n\n"
                                  f"Just click 'All Semesters' again to retry the failed ones!")

    # Section Timetable Buttons
    ttk.Label(frame, text="📚 SECTION TIMETABLES", font=("Arial", 14, "bold"), foreground="#2c3e50").pack(pady=(10, 15))
    
    # Create button grid
    ttk.Button(button_frame, text="🎓 Semester 3", command=generate_sem3, width=22).grid(row=0, column=0, padx=10, pady=8)
    ttk.Button(button_frame, text="🎓 Semester 5", command=generate_sem5, width=22).grid(row=0, column=1, padx=10, pady=8)
    ttk.Button(button_frame, text="🎓 Semester 7", command=generate_sem7, width=22).grid(row=1, column=0, padx=10, pady=8)
    ttk.Button(button_frame, text="🚀 All Semesters", command=generate_all, width=22).grid(row=1, column=1, padx=10, pady=8)

    # Info section
    info_frame = ttk.LabelFrame(frame, text="  ℹ️ Information  ", padding=20)
    info_frame.pack(pady=30, padx=40, fill='both', expand=True)
    
    info_text = """
📚 SECTION TIMETABLES

• Semester 3: 7 sections (A-G) with tea & lunch breaks
• Semester 5: 4 sections (A-D) with lunch break only  
• Semester 7: 3 sections (A-C) with tea & lunch breaks

🎯 HOW TO USE:

1. Click individual semester button (e.g., "Semester 3")
   → Generates timetable for that semester only
   → Opens in your browser automatically

2. Click "All Semesters" button
   → Generates all 3 semesters in one combined page
   → Perfect for printing complete timetables

💾 SAVED DATA:

• Generated schedules are automatically saved to latest_schedules.json
• This file is used by the Teacher Timetables feature
• You can generate teacher timetables in the "👨‍🏫 Teacher Timetables" tab

⚠️ IF GENERATION FAILS:

• The system tries up to 5 times automatically
• Failures are rare (<1% chance)
• If it fails, just click the button again!
• The randomization means each attempt is different

✨ FEATURES:

• Zero conflicts guaranteed (teachers, rooms, time slots)
• Quality constraints enforced (max 2 consecutive same subject)
• Lab distribution rules (Sem 3: one day max 2 labs, others: max 1/day)
• Color-coded HTML output (Blue=Theory, Purple=Lab, Orange=Break)
• Professional, print-ready format
"""
    
    info_label = ttk.Label(info_frame, 
                          text=info_text,
                          justify=tk.LEFT,
                          font=("Arial", 10),
                          foreground="#34495e")
    info_label.pack()

    return frame