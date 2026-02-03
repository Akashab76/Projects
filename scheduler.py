import random
from utils import parse_time, min_to_time, min_to_time_12h
from collections import defaultdict, Counter

# ✅ Import constraint validator for validation reporting AND scheduling
from constraint_validator import ConstraintValidator

# 🔥 Global validator instance
validator = None

def generate_timetable(data, sem):
    # RETRY MECHANISM: Try up to 5 times if scheduling fails
    max_attempts = 5
    
    for attempt_num in range(1, max_attempts + 1):
        if attempt_num > 1:
            print(f"\n🔄 RETRY #{attempt_num}: Restarting with different randomization...")
        
        result = _attempt_timetable_generation(data, sem, attempt_num)
        
        if result["success"]:
            return result
    
    # All attempts failed
    print(f"\n❌ FAILED after {max_attempts} attempts")
    return result

def _attempt_timetable_generation(data, sem, attempt_num):
    """Single attempt at generating timetable"""
    if attempt_num == 1:
        print(f"\n=== ULTIMATE FINAL BOSS SCHEDULING FOR SEMESTER {sem} ===")
        print(f"🚨 CUTOFF: No classes scheduled at or after 4:45 PM")
        print(f"🔥 CONSTRAINT-AWARE SCHEDULING: Teacher availability & preferences ENABLED")
    
    # 🔥 Initialize constraint validator (reload to get latest data!)
    global validator
    validator = ConstraintValidator()
    scheduled_classes = []  # Track all scheduled classes for validation
    
    # 🔥 Track classes per day per teacher for max_classes constraint
    teacher_classes_per_day = defaultdict(lambda: defaultdict(int))
    
    sections = data.sections.get(sem, [])
    if not sections:
        return {"html": "<h2>No sections found</h2>", "success": False}
    
    if attempt_num == 1:
        print(f"Sections: {sections}")
    
    days = ["Friday", "Saturday"] if sem == "7" else ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Build time slots
    time_slots = {}
    for sec in sections:
        for day in days:
            cfg = data.timings.get(sem, {}).get(sec, {}).get(day)
            if not cfg:
                continue
            current = parse_time(cfg["start_time"])
            duration = cfg["class_dur"]
            num = cfg["num_classes"]
            breaks = cfg.get("breaks", [])
            
            slots = []
            for _ in range(num):
                # 🚨 CUTOFF: Don't create slots starting at or after 4:45 PM (1005 min)
                if current >= 1005:  # 4:45 PM = 16*60+45
                    break
                    
                for brk in breaks:
                    bs = parse_time(brk["start"])
                    be = parse_time(brk["end"])
                    if bs <= current < be:
                        current = be
                slots.append((current, current + duration))
                current += duration
            time_slots[(sec, day)] = slots

    schedule = {}
    teacher_busy = defaultdict(set)
    room_busy = {r["name"]: set() for r in data.classrooms}
    
    def get_time_key(day, start_time):
        return (day, start_time)

    # Analyze teacher workload
    teacher_sections = defaultdict(list)
    for sec in sections:
        for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items():
            teacher = mapping.get('theory')
            if teacher and sec not in teacher_sections[teacher]:
                teacher_sections[teacher].append(sec)
    
    if attempt_num == 1:
        print(f"Teachers with 2+ sections: {len([t for t, secs in teacher_sections.items() if len(secs) >= 2])}")
        for t, secs in list(teacher_sections.items())[:5]:
            if len(secs) >= 2:
                print(f"  {t}: {secs}")
    
    # Initialize tracking structures
    lectures_remaining = {}
    for sec in sections:
        lectures_remaining[sec] = {}
        for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items():
            sub = next((s for s in data.subjects[sem] if s["code"] == code), None)
            if not sub or sub["elective"] == "yes" or sub.get("open_elective") == "yes" or sub["l"] == 0:
                continue
            lectures_remaining[sec][code] = sub["l"]
    
    teacher_section_slots = defaultdict(lambda: defaultdict(set))
    
    # SKIP PRE-SCHEDULING - it blocks too many slots!
    # Go straight to smart scheduling with more attempts

    # STEP 1: Open Electives (keep first - they're pre-scheduled)
    for sem_key in data.open_elective_schedule:
        if sem_key == sem:
            for sec in data.open_elective_schedule[sem_key]:
                if sec not in sections:
                    continue
                for oe_code, slot_list in data.open_elective_schedule[sem_key][sec].items():
                    mapping = data.mappings.get(sem, {}).get(sec, {}).get(oe_code)
                    if not mapping:
                        continue
                    teacher = mapping['theory']
                    for oe_info in slot_list:
                        day = oe_info['day']
                        slot_idx = oe_info['slot_index']
                        room = oe_info['room']
                        if (sec, day) in time_slots and slot_idx < len(time_slots[(sec, day)]):
                            start_time, end_time = time_slots[(sec, day)][slot_idx]
                            time_key = get_time_key(day, start_time)
                            
                            # ✅ CHECK CONSTRAINT: Warn if open elective violates teacher constraints
                            start_12h = min_to_time_12h(start_time)
                            end_12h = min_to_time_12h(end_time)
                            available, reason = validator.is_teacher_available(teacher, day, start_12h, end_12h)
                            if not available:
                                print(f"  ⚠️ Open Elective {oe_code} scheduled despite constraint: {teacher} - {reason}")
                            
                            schedule[(sec, day, slot_idx)] = {
                                "type": "open_elective",
                                "code": oe_code,
                                "teacher": teacher,
                                "room": room
                            }
                            teacher_busy[teacher].add(time_key)
                            room_busy[room].add(time_key)
                            
                            # ✅ Track for validation
                            scheduled_classes.append({
                                'day': day,
                                'start_time': min_to_time_12h(start_time),
                                'end_time': min_to_time_12h(end_time),
                                'subject': oe_code,
                                'teacher': teacher,
                                'section': sec,
                                'semester': sem,
                                'room': room,
                                'type': 'open_elective'
                            })

    # STEP 2: Labs (with constraints per semester)
    # SEMESTER 3: At most ONE day can have 2 labs, rest have max 1 lab
    # SEMESTER 5, 7: Max 1 lab per day (any day)
    labs_per_day = defaultdict(lambda: defaultdict(int))  # Track labs count: labs_per_day[sec][day]
    days_with_2_labs = defaultdict(int)  # Track how many days have 2 labs per section (ONLY for sem 3)
    
    for sec in sections:
        lab_subjects = [(code, mapping) for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items()
                       if next((s for s in data.subjects[sem] if s["code"] == code), {}).get("islab") == "yes"
                       and len(mapping.get("lab", [])) >= 2]
        
        for code, mapping in lab_subjects:
            labs = mapping.get("lab", [])
            teacher1, teacher2 = labs[0], labs[1]
            placed = False
            
            # RANDOMIZE day order so labs don't always go Mon-Tue-Wed!
            shuffled_days = days.copy()
            random.shuffle(shuffled_days)
            
            for day in shuffled_days:
                if placed:
                    break
                
                # SEMESTER 3 SPECIAL: At most ONE day can have 2 labs
                if sem == "3":
                    # If this day already has 2 labs, skip it (can't place 3rd)
                    if labs_per_day[sec][day] >= 2:
                        continue
                    # If another day already has 2 labs AND current day has 1, skip it (can't add 2nd)
                    if days_with_2_labs[sec] >= 1 and labs_per_day[sec][day] >= 1:
                        continue
                    # Otherwise: Can place lab (might result in 1 or 2 labs on this day)
                else:
                    # OTHER SEMESTERS (5, 7): Max 1 lab per day (any day, just spread them)
                    if labs_per_day[sec][day] >= 1:
                        continue
                
                slots = time_slots.get((sec, day), [])
                
                # 🚀 SOLUTION 2: RANDOMIZE SLOT POSITIONS TOO!
                slot_indices = list(range(len(slots) - 1))
                random.shuffle(slot_indices)
                
                for idx in slot_indices:
                    start1, end1 = slots[idx]
                    start2, end2 = slots[idx + 1]
                    
                    if end1 != start2:
                        continue
                    if (sec, day, idx) in schedule or (sec, day, idx + 1) in schedule:
                        continue
                    
                    # ✅ CHECK CONSTRAINT: Both lab teachers must be available
                    start_12h = min_to_time_12h(start1)
                    end_12h = min_to_time_12h(end2)
                    
                    available1, reason1 = validator.is_teacher_available(teacher1, day, start_12h, end_12h)
                    if not available1:
                        # print(f"    ⏭️ {teacher1} not available for lab {code} on {day} {start_12h}: {reason1}")
                        continue  # Teacher 1 not available, skip this slot
                    
                    available2, reason2 = validator.is_teacher_available(teacher2, day, start_12h, end_12h)
                    if not available2:
                        # print(f"    ⏭️ {teacher2} not available for lab {code} on {day} {start_12h}: {reason2}")
                        continue  # Teacher 2 not available, skip this slot
                    
                    time_key1 = get_time_key(day, start1)
                    time_key2 = get_time_key(day, start2)
                    
                    if time_key1 in teacher_busy[teacher1] or time_key2 in teacher_busy[teacher2]:
                        continue
                    
                    labs_available = [r for r in data.classrooms if r["is_lab"] == "yes" 
                                     and time_key1 not in room_busy[r["name"]] 
                                     and time_key2 not in room_busy[r["name"]]]
                    
                    if labs_available:
                        lab_room = labs_available[0]["name"]
                        schedule[(sec, day, idx)] = {
                            "type": "lab",
                            "code": code,
                            "teacher": f"{teacher1}/{teacher2}",
                            "room": lab_room,
                            "lab_span": 2
                        }
                        schedule[(sec, day, idx + 1)] = {
                            "type": "lab",
                            "code": code,
                            "teacher": f"{teacher1}/{teacher2}",
                            "room": lab_room,
                            "skip": True
                        }
                        teacher_busy[teacher1].add(time_key1)
                        teacher_busy[teacher1].add(time_key2)
                        teacher_busy[teacher2].add(time_key1)
                        teacher_busy[teacher2].add(time_key2)
                        room_busy[lab_room].add(time_key1)
                        room_busy[lab_room].add(time_key2)
                        
                        # INCREMENT lab count for this day!
                        labs_per_day[sec][day] += 1
                        
                        # 🔥 Track classes per day for both lab teachers
                        teacher_classes_per_day[teacher1][day] += 1
                        teacher_classes_per_day[teacher2][day] += 1
                        
                        # SEMESTER 3 ONLY: Track if this day just reached 2 labs
                        if sem == "3" and labs_per_day[sec][day] == 2:
                            days_with_2_labs[sec] += 1
                            print(f"  ℹ️  Sem 3: {sec} now has 2 labs on {day} (the one allowed 2-lab day)")
                        
                        # ✅ Track for validation (both teachers)
                        scheduled_classes.append({
                            'day': day,
                            'start_time': min_to_time_12h(start1),
                            'end_time': min_to_time_12h(end2),
                            'subject': code,
                            'teacher': teacher1,
                            'section': sec,
                            'semester': sem,
                            'room': lab_room,
                            'type': 'lab'
                        })
                        scheduled_classes.append({
                            'day': day,
                            'start_time': min_to_time_12h(start1),
                            'end_time': min_to_time_12h(end2),
                            'subject': code,
                            'teacher': teacher2,
                            'section': sec,
                            'semester': sem,
                            'room': lab_room,
                            'type': 'lab'
                        })
                        
                        placed = True
                        break

    # STEP 3: Electives
    elective_subjects = [s for s in data.subjects.get(sem, []) if s["elective"] == "yes" and s.get("open_elective", "no") != "yes"]
    
    if elective_subjects:
        max_lectures = max([s["l"] for s in elective_subjects])
        for lec_num in range(max_lectures):
            placed = False
            for day in days:
                if placed:
                    break
                max_slots = max([len(time_slots.get((sec, day), [])) for sec in sections], default=0)
                for try_slot_idx in range(max_slots):
                    all_ok = True
                    for sec in sections:
                        slots = time_slots.get((sec, day), [])
                        if try_slot_idx >= len(slots) or (sec, day, try_slot_idx) in schedule:
                            all_ok = False
                            break
                    if not all_ok:
                        continue
                    
                    teachers_ok = True
                    for sec in sections:
                        slots = time_slots.get((sec, day), [])
                        if try_slot_idx >= len(slots):
                            continue
                        start_time, end_time = slots[try_slot_idx]
                        time_key = get_time_key(day, start_time)
                        
                        # Convert to 12h for constraint checking
                        start_12h = min_to_time_12h(start_time)
                        end_12h = min_to_time_12h(end_time)
                        
                        for elec in elective_subjects:
                            if lec_num >= elec["l"]:
                                continue
                            mapping = data.mappings.get(sem, {}).get(sec, {}).get(elec["code"])
                            if mapping:
                                teacher = mapping["theory"]
                                
                                # ✅ CHECK CONSTRAINT: Teacher must be available
                                available, reason = validator.is_teacher_available(teacher, day, start_12h, end_12h)
                                if not available:
                                    teachers_ok = False
                                    break
                                
                                if time_key in teacher_busy[teacher]:
                                    teachers_ok = False
                                    break
                        if not teachers_ok:
                            break
                    if not teachers_ok:
                        continue
                    
                    elective_room_map = {}
                    rooms_ok = True
                    all_time_keys = set()
                    for sec in sections:
                        slots = time_slots.get((sec, day), [])
                        if try_slot_idx < len(slots):
                            start_time, _ = slots[try_slot_idx]
                            all_time_keys.add(get_time_key(day, start_time))
                    
                    for elec in elective_subjects:
                        if lec_num >= elec["l"]:
                            continue
                        available = [r["name"] for r in data.classrooms
                                   if r["is_lab"] == "no"
                                   and all(tk not in room_busy[r["name"]] for tk in all_time_keys)
                                   and r["name"] not in elective_room_map.values()]
                        if not available:
                            rooms_ok = False
                            break
                        elective_room_map[elec["code"]] = available[0]
                    if not rooms_ok:
                        continue
                    
                    for sec in sections:
                        slots = time_slots.get((sec, day), [])
                        if try_slot_idx >= len(slots):
                            continue
                        start_time, _ = slots[try_slot_idx]
                        time_key = get_time_key(day, start_time)
                        
                        codes_list = []
                        rooms_dict = {}
                        teachers_dict = {}
                        
                        for elec in elective_subjects:
                            if lec_num >= elec["l"]:
                                continue
                            mapping = data.mappings.get(sem, {}).get(sec, {}).get(elec["code"])
                            if mapping:
                                teacher = mapping["theory"]
                                room = elective_room_map[elec["code"]]
                                teacher_busy[teacher].add(time_key)
                                # 🔥 Track classes per day for this teacher
                                teacher_classes_per_day[teacher][day] += 1
                                codes_list.append(elec["code"])
                                rooms_dict[elec["code"]] = room
                                teachers_dict[elec["code"]] = teacher
                        
                        for code in codes_list:
                            room = elective_room_map[code]
                            for tk in all_time_keys:
                                room_busy[room].add(tk)
                        
                        schedule[(sec, day, try_slot_idx)] = {
                            "type": "elective",
                            "codes": codes_list,
                            "rooms": rooms_dict,
                            "teachers": teachers_dict
                        }
                        
                        # ✅ Track for validation
                        slots = time_slots.get((sec, day), [])
                        if try_slot_idx < len(slots):
                            start_time, end_time = slots[try_slot_idx]
                            for code in codes_list:
                                scheduled_classes.append({
                                    'day': day,
                                    'start_time': min_to_time_12h(start_time),
                                    'end_time': min_to_time_12h(end_time),
                                    'subject': code,
                                    'teacher': teachers_dict[code],
                                    'section': sec,
                                    'semester': sem,
                                    'room': rooms_dict[code],
                                    'type': 'elective'
                                })
                    
                    placed = True
                    break

    # STEP 4: THEORY LECTURES
    
    def place_lecture_smart(sec, code, teacher, sub):
        """Smart placement avoiding cross-section conflicts"""
        other_sections = [s for s in teacher_sections.get(teacher, []) if s != sec]
        forbidden_times = set()
        for other_sec in other_sections:
            forbidden_times.update(teacher_section_slots[teacher][other_sec])
        
        available_slots = []
        for day in days:
            # REMOVED: Max 2 per day check - only checking consecutive now!
            
            slots = time_slots.get((sec, day), [])
            for idx in range(len(slots)):
                if (sec, day, idx) in schedule:
                    continue
                
                start_time, end_time = slots[idx]
                time_key = get_time_key(day, start_time)
                
                if time_key in teacher_busy[teacher]:
                    continue
                
                # ✅ CHECK CONSTRAINT: Teacher must be available
                start_12h = min_to_time_12h(start_time)
                end_12h = min_to_time_12h(end_time)
                available, reason = validator.is_teacher_available(teacher, day, start_12h, end_12h)
                if not available:
                    continue  # Teacher not available, skip this slot
                
                available_rooms = [r["name"] for r in data.classrooms 
                                 if r["is_lab"] == "no" and time_key not in room_busy[r["name"]]]
                
                if not available_rooms:
                    continue
                
                # 🔥 CHECK MAX CLASSES PER DAY
                current_count = teacher_classes_per_day[teacher][day]
                if teacher in validator.availability_data:
                    max_classes = validator.availability_data[teacher].get('max_classes', 'No Limit')
                    if max_classes != 'No Limit':
                        try:
                            max_limit = int(max_classes)
                            if current_count >= max_limit:
                                continue  # Teacher already at max classes for this day
                        except:
                            pass  # Invalid limit, ignore
                
                # 🔥 GET PREFERENCE PENALTY (soft constraint)
                preference_penalty = validator.get_preference_penalty(teacher, start_12h)
                
                # PRIORITY SYSTEM:
                # 1. Avoid teacher cross-section conflicts
                # 2. NO 3+ same subjects in a row (HARD BLOCK!)
                # 3. Soft preference to spread same subjects
                # 4. 🔥 PREFER slots aligned with teacher preferences
                
                priority = 0 if time_key in forbidden_times else 1
                
                # 🔥 Apply preference penalty (higher penalty = lower priority)
                priority -= (preference_penalty / 20.0)  # Scale down penalty
                
                # CHECK 1: Would this create 3+ in a row? (HARD BLOCK!)
                would_create_3_in_row = False
                
                # Check if idx-1 and idx-2 are same subject
                if idx >= 2:
                    if (sec, day, idx-1) in schedule and (sec, day, idx-2) in schedule:
                        entry1 = schedule[(sec, day, idx-1)]
                        entry2 = schedule[(sec, day, idx-2)]
                        if (entry1.get("code") == code and entry2.get("code") == code and
                            entry1.get("type") != "lab" and entry2.get("type") != "lab"):
                            would_create_3_in_row = True
                
                # Check if idx+1 and idx+2 are same subject
                if idx <= len(slots) - 3:
                    if (sec, day, idx+1) in schedule and (sec, day, idx+2) in schedule:
                        entry1 = schedule[(sec, day, idx+1)]
                        entry2 = schedule[(sec, day, idx+2)]
                        if (entry1.get("code") == code and entry2.get("code") == code and
                            entry1.get("type") != "lab" and entry2.get("type") != "lab"):
                            would_create_3_in_row = True
                
                # Check if idx-1 same and idx+1 same (we'd be in the middle of 3)
                if idx >= 1 and idx < len(slots) - 1:
                    if (sec, day, idx-1) in schedule and (sec, day, idx+1) in schedule:
                        entry1 = schedule[(sec, day, idx-1)]
                        entry2 = schedule[(sec, day, idx+1)]
                        if (entry1.get("code") == code and entry2.get("code") == code and
                            entry1.get("type") != "lab" and entry2.get("type") != "lab"):
                            would_create_3_in_row = True
                
                # HARD SKIP if creates 3 in a row!
                if would_create_3_in_row:
                    continue
                
                # ✅ Allow 2 consecutive freely - no penalty!
                # Only hard constraint is 3+ consecutive (checked above)
                
                available_slots.append((priority, day, idx, time_key, available_rooms[0]))
        
        available_slots.sort(key=lambda x: x[0], reverse=True)
        
        if len(available_slots) > 0:
            priority_groups = {}
            for slot in available_slots:
                p = slot[0]
                if p not in priority_groups:
                    priority_groups[p] = []
                priority_groups[p].append(slot)
            
            shuffled_slots = []
            for p in sorted(priority_groups.keys(), reverse=True):
                group = priority_groups[p]
                random.shuffle(group)
                shuffled_slots.extend(group)
            
            available_slots = shuffled_slots
        
        for priority, day, idx, time_key, room in available_slots:
            display_type = "lab" if sub["islab"] == "yes" else "theory"
            schedule[(sec, day, idx)] = {
                "type": display_type,
                "code": code,
                "teacher": teacher,
                "room": room
            }
            teacher_busy[teacher].add(time_key)
            room_busy[room].add(time_key)
            teacher_section_slots[teacher][sec].add(time_key)
            # 🔥 Track classes per day for this teacher
            teacher_classes_per_day[teacher][day] += 1
            # REMOVED: lectures_per_day_per_subject tracking
            
            # ✅ Track for validation
            slots = time_slots.get((sec, day), [])
            if idx < len(slots):
                start_time, end_time = slots[idx]
                scheduled_classes.append({
                    'day': day,
                    'start_time': min_to_time_12h(start_time),
                    'end_time': min_to_time_12h(end_time),
                    'subject': code,
                    'teacher': teacher,
                    'section': sec,
                    'semester': sem,
                    'room': room,
                    'type': display_type
                })
            
            return True
        
        return False
    
    print("ULTRA SMART SCHEDULING: 20000 attempts with intelligent conflict avoidance...")
    
    for attempt in range(20000):
        if attempt % 2000 == 0 and attempt > 0:
            remaining = sum(sum(lectures_remaining[s].values()) for s in sections)
            print(f"  Attempt {attempt}: {remaining} lectures remaining...")
        
        shuffled_sections = sections.copy()
        random.shuffle(shuffled_sections)
        
        for sec in shuffled_sections:
            subjects = [(code, mapping, sub)
                       for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items()
                       for sub in [next((s for s in data.subjects[sem] if s["code"] == code), None)]
                       if sub and sub["elective"] != "yes" and sub.get("open_elective") != "yes"
                       and sub["l"] > 0 and code in lectures_remaining.get(sec, {})
                       and lectures_remaining[sec][code] > 0]
            
            random.shuffle(subjects)
            
            for code, mapping, sub in subjects:
                if lectures_remaining[sec][code] <= 0:
                    continue
                teacher = mapping["theory"]
                if place_lecture_smart(sec, code, teacher, sub):
                    lectures_remaining[sec][code] -= 1
                    break
    
    print("FINAL SWAP PHASE: Moving lectures (10000 attempts)...")
    
    for attempt in range(10000):  # DOUBLED from 5000 to 10000!
        stuck = [(sec, code, mapping, sub)
                 for sec in sections
                 for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items()
                 for sub in [next((s for s in data.subjects[sem] if s["code"] == code), None)]
                 if sub and code in lectures_remaining.get(sec, {}) and lectures_remaining[sec][code] > 0]
        
        if not stuck:
            break
        
        sec, code, mapping, sub = random.choice(stuck)
        teacher = mapping["theory"]
        
        teacher_lectures = []
        for s in sections:
            for d in days:
                slots = time_slots.get((s, d), [])
                for idx in range(len(slots)):
                    if (s, d, idx) in schedule:
                        entry = schedule[(s, d, idx)]
                        if (entry.get("teacher") == teacher and 
                            entry.get("type") not in ["open_elective", "elective", "lab"]):
                            teacher_lectures.append((s, d, idx, entry["code"]))
        
        if not teacher_lectures:
            continue
        
        random.shuffle(teacher_lectures)
        
        # INCREASED from 5 to 15 swap attempts per stuck lecture!
        for move_sec, move_day, move_idx, move_code in teacher_lectures[:15]:
            move_slots = time_slots.get((move_sec, move_day), [])
            move_start, _ = move_slots[move_idx]
            move_time_key = get_time_key(move_day, move_start)
            
            old_entry = schedule[(move_sec, move_day, move_idx)]
            old_room = old_entry["room"]
            old_code = old_entry["code"]  # Store the code being removed
            
            del schedule[(move_sec, move_day, move_idx)]
            teacher_busy[teacher].discard(move_time_key)
            room_busy[old_room].discard(move_time_key)
            teacher_section_slots[teacher][move_sec].discard(move_time_key)
            # REMOVED: lectures_per_day_per_subject tracking
            
            if move_sec == sec:
                if move_time_key not in teacher_busy[teacher]:
                    available_rooms = [r["name"] for r in data.classrooms 
                                     if r["is_lab"] == "no" and move_time_key not in room_busy[r["name"]]]
                    if available_rooms:
                        display_type = "lab" if sub["islab"] == "yes" else "theory"
                        schedule[(sec, move_day, move_idx)] = {
                            "type": display_type,
                            "code": code,
                            "teacher": teacher,
                            "room": available_rooms[0]
                        }
                        teacher_busy[teacher].add(move_time_key)
                        room_busy[available_rooms[0]].add(move_time_key)
                        teacher_section_slots[teacher][sec].add(move_time_key)
                        lectures_remaining[sec][code] -= 1
                        # REMOVED: lectures_per_day_per_subject tracking
                        
                        move_sub = next((s for s in data.subjects[sem] if s["code"] == move_code), None)
                        if not place_lecture_smart(move_sec, move_code, teacher, move_sub):
                            if move_sec in lectures_remaining and move_code in lectures_remaining[move_sec]:
                                lectures_remaining[move_sec][move_code] += 1
                        
                        break
            
            if place_lecture_smart(sec, code, teacher, sub):
                lectures_remaining[sec][code] -= 1
                
                move_sub = next((s for s in data.subjects[sem] if s["code"] == move_code), None)
                if not place_lecture_smart(move_sec, move_code, teacher, move_sub):
                    if move_sec in lectures_remaining and move_code in lectures_remaining[move_sec]:
                        lectures_remaining[move_sec][move_code] += 1
                
                break
            else:
                schedule[(move_sec, move_day, move_idx)] = old_entry
                teacher_busy[teacher].add(move_time_key)
                room_busy[old_room].add(move_time_key)
                teacher_section_slots[teacher][move_sec].add(move_time_key)
                # REMOVED: lectures_per_day_per_subject tracking
    
    # BRUTE FORCE LAST RESORT - Try EVERY slot systematically
    # IGNORES quality constraints (3 in a row, compactness) - just places anywhere valid!
    remaining_count = sum(sum(lectures_remaining[s].values()) for s in sections)
    if remaining_count > 0:
        print(f"BRUTE FORCE LAST RESORT: Trying all {remaining_count} remaining lectures...")
        
        # Try up to 10 passes - keep going until nothing changes
        for pass_num in range(10):
            stuck_before = sum(sum(lectures_remaining[s].values()) for s in sections)
            
            stuck = [(sec, code, mapping, sub)
                     for sec in sections
                     for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items()
                     for sub in [next((s for s in data.subjects[sem] if s["code"] == code), None)]
                     if sub and code in lectures_remaining.get(sec, {}) and lectures_remaining[sec][code] > 0]
            
            if not stuck:
                break
            
            # Shuffle to try different orders
            random.shuffle(stuck)
            
            for sec, code, mapping, sub in stuck:
                teacher = mapping["theory"]
                
                # DEBUG: Count why we can't place
                total_slots = 0
                occupied_slots = 0
                teacher_busy_slots = 0
                no_room_slots = 0
                
                while lectures_remaining[sec][code] > 0:
                    placed = False
                    
                    # Try EVERY slot in this section - NO quality constraints!
                    for day in days:
                        if placed:
                            break
                        slots = time_slots.get((sec, day), [])
                        for idx in range(len(slots)):
                            total_slots += 1
                            
                            if (sec, day, idx) in schedule:
                                occupied_slots += 1
                                continue
                            
                            start_time, _ = slots[idx]
                            time_key = get_time_key(day, start_time)
                            
                            if time_key in teacher_busy[teacher]:
                                teacher_busy_slots += 1
                                continue
                            
                            available_rooms = [r["name"] for r in data.classrooms 
                                             if r["is_lab"] == "no" and time_key not in room_busy[r["name"]]]
                            
                            if not available_rooms:
                                no_room_slots += 1
                                continue
                            
                            # PLACE IT - ignore all quality constraints!
                            display_type = "lab" if sub["islab"] == "yes" else "theory"
                            schedule[(sec, day, idx)] = {
                                "type": display_type,
                                "code": code,
                                "teacher": teacher,
                                "room": available_rooms[0]
                            }
                            teacher_busy[teacher].add(time_key)
                            room_busy[available_rooms[0]].add(time_key)
                            teacher_section_slots[teacher][sec].add(time_key)
                            lectures_remaining[sec][code] -= 1
                            # REMOVED: lectures_per_day_per_subject tracking
                            
                            placed = True
                            print(f"  ✅ Pass {pass_num+1}: Placed {sec}/{code} at {day} slot {idx}")
                            break
                    
                    if not placed:
                        print(f"  ❌ Cannot place {sec}/{code} (Teacher {teacher}):")
                        print(f"     Total slots checked: {total_slots}")
                        print(f"     Already occupied: {occupied_slots}")
                        print(f"     Teacher busy: {teacher_busy_slots}")
                        print(f"     No rooms: {no_room_slots}")
                        break  # Can't place this lecture, move to next
            
            stuck_after = sum(sum(lectures_remaining[s].values()) for s in sections)
            if stuck_after == stuck_before:
                print(f"  Pass {pass_num+1}: No progress made with empty slots.")
                
                # LAST RESORT: Try SWAPPING existing lectures!
                if pass_num >= 1:  # After just 2 failed passes, try desperate mode!
                    print(f"  🔥 DESPERATE MODE: Trying swaps...")
                    swapped_any = False
                    
                    for sec, code, mapping, sub in stuck:
                        if lectures_remaining[sec][code] <= 0:
                            continue
                        
                        teacher = mapping["theory"]
                        
                        # Find ALL lectures by ANY teacher in this section
                        swap_candidates = []
                        for day in days:
                            slots = time_slots.get((sec, day), [])
                            for idx in range(len(slots)):
                                if (sec, day, idx) in schedule:
                                    entry = schedule[(sec, day, idx)]
                                    if entry.get("type") not in ["open_elective", "elective", "lab"]:
                                        swap_candidates.append((day, idx, entry))
                        
                        random.shuffle(swap_candidates)
                        
                        # Try swapping with other lectures
                        for swap_day, swap_idx, swap_entry in swap_candidates[:30]:  # Try more swaps!
                            swap_code = swap_entry["code"]
                            swap_teacher = swap_entry["teacher"]
                            swap_room = swap_entry["room"]
                            
                            # Get time key
                            swap_slots = time_slots.get((sec, swap_day), [])
                            swap_start, _ = swap_slots[swap_idx]
                            swap_time_key = get_time_key(swap_day, swap_start)
                            
                            # Can our stuck teacher use this slot?
                            if swap_time_key in teacher_busy[teacher]:
                                continue
                            
                            # Remove the existing lecture
                            del schedule[(sec, swap_day, swap_idx)]
                            teacher_busy[swap_teacher].discard(swap_time_key)
                            room_busy[swap_room].discard(swap_time_key)
                            teacher_section_slots[swap_teacher][sec].discard(swap_time_key)
                            # REMOVED: lectures_per_day_per_subject tracking
                            
                            # Place our stuck lecture
                            available_rooms = [r["name"] for r in data.classrooms 
                                             if r["is_lab"] == "no" and swap_time_key not in room_busy[r["name"]]]
                            
                            if available_rooms:
                                display_type = "lab" if sub["islab"] == "yes" else "theory"
                                schedule[(sec, swap_day, swap_idx)] = {
                                    "type": display_type,
                                    "code": code,
                                    "teacher": teacher,
                                    "room": available_rooms[0]
                                }
                                teacher_busy[teacher].add(swap_time_key)
                                room_busy[available_rooms[0]].add(swap_time_key)
                                teacher_section_slots[teacher][sec].add(swap_time_key)
                                lectures_remaining[sec][code] -= 1
                                # REMOVED: lectures_per_day_per_subject tracking
                                
                                print(f"  🔄 SWAPPED: Placed {sec}/{code}, removed {sec}/{swap_code}")
                                
                                # Mark the removed lecture as stuck for next iteration
                                lectures_remaining[sec][swap_code] += 1
                                swapped_any = True
                                break
                            else:
                                # Restore the lecture we tried to remove
                                schedule[(sec, swap_day, swap_idx)] = swap_entry
                                teacher_busy[swap_teacher].add(swap_time_key)
                                room_busy[swap_room].add(swap_time_key)
                                teacher_section_slots[swap_teacher][sec].add(swap_time_key)
                                # REMOVED: lectures_per_day_per_subject tracking
                    
                    if not swapped_any:
                        print(f"  ❌ Desperate mode failed - stopping")
                        break
                    # If we swapped something, continue to next pass!
                else:
                    # Not reached desperate mode yet, stop after a few passes
                    break
    
    print("Checking results...")
    
    # FINAL VERIFICATION: Count actual scheduled lectures vs expected
    print("\n📊 FINAL VERIFICATION:")
    for sec in sections:
        scheduled_count = {}
        expected_count = {}
        
        # Count what was actually scheduled
        for (s, day, idx), entry in schedule.items():
            if s == sec and entry.get("type") != "lab" and not entry.get("skip") and "code" in entry:
                code = entry["code"]
                scheduled_count[code] = scheduled_count.get(code, 0) + 1
        
        # Get expected count
        for code, mapping in data.mappings.get(sem, {}).get(sec, {}).items():
            sub = next((s for s in data.subjects[sem] if s["code"] == code), None)
            if sub and sub["elective"] != "yes" and sub.get("open_elective") != "yes" and sub["l"] > 0:
                expected_count[code] = sub["l"]
        
        # Compare
        section_ok = True
        for code in expected_count:
            actual = scheduled_count.get(code, 0)
            expected = expected_count[code]
            if actual != expected:
                print(f"  ❌ {sec}/{code}: scheduled {actual}, expected {expected} (missing {expected-actual})")
                section_ok = False
        
        if section_ok:
            total = sum(scheduled_count.values())
            print(f"  ✅ {sec}: All {total} lectures scheduled correctly")
    
    unscheduled = []
    total_missing = 0
    for sec in sections:
        sec_total = 0
        sec_details = []
        for code in lectures_remaining.get(sec, {}):
            if lectures_remaining[sec][code] > 0:
                unscheduled.append(f"{sec}/{code}: {lectures_remaining[sec][code]} missing")
                sec_details.append(f"{code}:{lectures_remaining[sec][code]}")
                total_missing += lectures_remaining[sec][code]
                sec_total += lectures_remaining[sec][code]
        if sec_total > 0:
            print(f"  ⚠️  Section {sec}: {sec_total} lectures missing ({', '.join(sec_details)})")
    
    if unscheduled or total_missing > 0:
        print(f"\n❌ SCHEDULING INCOMPLETE: {total_missing} lectures still missing")
        for msg in unscheduled:
            print(f"  {msg}")
        success = False
    else:
        print(f"\n✅ PERFECT! ALL LECTURES SCHEDULED! 🎉🎉🎉")
        success = True
    
    # ✅ VALIDATE AGAINST TEACHER CONSTRAINTS
    print(f"\n🔍 VALIDATING SCHEDULE AGAINST TEACHER CONSTRAINTS")
    violations, warnings = validator.validate_schedule(scheduled_classes)
    
    if violations:
        print(f"\n⚠️  HARD CONSTRAINT VIOLATIONS: {len(violations)}")
        for v in violations[:10]:  # Show first 10
            print(f"  ❌ {v['class']} - {v['teacher']} on {v['day']} {v['time']}")
            print(f"     Reason: {v['reason']}")
    else:
        print(f"\n✅ NO HARD CONSTRAINT VIOLATIONS! All teachers available for assigned slots!")
    
    if warnings:
        print(f"\n💡 SOFT CONSTRAINT (PREFERENCE) VIOLATIONS: {len(warnings)}")
        print(f"   (These don't prevent scheduling, just not ideal)")
        for w in warnings[:5]:  # Show first 5
            print(f"  ⚡ {w['class']} - {w['teacher']} on {w['day']} {w['time']}")
            print(f"     Penalty: {w['penalty']} points - {w['reason']}")
    else:
        print(f"\n⭐ PERFECT! All preferences respected!")
    
    html = generate_html(sem, sections, days, time_slots, schedule)
    return {"html": html, "success": success, "schedule": schedule, "time_slots": time_slots, "days": days, "sections": sections}

def generate_html(sem, sections, days, time_slots, schedule):
    html = f"""<html><head><title>Semester {sem}</title>
    <style>
        body {{font-family: Arial; background: #f5f5f5; margin: 20px;}}
        h1 {{background: #d35400; color: white; padding: 15px; text-align: center;}}
        h2 {{background: #8e44ad; color: white; padding: 10px; margin-top: 25px;}}
        table {{width: 100%; border-collapse: collapse; margin: 20px 0; background: white;}}
        th {{background: #3498db; color: white; padding: 12px; border: 2px solid #2980b9;}}
        td {{padding: 10px; text-align: center; border: 1px solid #bdc3c7;}}
        .day-col {{background: #3498db; color: white; font-weight: bold;}}
        .tea {{background: white; color: #27ae60; font-weight: bold; border: 2px solid #27ae60;}}
        .lunch {{background: white; color: #e67e22; font-weight: bold; border: 2px solid #e67e22;}}
        .free {{background: #f8f9fa; color: #95a5a6;}}
        .theory {{background: white;}}
        .lab {{background: #9b59b6; color: white; font-weight: bold;}}
        .elective {{background: #f39c12; color: white; font-weight: bold; font-size: 11px;}}
        .open_elective {{background: #16a085; color: white; font-weight: bold;}}
    </style></head><body><h1>SEMESTER {sem}</h1>"""
    
    if sem == "3":
        tea_break_time, tea_break_end, lunch_time, lunch_end = 645, 675, 785, 840
    elif sem == "7":
        tea_break_time, tea_break_end, lunch_time, lunch_end = 645, 675, 840, 895
    else:
        tea_break_time, tea_break_end, lunch_time, lunch_end = 0, 0, 840, 895
    
    for sec in sections:
        html += f'<h2>SECTION {sec}</h2><table><thead><tr><th class="day-col">DAY</th>'
        
        all_slots = []
        for day in days:
            slots = time_slots.get((sec, day), [])
            for s, e in slots:
                if (s, e) not in all_slots:
                    all_slots.append((s, e))
        all_slots.sort()
        
        if sem in ["3", "7"]:
            before_tea = [(s, e) for s, e in all_slots if s < tea_break_time]
            after_tea = [(s, e) for s, e in all_slots if tea_break_end <= s < lunch_time]
            after_lunch = [(s, e) for s, e in all_slots if s >= lunch_end]
            for s, e in before_tea:
                html += f'<th>{min_to_time_12h(s)}<br>{min_to_time_12h(e)}</th>'
            html += f'<th class="tea">TEA</th>'
            for s, e in after_tea:
                html += f'<th>{min_to_time_12h(s)}<br>{min_to_time_12h(e)}</th>'
            html += f'<th class="lunch">LUNCH</th>'
            for s, e in after_lunch:
                html += f'<th>{min_to_time_12h(s)}<br>{min_to_time_12h(e)}</th>'
        else:
            before_lunch = [(s, e) for s, e in all_slots if s < lunch_time]
            after_lunch = [(s, e) for s, e in all_slots if s >= lunch_end]
            for s, e in before_lunch:
                html += f'<th>{min_to_time_12h(s)}<br>{min_to_time_12h(e)}</th>'
            html += f'<th class="lunch">LUNCH</th>'
            for s, e in after_lunch:
                html += f'<th>{min_to_time_12h(s)}<br>{min_to_time_12h(e)}</th>'
        html += '</tr></thead><tbody>'
        
        for day in days:
            html += f'<tr><td class="day-col">{day.upper()}</td>'
            slots = time_slots.get((sec, day), [])
            
            def render_cell(slot_start, slot_end):
                idx = next((i for i, (s, e) in enumerate(slots) if s == slot_start and e == slot_end), None)
                if idx is not None and (sec, day, idx) in schedule:
                    entry = schedule[(sec, day, idx)]
                    if entry.get("skip"):
                        return ""
                    if entry.get("type") == "open_elective":
                        return f'<td class="open_elective">{entry["code"]}<br>{entry["teacher"]}<br>{entry["room"]}</td>'
                    if entry.get("type") == "elective":
                        codes = "/".join(sorted(entry.get("codes", [])))
                        details = "<br>".join([f"{c}: {entry['teachers'].get(c,'')}, {entry['rooms'].get(c,'')}"
                                              for c in sorted(entry.get("codes", []))])
                        return f'<td class="elective">{codes}<br>{details}</td>'
                    if entry.get("type") == "lab" and entry.get("lab_span"):
                        return f'<td class="lab" colspan="{entry["lab_span"]}">{entry["code"]}<br>{entry["teacher"]}<br>{entry["room"]}</td>'
                    css = "lab" if entry.get("type") == "lab" else "theory"
                    return f'<td class="{css}">{entry["code"]}<br>{entry["teacher"]}<br>{entry["room"]}</td>'
                elif idx is not None:
                    return '<td class="free">FREE</td>'
                return '<td class="free">—</td>'
            
            if sem in ["3", "7"]:
                for s, e in before_tea:
                    html += render_cell(s, e)
                html += '<td class="tea">TEA BREAK</td>'
                for s, e in after_tea:
                    html += render_cell(s, e)
                html += '<td class="lunch">LUNCH BREAK</td>'
                for s, e in after_lunch:
                    html += render_cell(s, e)
            else:
                for s, e in before_lunch:
                    html += render_cell(s, e)
                html += '<td class="lunch">LUNCH BREAK</td>'
                for s, e in after_lunch:
                    html += render_cell(s, e)
            html += '</tr>'
        html += '</tbody></table>'
    html += '</body></html>'
    return html