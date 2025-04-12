# tests/test_clean_srt.py
import sys
import os

# Add project root to sys.path so `utils` is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.clean_srt import parse_srt

def test_parse_srt():
    parsed = parse_srt("data/rfscVS0vtbw_captions.srt")
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    print(f"✅ Parsed {len(parsed)} blocks.")
    print("Example block:", parsed[0])

if __name__ == "__main__":
    test_parse_srt()