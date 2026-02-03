#!/usr/bin/env python3
"""
Diagnostic Tool: Test Teacher Constraint Detection
Run this to verify that constraints are properly saved and detected
"""

import json
import os
from constraint_validator import ConstraintValidator

print("=" * 80)
print("TEACHER CONSTRAINT DIAGNOSTIC TOOL")
print("=" * 80)

# Load the availability data
if not os.path.exists('teacher_availability.json'):
    print("\n❌ ERROR: teacher_availability.json not found!")
    print("   Please set up teacher availability first in the Availability tab.")
    exit(1)

with open('teacher_availability.json', 'r', encoding='utf-8') as f:
    availability_data = json.load(f)

print(f"\n✅ Found availability data for {len(availability_data)} teachers")
print()

# Ask which teacher to check
teacher_code = input("Enter teacher code to diagnose (e.g., SNV, MD): ").strip()

if teacher_code not in availability_data:
    print(f"\n❌ Teacher '{teacher_code}' not found in availability data!")
    print(f"   Available teachers: {', '.join(availability_data.keys())}")
    exit(1)

data = availability_data[teacher_code]

print(f"\n{'=' * 80}")
print(f"TEACHER: {teacher_code}")
print(f"{'=' * 80}")

# Show working hours
print("\n📅 WORKING HOURS:")
if 'daily_hours' in data:
    for day, hours in data['daily_hours'].items():
        if hours.get('off'):
            print(f"  {day:12} OFF DAY")
        else:
            print(f"  {day:12} {hours['start']:10} - {hours['end']}")
else:
    print("  No working hours set")

# Show constraints
print("\n🚫 PERSONAL CONSTRAINTS:")
if 'constraints' in data and data['constraints']:
    for i, c in enumerate(data['constraints'], 1):
        print(f"  {i}. {c['day']:12} {c['start']:10} - {c['end']:10}  ({c['reason']})")
else:
    print("  No constraints set")

# Show preferences
print("\n⭐ PREFERENCES:")
print(f"  Time Preference: {data.get('preference', 'No Preference')}")
print(f"  Max Classes/Day: {data.get('max_classes', 'No Limit')}")
if data.get('notes'):
    print(f"  Notes: {data['notes']}")

# Test a specific time slot
print(f"\n{'=' * 80}")
print("TEST A TIME SLOT")
print(f"{'=' * 80}")

day = input("\nEnter day (e.g., Monday): ").strip()
start_time = input("Enter start time (e.g., 1:05 PM): ").strip()
end_time = input("Enter end time (e.g., 2:00 PM): ").strip()

# Create validator and test
validator = ConstraintValidator()
print(f"\n🔍 Testing: {teacher_code} on {day} from {start_time} to {end_time}")
print("-" * 80)

available, reason = validator.is_teacher_available(teacher_code, day, start_time, end_time)

print()
if available:
    print(f"✅ RESULT: {teacher_code} IS AVAILABLE")
    print(f"   Reason: {reason}")
else:
    print(f"❌ RESULT: {teacher_code} IS NOT AVAILABLE")
    print(f"   Reason: {reason}")

print(f"\n{'=' * 80}")
print("DIAGNOSTIC COMPLETE")
print(f"{'=' * 80}")
print()
print("If the constraint should have blocked the slot but didn't:")
print("  1. Check that the time format matches (use 12-hour format with AM/PM)")
print("  2. Make sure you saved the constraint in the Availability tab")
print("  3. Verify the day name matches exactly (case-sensitive)")
print("  4. Replace scheduler.py with the fixed version")
print("  5. Regenerate the timetable")
print()