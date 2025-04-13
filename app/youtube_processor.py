import os
import re
from pytubefix import YouTube
from urllib.parse import urlparse, parse_qs
from app.embed_transcript import embed_transcript



def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path.startswith(('/embed/', '/v/')):
            return parsed_url.path.split('/')[2]
    raise ValueError(f"Invalid YouTube URL: {url}")


def get_video_info(url: str) -> dict:
    """Get video metadata and return info as a dictionary."""
    video_id = extract_video_id(url)
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    return {
        "title": yt.title,
        "author": yt.author,
        "length": yt.length,
        "views": yt.views,
        "publish_date": yt.publish_date,
        "thumbnail": yt.thumbnail_url,
        "id": video_id,
    }


def save_captions(url: str, output_dir: str = "data") -> str:
    """Download and save English captions to a .srt file."""
    video_id = extract_video_id(url)
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    caption = yt.captions.get('a.en') or yt.captions.get('en')

    if caption:
        caption_text = caption.generate_srt_captions()
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{video_id}_captions.srt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(caption_text)
        return filename
    else:
        raise ValueError("⚠️ No English captions available.")


def extract_chapters(video_id: str) -> list[dict]:
    """Extract chapters from YouTube description using keywords and flexible timestamp formats."""
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    description = yt.description

    # Only check the section after "Chapters" or "Contents"
    match = re.search(r"(?i)(chapters|contents)(.*)", description, re.DOTALL)
    if not match:
        return []

    chapter_section = match.group(2)

    # Match: ⌨️ (0:00) Title  OR  0:00 Title
    pattern = r"[^\d\(]*\(?(\d{1,2}:\d{2}(?::\d{2})?)\)?[\s\-–—]*([^\n]+)"
    matches = re.findall(pattern, chapter_section)

    chapters = []
    for timestamp, title in matches:
        try:
            parts = list(map(int, timestamp.split(":")))
            seconds = parts[0]*60 + parts[1] if len(parts) == 2 else parts[0]*3600 + parts[1]*60 + parts[2]
            chapters.append({
                "timestamp": timestamp,
                "title": title.strip(") -•★⭐️⌨️").strip(),
                "seconds": seconds
            })
        except Exception:
            continue

    return chapters


def process_and_embed_video(url: str, output_dir: str = "data", persist_dir: str = "vectorstore/youtube") -> str:
    """Full pipeline: download captions, embed transcript, return video ID."""
    srt_path = save_captions(url, output_dir)
    embed_transcript(srt_path, persist_dir=persist_dir)
    return extract_video_id(url)

