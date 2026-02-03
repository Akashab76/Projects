# data.py - Clean and consistent
from elective_manager import ElectiveManager
import os


class Data:
    def __init__(self):
        self.teachers = []
        self.subjects = {str(i): [] for i in range(1, 9)}
        self.classrooms = []
        self.sections = {str(i): [] for i in range(1, 9)}
        self.mappings = {}
        self.timings = {}
        self.elective_manager = ElectiveManager()
        self.open_elective_schedule = {}
        
        # Load from config_data.py if it exists, otherwise use defaults
        if os.path.exists('config_data.py'):
            self._load_from_config()
        else:
            self._populate_default()
            self.save_to_file()

    def _load_from_config(self):
        """Load data from config_data.py"""
        try:
            import config_data
            import importlib
            importlib.reload(config_data)
            
            self.teachers = config_data.teachers
            self.subjects = config_data.subjects
            self.classrooms = config_data.classrooms
            self.sections = config_data.sections
            self.mappings = config_data.mappings
            self.timings = config_data.timings
            self.open_elective_schedule = config_data.open_elective_schedule
            
            print("✅ Data loaded from config_data.py!")
        except Exception as e:
            print(f"❌ Error loading config_data.py: {e}")
            print("   Loading default data instead...")
            self._populate_default()

    def save_to_file(self):
        """Save current data to config_data.py"""
        try:
            with open('config_data.py', 'w', encoding='utf-8') as f:
                f.write("# config_data.py - Auto-generated, you can edit this!\n\n")
                f.write("# ==================== TEACHERS ====================\n")
                f.write(f"teachers = {repr(self.teachers)}\n\n")
                f.write("# ==================== SUBJECTS ====================\n")
                f.write(f"subjects = {repr(self.subjects)}\n\n")
                f.write("# ==================== CLASSROOMS ====================\n")
                f.write(f"classrooms = {repr(self.classrooms)}\n\n")
                f.write("# ==================== SECTIONS ====================\n")
                f.write(f"sections = {repr(self.sections)}\n\n")
                f.write("# ==================== MAPPINGS ====================\n")
                f.write(f"mappings = {repr(self.mappings)}\n\n")
                f.write("# ==================== TIMINGS ====================\n")
                f.write(f"timings = {repr(self.timings)}\n\n")
                f.write("# ==================== OPEN ELECTIVE SCHEDULE ====================\n")
                f.write(f"open_elective_schedule = {repr(self.open_elective_schedule)}\n")
            
            print("✅ Data saved to config_data.py!")
            return True
        except Exception as e:
            print(f"❌ Error saving to config_data.py: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _populate_default(self):
        # ==================== TEACHERS ====================
        self.teachers = [
            {'name': 'MP', 'short': 'MP', 'desig': 'Associate Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'MK', 'short': 'MK', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'MD', 'short': 'MD', 'desig': 'Head Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'AG', 'short': 'AG', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'VR', 'short': 'VR', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'VH', 'short': 'VH', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SBM', 'short': 'SBM', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'NNK', 'short': 'NNK', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'SR(CHE)', 'short': 'SR(CHE)', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'SP', 'short': 'SP', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'CS', 'short': 'CS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'LBK', 'short': 'LBK', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'ARJ', 'short': 'ARJ', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'SR', 'short': 'SR', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SBS', 'short': 'SBS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'JA', 'short': 'JA', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'JS', 'short': 'JS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'NMM', 'short': 'NMM', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'MPS', 'short': 'MPS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'GS', 'short': 'GS', 'desig': 'Head Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'CV', 'short': 'CV', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SK', 'short': 'SK', 'desig': 'Associate Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SNV', 'short': 'SNV', 'desig': 'Associate Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'STN', 'short': 'STN', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'GP', 'short': 'GP', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'GSS', 'short': 'GSS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'AS', 'short': 'AS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'NMK', 'short': 'NMK', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'MS', 'short': 'MS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'KKR', 'short': 'KKR', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '11:15'},
            {'name': 'PB', 'short': 'PB', 'desig': 'Associate Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'YBM', 'short': 'YBM', 'desig': 'Associate Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SL', 'short': 'SL', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'KM', 'short': 'KM', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SA', 'short': 'SA', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SD', 'short': 'SD', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'BHL', 'short': 'BHL', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'TNS', 'short': 'TNS', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'RMR', 'short': 'RMR', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'NF1', 'short': 'NF1', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'NF2', 'short': 'NF2', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SBS', 'short': 'SBS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'JS', 'short': 'JS', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'CV', 'short': 'CV', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'MK', 'short': 'MK', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'GSS', 'short': 'GSS', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SL', 'short': 'SL', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'VH', 'short': 'VH', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'AS', 'short': 'AS', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'PB', 'short': 'PB', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SP', 'short': 'SP', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'JA', 'short': 'JA', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'SVN', 'short': 'SVN', 'desig': 'Assistant Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'RR', 'short': 'RR', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'AKP', 'short': 'AKP', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
            {'name': 'KMG', 'short': 'KMG', 'desig': 'Professor', 'credits': 16, 'start_time': '8:00'},
        ]

        # ==================== SUBJECTS ====================
        # Semester 3
        self.subjects["3"].append({'code': 'TFC', 'name': 'Theoritical Foundations of Computations', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["3"].append({'code': 'DST', 'name': 'Data Structures', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 3, 't': 0, 'p': 1})
        self.subjects["3"].append({'code': 'COA', 'name': 'Computer Organization & Architecture', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["3"].append({'code': 'DBM', 'name': 'Database Management', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 2, 't': 0, 'p': 1})
        self.subjects["3"].append({'code': 'PSM', 'name': 'Probability & Statistical Modelling', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 2, 't': 0, 'p': 1})
        self.subjects["3"].append({'code': 'OOP', 'name': 'Object Oriented Programming', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 2, 't': 0, 'p': 1})
        self.subjects["3"].append({'code': 'MML', 'name': 'Machine Learning', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 2, 't': 0, 'p': 1})

        # Semester 5
        self.subjects["5"].append({'code': 'DEL', 'name': 'Deep Learning', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 3, 't': 0, 'p': 1})
        self.subjects["5"].append({'code': 'SML', 'name': 'Statistical Modelling', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 3, 't': 0, 'p': 1})
        self.subjects["5"].append({'code': 'DAV', 'name': 'Data Analysis & Visualization', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 1, 't': 0, 'p': 1})
        self.subjects["5"].append({'code': 'KDD', 'name': 'Knowledge Discovery', 'elective': 'yes', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'IOT', 'name': 'Internet of Things', 'elective': 'yes', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'ISTM', 'name': 'Information Security &  Management', 'elective': 'yes', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'NIC', 'name': 'Nature Inspired Computing', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 2, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'CNS', 'name': 'Computer Networks', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 2, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'RMD', 'name': 'Research Methodology', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 2, 't': 0, 'p': 0})
        self.subjects["5"].append({'code': 'EVS', 'name': 'Environmental Studies', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 1, 't': 0, 'p': 0})

        # Semester 7
        self.subjects["7"].append({'code': 'TSA', 'name': 'Time Series Analysis', 'elective': 'no', 'open_elective': 'no', 'islab': 'yes', 'l': 2, 't': 0, 'p': 1})
        self.subjects["7"].append({'code': 'LLM', 'name': 'Large Language Models', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 2, 't': 0, 'p': 0})
        self.subjects["7"].append({'code': 'SNA', 'name': 'Social Network Analysis', 'elective': 'yes', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["7"].append({'code': 'CYS', 'name': 'Cyber Security', 'elective': 'yes', 'open_elective': 'no', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["7"].append({'code': 'OE-2', 'name': 'Open Elective - 2', 'elective': 'no', 'open_elective': 'yes', 'islab': 'no', 'l': 3, 't': 0, 'p': 0})
        self.subjects["7"].append({'code': 'IKL', 'name': 'Innovation & Knowledge Lab', 'elective': 'no', 'open_elective': 'no', 'islab': 'no', 'l': 1, 't': 0, 'p': 0})
        
        # ==================== CLASSROOMS ====================
        self.classrooms = [
            {'name': 'CR - 506', 'is_lab': 'no'},
            {'name': 'CR - 507', 'is_lab': 'no'},
            {'name': 'CR - 508', 'is_lab': 'no'},
            {'name': 'MEL CR-01', 'is_lab': 'no'},
            {'name': 'MEL CR-02', 'is_lab': 'no'},
            {'name': 'MEL CR-03', 'is_lab': 'no'},
            {'name': 'MEL CR-217', 'is_lab': 'no'},
            {'name': 'MEL CR-216', 'is_lab': 'no'},
            {'name': 'MEL CR-105', 'is_lab': 'no'},
            {'name': 'MEL LAB-01', 'is_lab': 'yes'},
            {'name': 'MEL LAB-02', 'is_lab': 'yes'},
            {'name': 'MEL LAB-03', 'is_lab': 'yes'},
            {'name': 'MEL-SH', 'is_lab': 'no'},
        ]

        # ==================== SECTIONS ====================
        self.sections["3"] = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.sections["5"] = ['A', 'B', 'C', 'D']
        self.sections["7"] = ['A', 'B', 'C']

        # ==================== MAPPINGS ====================
        self.mappings = {
            "3": {
                "A": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'VR', 'lab': ['VR', 'JS']},
                    "COA": {'theory': 'KKR', 'lab': []},
                    "DBM": {'theory': 'LBK', 'lab': ['LBK', 'YBM']},
                    "PSM": {'theory': 'KMG', 'lab': ['YBM', 'SR']},
                    "OOP": {'theory': 'AKP', 'lab': ['PB', 'SL']},
                    "MML": {'theory': 'YBM', 'lab': ['YBM', 'BHL']},
                },
                "B": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'SP', 'lab': ['SP', 'PB']},
                    "COA": {'theory': 'KKR', 'lab': []},
                    "DBM": {'theory': 'LBK', 'lab': ['LBK', 'RMR']},
                    "PSM": {'theory': 'KM', 'lab': ['KM', 'BHL']},
                    "OOP": {'theory': 'CV', 'lab': ['CV', 'SD']},
                    "MML": {'theory': 'CV', 'lab': ['CV', 'AS']},
                },
                "C": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'GSS', 'lab': ['GSS', 'SD']},
                    "COA": {'theory': 'SL', 'lab': []},
                    "DBM": {'theory': 'JS', 'lab': ['JS', 'CV']},
                    "PSM": {'theory': 'SBM', 'lab': ['SBM', 'BHL']},
                    "OOP": {'theory': 'RMR', 'lab': ['RMR', 'TNS']},
                    "MML": {'theory': 'SBM', 'lab': ['SBM', 'TNS']},
                },
                "D": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'GSS', 'lab': ['GSS', 'NF1']},
                    "COA": {'theory': 'SA', 'lab': []},
                    "DBM": {'theory': 'SD', 'lab': ['SD', 'AS']},
                    "PSM": {'theory': 'KM', 'lab': ['KM', 'SR']},
                    "OOP": {'theory': 'CV', 'lab': ['CV', 'BHL']},
                    "MML": {'theory': 'LBK', 'lab': ['LBK', 'NF2']},
                },
                "E": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'BHL', 'lab': ['BHL', 'SD']},
                    "COA": {'theory': 'TNS', 'lab': []},
                    "DBM": {'theory': 'YBM', 'lab': ['YBM', 'RMR']},
                    "PSM": {'theory': 'RR', 'lab': ['RR', 'SD']},
                    "OOP": {'theory': 'PB', 'lab': ['PB', 'SL']},
                    "MML": {'theory': 'RMR', 'lab': ['RMR', 'SP']},
                },
                "F": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'BHL', 'lab': ['BHL', 'NF1']},
                    "COA": {'theory': 'TNS', 'lab': []},
                    "DBM": {'theory': 'YBM', 'lab': ['YBM', 'SL']},
                    "PSM": {'theory': 'SD', 'lab': ['SD', 'VH']},
                    "OOP": {'theory': 'PB', 'lab': ['PB', 'RMR']},
                    "MML": {'theory': 'SBM', 'lab': ['SBM', 'MK']},
                },
                "G": {
                    "TFC": {'theory': 'SA', 'lab': []},
                    "DST": {'theory': 'TNS', 'lab': ['TNS', 'AS']},
                    "COA": {'theory': 'VH', 'lab': []},
                    "DBM": {'theory': 'SVN', 'lab': ['SVN', 'MK']},
                    "PSM": {'theory': 'BHL', 'lab': ['BHL', 'YBM']},
                    "OOP": {'theory': 'PB', 'lab': ['PB', 'AS']},
                    "MML": {'theory': 'BHL', 'lab': ['BHL', 'NF2']},
                },
            },
                  
            "5": {
                "A": {
                    "DEL": {'theory': 'MP', 'lab': ['MP', 'SP']},
                    "SML": {'theory': 'MK', 'lab': ['MK', 'CS']},
                    "DAV": {'theory': 'AG', 'lab': ['LBK', 'CS']},
                    "KDD": {'theory': 'VH', 'lab': []},
                    "IOT": {'theory': 'SBM', 'lab': []},
                    "ISTM": {'theory': 'NNK', 'lab': []},
                    "NIC": {'theory': 'VR', 'lab': []},
                    "CNS": {'theory': 'MD', 'lab': []},
                    "RMD": {'theory': 'SR(CHE)', 'lab': []},
                    "EVS": {'theory': 'ARJ', 'lab': []},
                },
                "B": {
                    "DEL": {'theory': 'SR', 'lab': ['SR', 'GS']},
                    "SML": {'theory': 'SBS', 'lab': ['SBS', 'CV']},
                    "DAV": {'theory': 'JA', 'lab': ['AG', 'VH']},
                    "KDD": {'theory': 'VH', 'lab': []},
                    "IOT": {'theory': 'SBM', 'lab': []},
                    "ISTM": {'theory': 'NNK', 'lab': []},
                    "NIC": {'theory': 'JS', 'lab': []},
                    "CNS": {'theory': 'MD', 'lab': []},
                    "RMD": {'theory': 'MPS', 'lab': []},
                    "EVS": {'theory': 'NMM', 'lab': []},
                },
                "C": {
                    "DEL": {'theory': 'SK', 'lab': ['SR', 'SK']},
                    "SML": {'theory': 'SBS', 'lab': ['GSS', 'CS']},
                    "DAV": {'theory': 'JA', 'lab': ['STN', 'SBM']},
                    "KDD": {'theory': 'VH', 'lab': []},
                    "IOT": {'theory': 'SBM', 'lab': []},
                    "ISTM": {'theory': 'NNK', 'lab': []},
                    "NIC": {'theory': 'LBK', 'lab': []},
                    "CNS": {'theory': 'SNV', 'lab': []},
                    "RMD": {'theory': 'MPS', 'lab': []},
                    "EVS": {'theory': 'GP', 'lab': []},
                },
                "D": {
                    "DEL": {'theory': 'CV', 'lab': ['CV', 'AG']},
                    "SML": {'theory': 'MK', 'lab': ['MK', 'AG']},
                    "DAV": {'theory': 'AS', 'lab': ['VR', 'KKR']},
                    "KDD": {'theory': 'VH', 'lab': []},
                    "IOT": {'theory': 'SBM', 'lab': []},
                    "ISTM": {'theory': 'NNK', 'lab': []},
                    "NIC": {'theory': 'GSS', 'lab': []},
                    "CNS": {'theory': 'SNV', 'lab': []},
                    "RMD": {'theory': 'MS', 'lab': []},
                    "EVS": {'theory': 'NMK', 'lab': []},
                },
            },
            "7": {
                "A": {
                    "TSA": {'theory': 'SR', 'lab': ['VH', 'MK']},
                    "LLM": {'theory': 'SBS', 'lab': []},
                    "SNA": {'theory': 'SL', 'lab': []},
                    "CYS": {'theory': 'SP', 'lab': []},
                    "OE-2": {'theory': 'SP', 'lab': []},
                    "IKL": {'theory': 'SL', 'lab': []},
                },
                "B": {
                    "TSA": {'theory': 'MK', 'lab': ['SBM', 'SR']},
                    "LLM": {'theory': 'SK', 'lab': []},
                    "SNA": {'theory': 'SL', 'lab': []},
                    "CYS": {'theory': 'SP', 'lab': []},
                    "OE-2": {'theory': 'SP', 'lab': []},
                    "IKL": {'theory': 'VH', 'lab': []},
                },
                "C": {
                    "TSA": {'theory': 'GS', 'lab': ['PB', 'YBM']},
                    "LLM": {'theory': 'MP', 'lab': []},
                    "SNA": {'theory': 'SL', 'lab': []},
                    "CYS": {'theory': 'SP', 'lab': []},
                    "OE-2": {'theory': 'SP', 'lab': []},
                    "IKL": {'theory': 'PB', 'lab': []},
                },
            },
        }

        # ==================== TIMINGS ====================
        self.timings = {
            "3": {
                "A": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "B": {
                    "Monday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "C": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "D": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "E": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "F": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Saturday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
                "G": {
                    "Monday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Tuesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Wednesday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Thursday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '13:05', 'end': '14:00'}]},
                },
            },
            "5": {
                "A": {
                    "Monday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Tuesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Wednesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Thursday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Friday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                },
                "B": {
                    "Monday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Tuesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Wednesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Thursday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Friday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Saturday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                },
                "C": {
                    "Monday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Tuesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Wednesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 4, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Thursday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Friday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Saturday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                },
                "D": {
                    "Monday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Tuesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Wednesday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Thursday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 5, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                    "Friday": {'start_time': '11:15', 'class_dur': 55, 'num_classes': 3, 'breaks': [{'start': '14:00', 'end': '14:55'}]},
                },
            },
            "7": {
                "A": {
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 7, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                },
                "B": {
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 7, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                },
                "C": {
                    "Friday": {'start_time': '8:55', 'class_dur': 55, 'num_classes': 7, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                    "Saturday": {'start_time': '8:00', 'class_dur': 55, 'num_classes': 6, 'breaks': [{'start': '10:45', 'end': '11:15'}, {'start': '14:00', 'end': '14:55'}]},
                },
            },
        }

        # ==================== OPEN ELECTIVE SCHEDULE ====================
        self.open_elective_schedule = {
            '7': {
                'A': {'OE-2': [{'day': 'Friday', 'slot_index': 0, 'room': 'CR - 506'}, {'day': 'Friday', 'slot_index': 1, 'room': 'CR - 506'}, {'day': 'Saturday', 'slot_index': 1, 'room': 'CR - 506'}]},
                'B': {'OE-2': [{'day': 'Friday', 'slot_index': 0, 'room': 'CR - 506'}, {'day': 'Friday', 'slot_index': 1, 'room': 'CR - 506'}, {'day': 'Saturday', 'slot_index': 1, 'room': 'CR - 506'}]},
                'C': {'OE-2': [{'day': 'Friday', 'slot_index': 0, 'room': 'MEL CR-105'}, {'day': 'Friday', 'slot_index': 1, 'room': 'MEL CR-105'}, {'day': 'Saturday', 'slot_index': 1, 'room': 'MEL CR-105'}]}
            }
        }