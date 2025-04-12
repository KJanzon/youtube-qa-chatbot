import re
from typing import List, Dict

def parse_srt(srt_path: str) -> List[Dict[str, str]]:
    """Parse an .srt file and return a list of chunks with text and start time."""
    with open(srt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = raw.strip().split("\n\n")
    results = []

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue

        # Format: index, timestamp, text
        timestamp = lines[1]
        text = " ".join(lines[2:]).strip()

        # Extract just the start time (e.g., "00:01:05,900" -> "00:01:05")
        match = re.match(r"(\d{2}:\d{2}:\d{2})", timestamp)
        start_time = match.group(1) if match else "00:00:00"

        results.append({
            "text": text,
            "timestamp": start_time
        })

    return results
