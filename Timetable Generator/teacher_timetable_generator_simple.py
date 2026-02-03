# teacher_timetable_generator_simple.py
# FIXED VERSION - Determines Lab/Theory based on DURATION
import json
import os
from collections import defaultdict

def convert_to_12h(time_24h):
    """Convert 24-hour time to 12-hour format (e.g., 13:05 -> 1:05 PM)"""
    if not time_24h or time_24h == "???":
        return time_24h
    
    # Handle time ranges like "08:55-10:45"
    if '-' in time_24h:
        start, end = time_24h.split('-')
        start_12h = convert_single_time_to_12h(start)
        end_12h = convert_single_time_to_12h(end)
        return f"{start_12h}-{end_12h}"
    else:
        return convert_single_time_to_12h(time_24h)

def convert_single_time_to_12h(time_str):
    """Convert single time like 13:05 to 1:05 PM"""
    try:
        hour, minute = map(int, time_str.split(':'))
        
        if hour == 0:
            return f"12:{minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{minute:02d} AM"
        elif hour == 12:
            return f"12:{minute:02d} PM"
        else:
            return f"{hour-12}:{minute:02d} PM"
    except:
        return time_str

def calculate_duration(time_str):
    """Calculate duration in minutes from time string like '8:55 AM-10:45 AM'"""
    try:
        # Handle both 24h and 12h formats
        time_str = time_str.replace(' AM', '').replace(' PM', '')
        start, end = time_str.split('-')
        
        # Parse start time
        start_parts = start.strip().split(':')
        start_hour = int(start_parts[0])
        start_min = int(start_parts[1])
        
        # Parse end time
        end_parts = end.strip().split(':')
        end_hour = int(end_parts[0])
        end_min = int(end_parts[1])
        
        # Calculate duration
        start_total = start_hour * 60 + start_min
        end_total = end_hour * 60 + end_min
        
        return end_total - start_total
    except:
        return 0

def determine_class_type(time_str, original_type):
    """
    Determine if class is Lab or Theory based on duration
    - 55 minutes (single slot) = Theory
    - 110 minutes (double slot) = Lab
    - Open electives stay as open_elective
    """
    # If it's open elective, keep it
    if original_type == "open_elective":
        return "open_elective"
    
    duration = calculate_duration(time_str)
    
    # 110 minutes = Lab (2 slots of 55 min each)
    # 55 minutes = Theory (1 slot)
    if duration >= 100:  # Allow some tolerance (100-120 mins = Lab)
        return "lab"
    else:
        return "theory"

def generate_teacher_timetables_simple(specific_teacher=None):
    """
    Generate teacher timetables by reading from latest_schedules.json
    Shows table with days on LEFT, times on TOP
    Determines Lab/Theory by DURATION
    """
    
    # Check if file exists
    if not os.path.exists("latest_schedules.json"):
        return {
            "success": False,
            "error": "No schedule data found! Generate section timetables first.",
            "html": "<h2>❌ No Data Found</h2><p>Please generate section timetables first in the 'Generate' tab.</p>"
        }
    
    # Load JSON data
    try:
        with open("latest_schedules.json", 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read schedule data: {str(e)}",
            "html": f"<h2>❌ Error</h2><p>Failed to read schedule data: {str(e)}</p>"
        }
    
    # Organize data by teacher
    teacher_data = defaultdict(lambda: {"classes": [], "stats": {"theory": 0, "lab": 0, "open_elective": 0, "total": 0}})
    
    for sem, classes in all_data.items():
        for cls in classes:
            teacher = cls.get("teacher", "???")
            
            # Skip ??? entries
            if teacher == "???":
                continue
            
            # Handle multiple teachers (labs) - split by /
            teachers = [t.strip() for t in teacher.split('/')]
            
            for t in teachers:
                # Determine actual type based on duration
                original_type = cls.get("type", "theory")
                actual_type = determine_class_type(cls["time"], original_type)
                
                # Add class to this teacher (with 12h time format and corrected type)
                teacher_data[t]["classes"].append({
                    "sem": cls["sem"],
                    "section": cls["section"],
                    "day": cls["day"],
                    "time": cls["time"],  # Keep original for sorting
                    "time_12h": convert_to_12h(cls["time"]),  # 12h format for display
                    "time_start": cls["time_start"],
                    "subject": cls["subject"],
                    "room": cls["room"],
                    "type": actual_type  # Use corrected type based on duration
                })
                
                # Update stats with corrected type
                if actual_type == "lab":
                    teacher_data[t]["stats"]["lab"] += 1
                elif actual_type == "open_elective":
                    teacher_data[t]["stats"]["open_elective"] += 1
                else:
                    teacher_data[t]["stats"]["theory"] += 1
                
                teacher_data[t]["stats"]["total"] += 1
    
    # Generate HTML
    if specific_teacher and specific_teacher not in teacher_data:
        return {
            "success": False,
            "error": f"Teacher {specific_teacher} has no classes",
            "html": f"<h2>No Data for {specific_teacher}</h2><p>This teacher has no classes in the generated timetables.</p>"
        }
    
    # Build HTML
    html = generate_html_simple(teacher_data, specific_teacher)
    
    return {
        "success": True,
        "html": html,
        "teacher_count": len(teacher_data)
    }


def generate_html_simple(teacher_data, specific_teacher=None):
    """Generate beautiful HTML for teacher timetables with TABLE layout"""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Teacher Timetables - All Semesters</title>
    <meta charset="UTF-8">
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 15px;
            margin: -40px -40px 40px -40px;
            font-size: 32px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .teacher-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-left: 6px solid #667eea;
        }}
        .teacher-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #dee2e6;
        }}
        .teacher-name {{
            font-size: 26px;
            font-weight: bold;
            color: #667eea;
        }}
        .stats {{
            display: flex;
            gap: 10px;
        }}
        .stat-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 13px;
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        }}
        .timetable-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .timetable-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            font-size: 11px;
        }}
        .timetable-table td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
            vertical-align: middle;
            min-width: 120px;
        }}
        .day-cell {{
            background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
            font-weight: bold;
            color: #667eea;
            font-size: 13px;
            text-align: left;
            padding-left: 15px !important;
            width: 120px;
        }}
        .class-cell {{
            background: #fafafa;
            font-size: 10px;
            padding: 8px 5px !important;
        }}
        .class-item {{
            background: linear-gradient(135deg, #e8f4fd 0%, #d4e9fc 100%);
            border-left: 4px solid #3498db;
            padding: 8px;
            margin: 3px 0;
            border-radius: 5px;
            text-align: left;
            line-height: 1.4;
        }}
        .class-item.lab {{
            background: linear-gradient(135deg, #f3e8ff 0%, #e8d9ff 100%);
            border-left-color: #9b59b6;
        }}
        .class-item.open_elective {{
            background: linear-gradient(135deg, #e8fff0 0%, #d4ffe6 100%);
            border-left-color: #16a085;
        }}
        .class-subject {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 11px;
            margin-bottom: 3px;
        }}
        .class-details {{
            color: #7f8c8d;
            font-size: 9px;
            line-height: 1.3;
        }}
        .sem-badge {{
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
            margin-right: 3px;
        }}
        .empty-cell {{
            color: #bdc3c7;
            font-style: italic;
            font-size: 16px;
        }}
        .no-classes {{
            text-align: center;
            padding: 40px;
            color: #95a5a6;
            font-style: italic;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>👨‍🏫 Teacher Timetables - All Semesters (3, 5, 7)</h1>
"""
    
    # Decide which teachers to show
    teachers_to_show = [specific_teacher] if specific_teacher else sorted(teacher_data.keys())
    
    for teacher in teachers_to_show:
        if teacher not in teacher_data:
            continue
        
        t_data = teacher_data[teacher]
        stats = t_data["stats"]
        classes = t_data["classes"]
        
        if stats["total"] == 0:
            continue
        
        html += f"""
        <div class="teacher-card">
            <div class="teacher-header">
                <div class="teacher-name">{teacher}</div>
                <div class="stats">
                    <span class="stat-badge">📚 {stats['theory']} Theory</span>
                    <span class="stat-badge">🔬 {stats['lab']} Lab</span>
                    <span class="stat-badge">🌟 {stats['open_elective']} Open Elective</span>
                    <span class="stat-badge">⏰ {stats['total']} Total</span>
                </div>
            </div>
"""
        
        # Build TABLE with days on LEFT, times on TOP
        # Get all unique time slots (sorted)
        all_times = sorted(set((c["time"], c["time_12h"], c["time_start"]) for c in classes), key=lambda x: x[2])
        
        # Group classes by day and time
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        schedule_grid = defaultdict(lambda: defaultdict(list))
        
        for cls in classes:
            schedule_grid[cls["day"]][cls["time"]].append(cls)
        
        # Build HTML table
        html += '''<table class="timetable-table">
            <thead>
                <tr>
                    <th style="text-align: left; padding-left: 15px;">📅 Day / ⏰ Time</th>'''
        
        # Column headers (times)
        for time_24h, time_12h, _ in all_times:
            html += f'<th>{time_12h}</th>'
        
        html += '</tr></thead><tbody>'
        
        # Rows (days)
        for day in days_order:
            if day not in schedule_grid:
                continue
            
            html += f'<tr><td class="day-cell">{day}</td>'
            
            # Each time slot column
            for time_24h, time_12h, _ in all_times:
                classes_here = schedule_grid[day].get(time_24h, [])
                
                if classes_here:
                    html += '<td class="class-cell">'
                    for cls in classes_here:
                        # Icon based on corrected type
                        emoji = "📖" if cls["type"] == "theory" else "🔬" if cls["type"] == "lab" else "🌟"
                        html += f'''<div class="class-item {cls['type']}">
                            <div class="class-subject">{emoji} {cls['subject']}</div>
                            <div class="class-details">
                                <span class="sem-badge">S{cls['sem']}</span>
                                Sec: {cls['section']} | {cls['room']}
                            </div>
                        </div>'''
                    html += '</td>'
                else:
                    html += '<td class="empty-cell">—</td>'
            
            html += '</tr>'
        
        html += '</tbody></table>'
        html += "</div>"  # Close teacher-card
    
    if len(teachers_to_show) == 0 or all(teacher_data[t]["stats"]["total"] == 0 for t in teachers_to_show if t in teacher_data):
        html += '<div class="no-classes">😴 No classes found for the selected teacher(s)</div>'
    
    html += """
    </div>
</body>
</html>
"""
    
    return html