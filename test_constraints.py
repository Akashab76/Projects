#!/usr/bin/env python3
"""
Test: Verify Constraint Checking in Scheduler
This simulates what the scheduler does and shows all debug output
"""

from constraint_validator import ConstraintValidator

print("=" * 80)
print("CONSTRAINT CHECKING SIMULATION")
print("=" * 80)

# Test case: SNV with constraint 12:30 PM - 1:30 PM
teacher = "SNV"
day = "Monday"
test_slots = [
    ("11:15 AM", "12:10 PM", "Should be OK - before constraint"),
    ("12:30 PM", "1:25 PM", "Should be BLOCKED - starts at constraint start"),
    ("1:05 PM", "2:00 PM", "Should be BLOCKED - overlaps constraint"),
    ("1:30 PM", "2:25 PM", "Should be OK - starts at constraint end"),
    ("2:00 PM", "2:55 PM", "Should be OK - after constraint"),
]

print(f"\nTesting teacher: {teacher}")
print(f"Day: {day}")
print("\nExpected constraint: 12:30 PM - 1:30 PM (picking up daughter)")
print()

validator = ConstraintValidator()

# Check if teacher has constraints
if teacher in validator.availability_data:
    data = validator.availability_data[teacher]
    print("📋 Teacher's constraints:")
    if 'constraints' in data:
        for c in data['constraints']:
            print(f"  - {c['day']}: {c['start']} - {c['end']} ({c['reason']})")
    else:
        print("  ⚠️  NO CONSTRAINTS FOUND!")
    print()
else:
    print(f"⚠️  Teacher '{teacher}' not found in availability data!")
    print()

print("=" * 80)
print("TESTING TIME SLOTS")
print("=" * 80)

for start_time, end_time, expected in test_slots:
    print(f"\n📍 Testing: {start_time} - {end_time}")
    print(f"   Expected: {expected}")
    print()
    
    available, reason = validator.is_teacher_available(teacher, day, start_time, end_time)
    
    if available:
        print(f"   ✅ Result: AVAILABLE - {reason}")
    else:
        print(f"   ❌ Result: NOT AVAILABLE - {reason}")
    
    print()

print("=" * 80)
print()
print("If constraints are not being detected:")
print("  1. Make sure teacher_availability.json exists")
print("  2. Check that the constraint was saved in the Availability tab")
print("  3. Verify time format is '12:30 PM' not '12:30PM' (space before AM/PM)")
print("  4. Make sure you're using the FIXED scheduler.py")
print()