# utils.py
def parse_time(t: str) -> int:
    h, m = map(int, t.split(':'))
    return h * 60 + m

def min_to_time(m: int) -> str:
    h = m // 60
    mm = m % 60
    return f"{h:02d}:{mm:02d}"

def min_to_time_12h(m: int) -> str:
    """Convert minutes since midnight to 12-hour format (e.g., 535 -> 8:55 AM)"""
    h = m // 60
    mm = m % 60
    
    if h == 0:
        return f"12:{mm:02d} AM"
    elif h < 12:
        return f"{h}:{mm:02d} AM"
    elif h == 12:
        return f"12:{mm:02d} PM"
    else:
        return f"{h-12}:{mm:02d} PM"