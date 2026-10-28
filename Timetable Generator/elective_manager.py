# elective_manager.py
class ElectiveManager:
    def __init__(self):
        self.occupied = {}
    def is_occupied(self, day, start): return self.occupied.get((day, start), False)
    def assign(self, sem, sec, sub, day, start): self.occupied[(day, start)] = True
    def clear(self): self.occupied.clear()