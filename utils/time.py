# utils/time.py

def timestamp_to_seconds(ts: str) -> int:
    """Convert HH:MM:SS or MM:SS string into total seconds."""
    parts = list(map(int, ts.split(":")))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0
