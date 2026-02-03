import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
from collections import defaultdict, Counter
from datetime import datetime

# Try to import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class EnhancedAIAssistant:
    """Super-powered AI Assistant with advanced analytics"""
    
    def __init__(self, data):
        self.data = data
        self.api_key = ""
        self.api_provider = "openai"
        self.api_base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        self.conversation_history = []
        self.cache = {}  # Cache for expensive computations
        
    def set_api_config(self, provider, api_key, model=None, base_url=None):
        """Configure AI API settings"""
        self.api_provider = provider
        self.api_key = api_key
        if model:
            self.model = model
        if base_url:
            self.api_base_url = base_url
        elif provider == "openai":
            self.api_base_url = "https://api.openai.com/v1"
        elif provider == "anthropic":
            self.api_base_url = "https://api.anthropic.com/v1"
        elif provider == "ollama":
            self.api_base_url = "http://localhost:11434/api"
        elif provider == "grok":
            self.api_base_url = "https://api.x.ai/v1"
            if not model:
                self.model = "grok-beta"
    
    # ============ ADVANCED ANALYSIS FUNCTIONS ============
    
    def get_comprehensive_stats(self):
        """Get comprehensive timetable statistics with insights"""
        stats = {
            'teachers': self._analyze_teachers(),
            'subjects': self._analyze_subjects(),
            'classrooms': self._analyze_classrooms(),
            'workload': self._analyze_workload(),
            'distribution': self._analyze_distribution(),
            'coverage': self._analyze_coverage()
        }
        return stats
    
    def _analyze_teachers(self):
        """Detailed teacher analysis"""
        analysis = {
            'total': len(self.data.teachers),
            'by_designation': Counter(t['desig'] for t in self.data.teachers),
            'by_start_time': Counter(t['start_time'] for t in self.data.teachers),
            'avg_credits': sum(t['credits'] for t in self.data.teachers) / len(self.data.teachers) if self.data.teachers else 0,
            'most_loaded': None,
            'least_loaded': None
        }
        
        # Find most and least loaded teachers
        workload = self._calculate_teacher_workload()
        if workload:
            most = max(workload.items(), key=lambda x: x[1]['total'])
            least = min(workload.items(), key=lambda x: x[1]['total'])
            analysis['most_loaded'] = (most[0], most[1]['total'])
            analysis['least_loaded'] = (least[0], least[1]['total'])
        
        return analysis
    
    def _analyze_subjects(self):
        """Detailed subject analysis"""
        total = 0
        by_type = {'theory': 0, 'lab': 0, 'elective': 0, 'open_elective': 0, 'core': 0}
        by_semester = {}
        
        for sem, subjects in self.data.subjects.items():
            if subjects:
                by_semester[sem] = len(subjects)
                total += len(subjects)
                for sub in subjects:
                    if sub['islab'] == 'yes':
                        by_type['lab'] += 1
                    else:
                        by_type['theory'] += 1
                    
                    if sub['elective'] == 'yes':
                        by_type['elective'] += 1
                    elif sub.get('open_elective') == 'yes':
                        by_type['open_elective'] += 1
                    else:
                        by_type['core'] += 1
        
        return {
            'total': total,
            'by_type': by_type,
            'by_semester': by_semester
        }
    
    def _analyze_classrooms(self):
        """Detailed classroom analysis"""
        labs = [c for c in self.data.classrooms if c['is_lab'] == 'yes']
        regular = [c for c in self.data.classrooms if c['is_lab'] == 'no']
        
        return {
            'total': len(self.data.classrooms),
            'labs': len(labs),
            'regular': len(regular),
            'lab_names': [l['name'] for l in labs],
            'regular_names': [r['name'] for r in regular],
            'utilization': self._calculate_room_utilization()
        }
    
    def _calculate_teacher_workload(self):
        """Calculate detailed workload for each teacher"""
        workload = {}
        
        for t in self.data.teachers:
            workload[t['short']] = {
                'theory_hours': 0,
                'lab_hours': 0,
                'sections': set(),
                'subjects': set(),
                'total': 0
            }
        
        # Count from mappings
        for sem in self.data.mappings:
            for sec in self.data.mappings[sem]:
                for sub_code, mapping in self.data.mappings[sem][sec].items():
                    # Get subject details
                    sub = next((s for s in self.data.subjects[sem] if s['code'] == sub_code), None)
                    if not sub:
                        continue
                    
                    # Theory teacher
                    teacher = mapping['theory']
                    if teacher in workload:
                        workload[teacher]['theory_hours'] += sub['l']
                        workload[teacher]['sections'].add(f"S{sem}-{sec}")
                        workload[teacher]['subjects'].add(sub_code)
                    
                    # Lab teachers
                    for lab_teacher in mapping.get('lab', []):
                        if lab_teacher in workload:
                            workload[lab_teacher]['lab_hours'] += sub['p']
                            workload[lab_teacher]['sections'].add(f"S{sem}-{sec}")
                            workload[lab_teacher]['subjects'].add(sub_code)
        
        # Calculate totals
        for teacher in workload:
            workload[teacher]['total'] = workload[teacher]['theory_hours'] + workload[teacher]['lab_hours']
            workload[teacher]['sections'] = len(workload[teacher]['sections'])
            workload[teacher]['subjects'] = len(workload[teacher]['subjects'])
        
        return workload
    
    def _analyze_workload(self):
        """Analyze workload distribution and balance"""
        workload = self._calculate_teacher_workload()
        
        if not workload:
            return {'balanced': True, 'max_diff': 0, 'issues': []}
        
        loads = [w['total'] for w in workload.values() if w['total'] > 0]
        if not loads:
            return {'balanced': True, 'max_diff': 0, 'issues': []}
        
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        min_load = min(loads)
        max_diff = max_load - min_load
        
        # Check for imbalances
        issues = []
        threshold = avg_load * 0.3  # 30% deviation threshold
        
        for teacher, data in workload.items():
            if data['total'] == 0:
                issues.append(f"{teacher} has no assigned classes")
            elif data['total'] > avg_load + threshold:
                issues.append(f"{teacher} is overloaded ({data['total']} hrs vs {avg_load:.1f} avg)")
            elif data['total'] < avg_load - threshold and data['total'] > 0:
                issues.append(f"{teacher} is underloaded ({data['total']} hrs vs {avg_load:.1f} avg)")
        
        return {
            'balanced': max_diff <= threshold,
            'avg_load': avg_load,
            'max_load': max_load,
            'min_load': min_load,
            'max_diff': max_diff,
            'issues': issues
        }
    
    def _analyze_distribution(self):
        """Analyze how classes are distributed across days and times"""
        distribution = {
            'by_day': defaultdict(int),
            'by_semester': defaultdict(lambda: defaultdict(int)),
            'peak_times': [],
            'low_times': []
        }
        
        # Analyze from timings
        for sem in self.data.timings:
            for sec in self.data.timings[sem]:
                for day, config in self.data.timings[sem][sec].items():
                    num_classes = config['num_classes']
                    distribution['by_day'][day] += num_classes
                    distribution['by_semester'][sem][day] += num_classes
        
        return distribution
    
    def _analyze_coverage(self):
        """Analyze mapping coverage - are all subjects assigned?"""
        coverage = {
            'fully_mapped': [],
            'partially_mapped': [],
            'unmapped': [],
            'total_mappings': 0
        }
        
        for sem in self.data.subjects:
            for sub in self.data.subjects[sem]:
                sub_code = sub['code']
                sections = self.data.sections.get(sem, [])
                
                mapped_sections = []
                for sec in sections:
                    if sem in self.data.mappings and sec in self.data.mappings[sem]:
                        if sub_code in self.data.mappings[sem][sec]:
                            mapped_sections.append(sec)
                            coverage['total_mappings'] += 1
                
                if len(mapped_sections) == len(sections) and len(sections) > 0:
                    coverage['fully_mapped'].append(f"{sem}/{sub_code}")
                elif len(mapped_sections) > 0:
                    coverage['partially_mapped'].append(f"{sem}/{sub_code} ({len(mapped_sections)}/{len(sections)})")
                elif len(sections) > 0:
                    coverage['unmapped'].append(f"{sem}/{sub_code}")
        
        return coverage
    
    def _calculate_room_utilization(self):
        """Calculate how much each room is used"""
        utilization = {room['name']: 0 for room in self.data.classrooms}
        
        # Count from mappings (simplified)
        for sem in self.data.mappings:
            for sec in self.data.mappings[sem]:
                for sub_code, mapping in self.data.mappings[sem][sec].items():
                    # This is a rough estimate - actual utilization depends on schedule
                    # In reality, you'd need to analyze the generated timetable
                    pass
        
        return utilization
    
    # ============ CONFLICT DETECTION ============
    
    def find_conflicts(self):
        """Advanced conflict detection"""
        conflicts = {
            'teacher_conflicts': self._find_teacher_conflicts(),
            'room_conflicts': self._find_room_conflicts(),
            'timing_issues': self._find_timing_issues(),
            'workload_warnings': self._find_workload_warnings()
        }
        return conflicts
    
    def _find_teacher_conflicts(self):
        """Find teachers assigned to multiple sections simultaneously"""
        conflicts = []
        
        # Group by teacher and semester
        teacher_sections = defaultdict(lambda: defaultdict(list))
        
        for sem in self.data.mappings:
            for sec in self.data.mappings[sem]:
                for sub_code, mapping in self.data.mappings[sem][sec].items():
                    teacher = mapping['theory']
                    teacher_sections[teacher][sem].append((sec, sub_code))
                    
                    # Lab teachers too
                    for lab_teacher in mapping.get('lab', []):
                        teacher_sections[lab_teacher][sem].append((sec, f"{sub_code}-LAB"))
        
        # Check for potential conflicts (multiple sections in same semester)
        for teacher, sems in teacher_sections.items():
            for sem, assignments in sems.items():
                if len(set(a[0] for a in assignments)) > 1:  # Multiple different sections
                    sections = set(a[0] for a in assignments)
                    conflicts.append({
                        'teacher': teacher,
                        'semester': sem,
                        'sections': list(sections),
                        'count': len(assignments),
                        'severity': 'HIGH' if len(sections) > 2 else 'MEDIUM'
                    })
        
        return conflicts
    
    def _find_room_conflicts(self):
        """Find potential room allocation issues"""
        conflicts = []
        
        # Check if enough lab rooms for lab subjects
        lab_rooms = [c for c in self.data.classrooms if c['is_lab'] == 'yes']
        lab_count = 0
        
        for sem in self.data.subjects:
            for sub in self.data.subjects[sem]:
                if sub['islab'] == 'yes':
                    lab_count += 1
        
        if lab_count > len(lab_rooms) * 3:  # Rough heuristic
            conflicts.append({
                'type': 'insufficient_labs',
                'message': f"Only {len(lab_rooms)} lab rooms for {lab_count} lab subjects",
                'severity': 'HIGH'
            })
        
        return conflicts
    
    def _find_timing_issues(self):
        """Find timing configuration issues"""
        issues = []
        
        for sem in self.data.timings:
            for sec in self.data.timings[sem]:
                for day, config in self.data.timings[sem][sec].items():
                    # Check if enough slots
                    num_classes = config['num_classes']
                    if num_classes < 4:
                        issues.append({
                            'sem': sem,
                            'sec': sec,
                            'day': day,
                            'issue': f'Only {num_classes} slots scheduled',
                            'severity': 'LOW'
                        })
        
        return issues
    
    def _find_workload_warnings(self):
        """Find workload-related warnings"""
        warnings = []
        workload = self._calculate_teacher_workload()
        
        for teacher, data in workload.items():
            if data['total'] > 20:
                warnings.append({
                    'teacher': teacher,
                    'hours': data['total'],
                    'message': f"Heavy workload: {data['total']} hours",
                    'severity': 'MEDIUM'
                })
            elif data['total'] == 0:
                warnings.append({
                    'teacher': teacher,
                    'hours': 0,
                    'message': "No classes assigned",
                    'severity': 'LOW'
                })
        
        return warnings
    
    # ============ REPORT GENERATION ============
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report"""
        stats = self.get_comprehensive_stats()
        conflicts = self.find_conflicts()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          COMPREHENSIVE TIMETABLE ANALYSIS REPORT            ║
║          Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                    ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL STATISTICS
{'='*60}
Teachers:        {stats['teachers']['total']} total
                 • Assistant: {stats['teachers']['by_designation'].get('Assistant Professor', 0)}
                 • Associate: {stats['teachers']['by_designation'].get('Associate Professor', 0)}
                 • Head: {stats['teachers']['by_designation'].get('Head Professor', 0)}
                 • Avg Credits: {stats['teachers']['avg_credits']:.1f}/week

Subjects:        {stats['subjects']['total']} total
                 • Core: {stats['subjects']['by_type']['core']}
                 • Electives: {stats['subjects']['by_type']['elective']}
                 • Open Electives: {stats['subjects']['by_type']['open_elective']}
                 • Labs: {stats['subjects']['by_type']['lab']}
                 • Theory: {stats['subjects']['by_type']['theory']}

Classrooms:      {stats['classrooms']['total']} total
                 • Regular: {stats['classrooms']['regular']}
                 • Labs: {stats['classrooms']['labs']}

"""
        
        # Workload analysis
        workload = stats['workload']
        report += f"""
⚖️ WORKLOAD BALANCE
{'='*60}
Status:          {'✓ BALANCED' if workload['balanced'] else '✗ IMBALANCED'}
Average Load:    {workload.get('avg_load', 0):.1f} hours
Maximum Load:    {workload.get('max_load', 0):.0f} hours
Minimum Load:    {workload.get('min_load', 0):.0f} hours
Max Difference:  {workload.get('max_diff', 0):.1f} hours

"""
        
        if workload.get('issues'):
            report += "⚠️ WORKLOAD ISSUES:\n"
            for issue in workload['issues'][:5]:  # Show first 5
                report += f"   • {issue}\n"
            if len(workload['issues']) > 5:
                report += f"   ... and {len(workload['issues']) - 5} more\n"
            report += "\n"
        
        # Conflicts
        teacher_conflicts = conflicts['teacher_conflicts']
        if teacher_conflicts:
            report += f"""
⚠️ POTENTIAL TEACHER CONFLICTS
{'='*60}
Found {len(teacher_conflicts)} potential conflicts:

"""
            for conf in teacher_conflicts[:3]:  # Show first 3
                report += f"   • {conf['teacher']} in Sem {conf['semester']}: {conf['count']} assignments across {len(conf['sections'])} sections\n"
                report += f"     Sections: {', '.join(conf['sections'])}\n"
                report += f"     Severity: {conf['severity']}\n\n"
            
            if len(teacher_conflicts) > 3:
                report += f"   ... and {len(teacher_conflicts) - 3} more conflicts\n\n"
        else:
            report += "✓ No teacher conflicts detected\n\n"
        
        # Coverage
        coverage = stats['coverage']
        report += f"""
📋 MAPPING COVERAGE
{'='*60}
Total Mappings:     {coverage['total_mappings']}
Fully Mapped:       {len(coverage['fully_mapped'])} subjects
Partially Mapped:   {len(coverage['partially_mapped'])} subjects
Unmapped:           {len(coverage['unmapped'])} subjects

"""
        
        if coverage['unmapped']:
            report += "⚠️ UNMAPPED SUBJECTS:\n"
            for subj in coverage['unmapped'][:5]:
                report += f"   • {subj}\n"
            if len(coverage['unmapped']) > 5:
                report += f"   ... and {len(coverage['unmapped']) - 5} more\n"
            report += "\n"
        
        # Recommendations
        report += f"""
💡 RECOMMENDATIONS
{'='*60}
"""
        
        recommendations = []
        
        if not workload['balanced']:
            recommendations.append("• Rebalance teacher workload for more even distribution")
        
        if coverage['unmapped']:
            recommendations.append(f"• Complete {len(coverage['unmapped'])} unmapped subject assignments")
        
        if teacher_conflicts:
            recommendations.append(f"• Review and resolve {len(teacher_conflicts)} teacher scheduling conflicts")
        
        if stats['teachers']['most_loaded']:
            teacher, load = stats['teachers']['most_loaded']
            if load > 20:
                recommendations.append(f"• Consider reducing {teacher}'s workload ({load} hours)")
        
        if not recommendations:
            recommendations.append("• System is well-configured! No major issues found.")
        
        for rec in recommendations:
            report += f"{rec}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
    
    def generate_teacher_summary(self, teacher_short=None):
        """Generate detailed summary for specific teacher or all teachers"""
        workload = self._calculate_teacher_workload()
        
        if teacher_short:
            if teacher_short not in workload:
                return f"Teacher {teacher_short} not found or has no assignments."
            
            teacher_info = next((t for t in self.data.teachers if t['short'] == teacher_short), None)
            if not teacher_info:
                return f"Teacher {teacher_short} not found."
            
            data = workload[teacher_short]
            
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     TEACHER PROFILE                         ║
╚══════════════════════════════════════════════════════════════╝

Name:            {teacher_info['name']} ({teacher_short})
Designation:     {teacher_info['desig']}
Start Time:      {teacher_info['start_time']}
Credits/Week:    {teacher_info['credits']}

WORKLOAD SUMMARY
{'='*60}
Theory Hours:    {data['theory_hours']}
Lab Hours:       {data['lab_hours']}
Total Hours:     {data['total']}

Sections:        {data['sections']}
Subjects:        {data['subjects']}

"""
            
            # Find actual assignments
            assignments = []
            for sem in self.data.mappings:
                for sec in self.data.mappings[sem]:
                    for sub_code, mapping in self.data.mappings[sem][sec].items():
                        if mapping['theory'] == teacher_short:
                            assignments.append(f"• Sem {sem}-{sec}: {sub_code} (Theory)")
                        if teacher_short in mapping.get('lab', []):
                            assignments.append(f"• Sem {sem}-{sec}: {sub_code} (Lab)")
            
            if assignments:
                report += "ASSIGNMENTS:\n"
                for assign in sorted(assignments):
                    report += f"{assign}\n"
            
            return report
        else:
            # Summary for all teachers
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║              ALL TEACHERS WORKLOAD SUMMARY                  ║
╚══════════════════════════════════════════════════════════════╝

"""
            
            # Sort by total workload
            sorted_teachers = sorted(workload.items(), key=lambda x: x[1]['total'], reverse=True)
            
            report += f"{'Teacher':<8} {'Theory':<8} {'Lab':<8} {'Total':<8} {'Sections':<10} {'Subjects':<10}\n"
            report += "="*60 + "\n"
            
            for teacher, data in sorted_teachers:
                if data['total'] > 0:
                    report += f"{teacher:<8} {data['theory_hours']:<8} {data['lab_hours']:<8} {data['total']:<8} {data['sections']:<10} {data['subjects']:<10}\n"
            
            return report
    
    # ============ AI CHAT FUNCTIONS ============
    
    def build_system_prompt(self):
        """Build enhanced system prompt with full context"""
        stats = self.get_comprehensive_stats()
        
        prompt = f"""You are an expert timetable scheduling assistant with deep knowledge of academic scheduling.

CURRENT TIMETABLE OVERVIEW:
- Teachers: {stats['teachers']['total']} total
- Subjects: {stats['subjects']['total']} total ({stats['subjects']['by_type']['core']} core, {stats['subjects']['by_type']['elective']} electives)
- Classrooms: {stats['classrooms']['total']} ({stats['classrooms']['regular']} regular, {stats['classrooms']['labs']} labs)
- Semesters Active: {', '.join(str(s) for s in stats['subjects']['by_semester'].keys())}

WORKLOAD STATUS:
- Average Load: {stats['workload'].get('avg_load', 0):.1f} hours
- Balance Status: {'BALANCED' if stats['workload']['balanced'] else 'IMBALANCED'}
- Issues: {len(stats['workload'].get('issues', []))} found

Your role is to:
1. Answer questions about the timetable configuration
2. Provide insights on workload distribution
3. Identify potential scheduling conflicts
4. Suggest optimizations and improvements
5. Help with teacher and room assignments

Be concise, actionable, and focus on practical solutions. Use data to support your recommendations."""
        
        return prompt
    
    def chat(self, message):
        """Enhanced chat with better context"""
        if not REQUESTS_AVAILABLE:
            return "Error: 'requests' library not available. Please install it: pip install requests"
        
        # Build context
        system_prompt = self.build_system_prompt()
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            if self.api_provider == "openai":
                response = self._chat_openai(system_prompt, message)
            elif self.api_provider == "anthropic":
                response = self._chat_anthropic(system_prompt, message)
            elif self.api_provider == "grok":
                response = self._chat_grok(system_prompt, message)
            elif self.api_provider == "ollama":
                response = self._chat_ollama(system_prompt, message)
            else:
                return "Unsupported API provider"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _chat_openai(self, system_prompt, message):
        """Chat with OpenAI API"""
        url = f"{self.api_base_url}/chat/completions"
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history[-10:])  # Last 10 messages for context
        
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _chat_anthropic(self, system_prompt, message):
        """Chat with Anthropic API"""
        # Similar implementation for Anthropic
        return "Anthropic API not fully implemented yet"
    
    def _chat_ollama(self, system_prompt, message):
        """Chat with Ollama local API"""
        url = f"{self.api_base_url}/generate"
        
        full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()['response']
    
    def _chat_grok(self, system_prompt, message):
        """Chat with Grok (X.AI) API - Same format as OpenAI"""
        url = f"{self.api_base_url}/chat/completions"
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history[-10:])
        
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# ============ UI CREATION FUNCTION ============

def create_enhanced_ai_tab(parent, data):
    """Create the enhanced AI assistant tab with superior UX"""
    
    ai = EnhancedAIAssistant(data)
    
    # Main container with better layout
    main_container = ttk.Frame(parent)
    main_container.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Create notebook for different analysis views
    notebook = ttk.Notebook(main_container)
    notebook.pack(fill='both', expand=True)
    
    # ========== TAB 1: QUICK INSIGHTS ==========
    insights_frame = ttk.Frame(notebook)
    notebook.add(insights_frame, text="📊 Quick Insights")
    
    # Scrolled text for insights
    insights_text = scrolledtext.ScrolledText(insights_frame, wrap=tk.WORD, font=("Consolas", 10), height=35)
    insights_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Buttons frame
    insights_btn_frame = ttk.Frame(insights_frame)
    insights_btn_frame.pack(fill='x', padx=10, pady=(0, 10))
    
    def show_comprehensive_report():
        insights_text.delete(1.0, tk.END)
        report = ai.generate_comprehensive_report()
        insights_text.insert(1.0, report)
    
    def show_teacher_workload():
        insights_text.delete(1.0, tk.END)
        report = ai.generate_teacher_summary()
        insights_text.insert(1.0, report)
    
    def show_conflicts():
        insights_text.delete(1.0, tk.END)
        conflicts = ai.find_conflicts()
        
        output = "╔══════════════════════════════════════════════════════════════╗\n"
        output += "║                  CONFLICT ANALYSIS REPORT                   ║\n"
        output += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        # Teacher conflicts
        teacher_conf = conflicts['teacher_conflicts']
        output += f"⚠️ TEACHER CONFLICTS: {len(teacher_conf)} found\n"
        output += "="*60 + "\n"
        if teacher_conf:
            for conf in teacher_conf:
                output += f"\n• {conf['teacher']} in Semester {conf['semester']}\n"
                output += f"  Sections: {', '.join(conf['sections'])}\n"
                output += f"  Severity: {conf['severity']}\n"
        else:
            output += "✓ No teacher conflicts detected\n"
        
        output += "\n\n"
        
        # Room conflicts
        room_conf = conflicts['room_conflicts']
        output += f"🏫 ROOM CONFLICTS: {len(room_conf)} found\n"
        output += "="*60 + "\n"
        if room_conf:
            for conf in room_conf:
                output += f"\n• {conf['message']}\n"
                output += f"  Severity: {conf['severity']}\n"
        else:
            output += "✓ No room conflicts detected\n"
        
        output += "\n\n"
        
        # Workload warnings
        workload_warn = conflicts['workload_warnings']
        output += f"⚖️ WORKLOAD WARNINGS: {len(workload_warn)} found\n"
        output += "="*60 + "\n"
        if workload_warn:
            for warn in workload_warn:
                output += f"\n• {warn['teacher']}: {warn['message']}\n"
                output += f"  Severity: {warn['severity']}\n"
        else:
            output += "✓ No workload warnings\n"
        
        insights_text.insert(1.0, output)
    
    def show_recommendations():
        insights_text.delete(1.0, tk.END)
        
        stats = ai.get_comprehensive_stats()
        conflicts = ai.find_conflicts()
        
        output = "╔══════════════════════════════════════════════════════════════╗\n"
        output += "║               SMART RECOMMENDATIONS                         ║\n"
        output += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        recommendations = []
        
        # Workload recommendations
        workload = stats['workload']
        if not workload['balanced']:
            recommendations.append(("HIGH", "Workload Imbalance", 
                f"Current max difference is {workload['max_diff']:.1f} hours. Consider redistributing classes to balance teacher workload."))
        
        # Coverage recommendations
        coverage = stats['coverage']
        if coverage['unmapped']:
            recommendations.append(("HIGH", "Unmapped Subjects",
                f"{len(coverage['unmapped'])} subjects not assigned to any section. Complete these mappings."))
        
        # Teacher conflict recommendations
        if conflicts['teacher_conflicts']:
            recommendations.append(("MEDIUM", "Teacher Conflicts",
                f"{len(conflicts['teacher_conflicts'])} potential scheduling conflicts. Review teacher assignments."))
        
        # Room recommendations
        if conflicts['room_conflicts']:
            recommendations.append(("MEDIUM", "Room Allocation",
                "Potential room shortage detected. Consider adding more lab rooms or optimizing schedule."))
        
        # No issues
        if not recommendations:
            recommendations.append(("INFO", "System Status", "✓ System is well-configured! No major issues found."))
        
        # Display recommendations
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        recommendations.sort(key=lambda x: priority_order.get(x[0], 5))
        
        for priority, title, desc in recommendations:
            icon = "🔴" if priority == "HIGH" else "🟡" if priority == "MEDIUM" else "🔵" if priority == "LOW" else "✅"
            output += f"{icon} [{priority}] {title}\n"
            output += f"{'─'*60}\n"
            output += f"{desc}\n\n"
        
        insights_text.insert(1.0, output)
    
    ttk.Button(insights_btn_frame, text="📋 Full Report", command=show_comprehensive_report).pack(side='left', padx=5)
    ttk.Button(insights_btn_frame, text="👨‍🏫 Teacher Workload", command=show_teacher_workload).pack(side='left', padx=5)
    ttk.Button(insights_btn_frame, text="⚠️ Conflicts", command=show_conflicts).pack(side='left', padx=5)
    ttk.Button(insights_btn_frame, text="💡 Recommendations", command=show_recommendations).pack(side='left', padx=5)
    
    # Show initial report
    show_comprehensive_report()
    
    # ========== TAB 2: AI CHAT ==========
    chat_frame = ttk.Frame(notebook)
    notebook.add(chat_frame, text="💬 AI Chat")
    
    # API Configuration section
    config_frame = ttk.LabelFrame(chat_frame, text="⚙️ AI Configuration", padding=10)
    config_frame.pack(fill='x', padx=10, pady=10)
    
    config_grid = ttk.Frame(config_frame)
    config_grid.pack(fill='x')
    
    ttk.Label(config_grid, text="Provider:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
    provider_var = tk.StringVar(value="openai")
    provider_combo = ttk.Combobox(config_grid, textvariable=provider_var, 
                                  values=["openai", "anthropic", "grok", "ollama"], width=15)
    provider_combo.grid(row=0, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(config_grid, text="API Key:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
    api_key_var = tk.StringVar()
    api_key_entry = ttk.Entry(config_grid, textvariable=api_key_var, show="*", width=40)
    api_key_entry.grid(row=1, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(config_grid, text="Model:").grid(row=2, column=0, sticky='w', padx=5, pady=3)
    model_var = tk.StringVar(value="gpt-3.5-turbo")
    model_entry = ttk.Entry(config_grid, textvariable=model_var, width=25)
    model_entry.grid(row=2, column=1, sticky='w', padx=5, pady=3)
    
    def save_config():
        ai.set_api_config(
            provider=provider_var.get(),
            api_key=api_key_var.get(),
            model=model_var.get()
        )
        messagebox.showinfo("Success", "API configuration saved!")
    
    ttk.Button(config_grid, text="💾 Save Config", command=save_config).grid(row=0, column=2, rowspan=2, padx=10)
    
    # Chat display
    chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=("Consolas", 10), height=20)
    chat_display.pack(fill='both', expand=True, padx=10, pady=10)
    chat_display.config(state='disabled')
    
    # Configure tags
    chat_display.tag_configure("user", foreground="#2980b9", font=("Consolas", 10, "bold"))
    chat_display.tag_configure("assistant", foreground="#27ae60", font=("Consolas", 10, "bold"))
    chat_display.tag_configure("system", foreground="#7f8c8d", font=("Consolas", 10, "italic"))
    
    # Welcome message
    chat_display.config(state='normal')
    chat_display.insert(tk.END, "🤖 Enhanced AI Timetable Assistant\n", "assistant")
    chat_display.insert(tk.END, "="*60 + "\n\n", "system")
    chat_display.insert(tk.END, "I can help you with:\n", "system")
    chat_display.insert(tk.END, "• Analyzing teacher workloads and suggesting optimizations\n", "system")
    chat_display.insert(tk.END, "• Finding scheduling conflicts and proposing solutions\n", "system")
    chat_display.insert(tk.END, "• Answering questions about your timetable configuration\n", "system")
    chat_display.insert(tk.END, "• Providing strategic recommendations\n\n", "system")
    chat_display.insert(tk.END, "Configure your API above, then start chatting!\n\n", "system")
    chat_display.config(state='disabled')
    
    # Input area
    input_frame = ttk.Frame(chat_frame)
    input_frame.pack(fill='x', padx=10, pady=(0, 10))
    
    message_entry = ttk.Entry(input_frame, font=("Arial", 11))
    message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(chat_frame, textvariable=status_var, foreground="#7f8c8d")
    status_label.pack(anchor='w', padx=10)
    
    def send_message(message=None):
        if message is None:
            message = message_entry.get().strip()
        
        if not message:
            return
        
        if not api_key_var.get() and provider_var.get() != "ollama":
            messagebox.showwarning("API Key Required", "Please configure your API key first.")
            return
        
        # Display user message
        chat_display.config(state='normal')
        chat_display.insert(tk.END, "You: ", "user")
        chat_display.insert(tk.END, message + "\n\n")
        chat_display.config(state='disabled')
        chat_display.see(tk.END)
        
        message_entry.delete(0, tk.END)
        status_var.set("Thinking...")
        
        def get_response():
            try:
                response = ai.chat(message)
                
                def update_ui():
                    chat_display.config(state='normal')
                    chat_display.insert(tk.END, "Assistant: ", "assistant")
                    chat_display.insert(tk.END, response + "\n\n")
                    chat_display.config(state='disabled')
                    chat_display.see(tk.END)
                    status_var.set("Ready")
                
                parent.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    chat_display.config(state='normal')
                    chat_display.insert(tk.END, f"Error: {str(e)}\n\n", "system")
                    chat_display.config(state='disabled')
                    status_var.set("Error")
                
                parent.after(0, show_error)
        
        thread = threading.Thread(target=get_response, daemon=True)
        thread.start()
    
    send_btn = ttk.Button(input_frame, text="Send 📤", command=send_message, width=12)
    send_btn.pack(side='right')
    
    message_entry.bind('<Return>', lambda e: send_message())
    
    # ========== TAB 3: TEACHER LOOKUP ==========
    teacher_frame = ttk.Frame(notebook)
    notebook.add(teacher_frame, text="👨‍🏫 Teacher Lookup")
    
    lookup_container = ttk.Frame(teacher_frame)
    lookup_container.pack(fill='both', expand=True, padx=10, pady=10)
    
    ttk.Label(lookup_container, text="Select Teacher:", font=("Arial", 12, "bold")).pack(anchor='w', pady=5)
    
    teacher_var = tk.StringVar()
    teacher_combo = ttk.Combobox(lookup_container, textvariable=teacher_var, width=30)
    teacher_combo['values'] = [t['short'] for t in data.teachers]
    teacher_combo.pack(anchor='w', pady=5)
    
    teacher_display = scrolledtext.ScrolledText(lookup_container, wrap=tk.WORD, font=("Consolas", 10), height=30)
    teacher_display.pack(fill='both', expand=True, pady=10)
    
    def show_teacher_info():
        teacher = teacher_var.get()
        if not teacher:
            messagebox.showwarning("Selection Required", "Please select a teacher.")
            return
        
        teacher_display.delete(1.0, tk.END)
        info = ai.generate_teacher_summary(teacher)
        teacher_display.insert(1.0, info)
    
    ttk.Button(lookup_container, text="📊 Show Details", command=show_teacher_info).pack(anchor='w', pady=5)
    
    return main_container