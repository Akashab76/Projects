"""
Constraint Validator for Timetable Generation
Handles teacher availability and personal constraints
"""

import json
from datetime import datetime, time
from collections import defaultdict

class ConstraintValidator:
    """Validate and check teacher availability constraints"""
    
    def __init__(self):
        self.availability_data = self.load_availability()
    
    def load_availability(self):
        """Load teacher availability from file"""
        try:
            with open('teacher_availability.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def time_to_minutes(self, time_str):
        """Convert time string to minutes since midnight"""
        # Parse "HH:MM AM/PM" format
        try:
            time_parts = time_str.split()
            if len(time_parts) != 2:
                return None
            
            time_part, period = time_parts
            hour, minute = map(int, time_part.split(':'))
            
            # Convert to 24-hour
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
            
            return hour * 60 + minute
        except:
            return None
    
    def is_teacher_available(self, teacher, day, start_time, end_time):
        """Check if teacher is available for given time slot"""
        
        # ✅ RELOAD availability data to get latest constraints!
        self.availability_data = self.load_availability()
        
        if teacher not in self.availability_data:
            return True, "No constraints defined"
        
        data = self.availability_data[teacher]
        
        # DEBUG: Print what we're checking
        print(f"🔍 Checking {teacher} on {day} at {start_time}-{end_time}")
        
        # Check daily working hours
        if 'daily_hours' in data and day in data['daily_hours']:
            day_hours = data['daily_hours'][day]
            
            # Check if it's an off day
            if day_hours.get('off', False):
                print(f"  ❌ {day} is OFF day for {teacher}")
                return False, f"{teacher} has {day} as off day"
            
            # Check if within working hours
            work_start = self.time_to_minutes(day_hours.get('start', '09:00 AM'))
            work_end = self.time_to_minutes(day_hours.get('end', '05:00 PM'))
            slot_start = self.time_to_minutes(start_time)
            slot_end = self.time_to_minutes(end_time)
            
            if slot_start is None or slot_end is None:
                return True, "Invalid time format"
            
            if slot_start < work_start:
                print(f"  ❌ Class starts at {start_time}, but {teacher} starts work at {day_hours['start']}")
                return False, f"{teacher} starts work at {day_hours['start']} on {day}"
            
            if slot_end > work_end:
                print(f"  ❌ Class ends at {end_time}, but {teacher} ends work at {day_hours['end']}")
                return False, f"{teacher} ends work at {day_hours['end']} on {day}"
        
        # Check personal constraints (unavailable blocks)
        if 'constraints' in data:
            for constraint in data['constraints']:
                if constraint['day'] == day or constraint['day'] == 'All Days':
                    block_start = self.time_to_minutes(constraint['start'])
                    block_end = self.time_to_minutes(constraint['end'])
                    slot_start = self.time_to_minutes(start_time)
                    slot_end = self.time_to_minutes(end_time)
                    
                    if slot_start is None or slot_end is None:
                        continue
                    
                    # DEBUG: Show constraint check
                    print(f"  📋 Checking constraint: {constraint['start']}-{constraint['end']} ({constraint['reason']})")
                    print(f"     Slot: {start_time}-{end_time}")
                    print(f"     Block: {block_start}-{block_end} minutes")
                    print(f"     Slot: {slot_start}-{slot_end} minutes")
                    
                    # Check if times overlap
                    if not (slot_end <= block_start or slot_start >= block_end):
                        print(f"  ❌ OVERLAP! Constraint blocks this slot: {constraint['reason']}")
                        return False, f"{teacher} unavailable: {constraint['reason']}"
        
        print(f"  ✅ {teacher} is available!")
        return True, "Available"
    
    def get_preference_penalty(self, teacher, start_time):
        """Get penalty score for scheduling based on preferences"""
        # ✅ RELOAD availability data to get latest preferences!
        self.availability_data = self.load_availability()
        
        if teacher not in self.availability_data:
            return 0
        
        data = self.availability_data[teacher]
        preference = data.get('preference', 'No Preference')
        
        slot_minutes = self.time_to_minutes(start_time)
        if slot_minutes is None:
            return 0
        
        # Calculate penalties based on lunch time reference (~1 PM / 13:00)
        LUNCH_TIME = 13 * 60  # 1:00 PM in minutes
        
        if preference == "Prefer Before Lunch":
            # Penalty for classes after lunch (after 1 PM)
            if slot_minutes >= LUNCH_TIME:
                return 10
        elif preference == "Prefer After Lunch":
            # Penalty for classes before lunch (before 1 PM)
            if slot_minutes < LUNCH_TIME:
                return 10
        elif preference == "Prefer Early Morning":
            # Penalty increases after 10 AM
            if slot_minutes >= 10 * 60:
                return 15
        # Support old preference values for backward compatibility
        elif preference == "Prefer Morning (Before 12 PM)":
            if slot_minutes >= 12 * 60:
                return 10
        elif preference == "Prefer Afternoon (After 12 PM)":
            if slot_minutes < 12 * 60:
                return 10
        elif preference == "Prefer Early Morning (Before 10 AM)":
            if slot_minutes >= 10 * 60:
                return 15
        
        return 0
    
    def check_max_classes_per_day(self, teacher, day, current_schedule):
        """Check if adding another class would exceed max classes per day"""
        if teacher not in self.availability_data:
            return True, "No limit defined"
        
        data = self.availability_data[teacher]
        max_classes = data.get('max_classes', 'No Limit')
        
        if max_classes == 'No Limit':
            return True, "No limit"
        
        try:
            max_limit = int(max_classes)
        except:
            return True, "Invalid limit"
        
        # Count current classes for this teacher on this day
        count = 0
        for cls in current_schedule:
            if cls['teacher'] == teacher and cls['day'] == day:
                count += 1
        
        if count >= max_limit:
            return False, f"{teacher} already has {count} classes on {day} (max: {max_limit})"
        
        return True, "Within limit"
    
    def validate_schedule(self, schedule):
        """Validate entire schedule against all constraints"""
        violations = []
        warnings = []
        
        for cls in schedule:
            teacher = cls['teacher']
            day = cls['day']
            start_time = cls['start_time']
            end_time = cls['end_time']
            
            # Check availability
            available, reason = self.is_teacher_available(teacher, day, start_time, end_time)
            if not available:
                violations.append({
                    'type': 'HARD_CONSTRAINT',
                    'class': f"{cls['subject']} - {cls['section']}",
                    'teacher': teacher,
                    'day': day,
                    'time': f"{start_time} - {end_time}",
                    'reason': reason
                })
            
            # Check preferences (soft constraints)
            penalty = self.get_preference_penalty(teacher, start_time)
            if penalty > 0:
                warnings.append({
                    'type': 'PREFERENCE_VIOLATION',
                    'class': f"{cls['subject']} - {cls['section']}",
                    'teacher': teacher,
                    'day': day,
                    'time': start_time,
                    'penalty': penalty,
                    'reason': f"Not aligned with {teacher}'s preference"
                })
        
        return violations, warnings
    
    def get_teacher_summary(self, teacher):
        """Get summary of teacher's constraints"""
        if teacher not in self.availability_data:
            return "No constraints defined"
        
        data = self.availability_data[teacher]
        summary = []
        
        # Working hours
        if 'daily_hours' in data:
            summary.append("📅 WORKING HOURS:")
            for day, hours in data['daily_hours'].items():
                if hours.get('off'):
                    summary.append(f"  {day}: OFF DAY")
                else:
                    summary.append(f"  {day}: {hours['start']} - {hours['end']}")
        
        # Constraints
        if 'constraints' in data and data['constraints']:
            summary.append("\n🚫 UNAVAILABLE TIMES:")
            for c in data['constraints']:
                summary.append(f"  {c['day']}: {c['start']}-{c['end']} ({c['reason']})")
        
        # Preferences
        if data.get('preference', 'No Preference') != 'No Preference':
            summary.append(f"\n⭐ PREFERENCE: {data['preference']}")
        
        if data.get('max_classes', 'No Limit') != 'No Limit':
            summary.append(f"📊 MAX CLASSES/DAY: {data['max_classes']}")
        
        return "\n".join(summary)
    
    def get_available_slots(self, teacher, day):
        """Get list of available time slots for teacher on given day"""
        if teacher not in self.availability_data:
            # Return all standard slots if no constraints
            return self.get_standard_slots()
        
        data = self.availability_data[teacher]
        available_slots = []
        
        # Get working hours for the day
        if 'daily_hours' in data and day in data['daily_hours']:
            day_hours = data['daily_hours'][day]
            
            if day_hours.get('off'):
                return []  # Off day, no slots
            
            work_start = self.time_to_minutes(day_hours.get('start', '09:00 AM'))
            work_end = self.time_to_minutes(day_hours.get('end', '05:00 PM'))
        else:
            work_start = 9 * 60  # 9 AM
            work_end = 17 * 60  # 5 PM
        
        # Generate slots
        current_time = work_start
        while current_time + 55 <= work_end:  # 55 min class
            slot_start = self.minutes_to_time(current_time)
            slot_end = self.minutes_to_time(current_time + 55)
            
            # Check if slot is blocked by constraints
            is_blocked = False
            if 'constraints' in data:
                for constraint in data['constraints']:
                    if constraint['day'] == day or constraint['day'] == 'All Days':
                        block_start = self.time_to_minutes(constraint['start'])
                        block_end = self.time_to_minutes(constraint['end'])
                        
                        # Check overlap
                        if not (current_time + 55 <= block_start or current_time >= block_end):
                            is_blocked = True
                            break
            
            if not is_blocked:
                available_slots.append({
                    'start': slot_start,
                    'end': slot_end,
                    'penalty': self.get_preference_penalty(teacher, slot_start)
                })
            
            current_time += 55  # Next slot
        
        return available_slots
    
    def minutes_to_time(self, minutes):
        """Convert minutes since midnight to time string"""
        hour = minutes // 60
        minute = minutes % 60
        
        period = 'AM' if hour < 12 else 'PM'
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour
        
        return f"{display_hour:02d}:{minute:02d} {period}"
    
    def get_standard_slots(self):
        """Get standard time slots (9 AM - 5 PM)"""
        slots = []
        current = 9 * 60  # 9 AM
        end = 17 * 60  # 5 PM
        
        while current + 55 <= end:
            slots.append({
                'start': self.minutes_to_time(current),
                'end': self.minutes_to_time(current + 55),
                'penalty': 0
            })
            current += 55
        
        return slots