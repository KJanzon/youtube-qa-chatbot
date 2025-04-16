import os
import sys

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.youtube_processor import get_video_info

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=rfscVS0vtbw"
    info = get_video_info(url)
    print("✅ Video info:")
    for k, v in info.items():
        print(f"{k}: {v}")

def test_get_video_info():
    url = "https://www.youtube.com/watch?v=rfscVS0vtbw"  # Replace with your own test link
    info = get_video_info(url)
    
    assert isinstance(info, dict), "Output should be a dictionary"
    assert "title" in info, "Video metadata must include title"
    assert "id" in info, "Video metadata must include video ID"
    
    print("✅ Video Info:")
    for k, v in info.items():
        print(f"{k}: {v}")

#if __name__ == "__main__":
   # test_get_video_info()


