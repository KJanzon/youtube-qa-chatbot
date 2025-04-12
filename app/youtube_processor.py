import os
from pytubefix import YouTube

# Video setup
url = "https://www.youtube.com/watch?v=rfscVS0vtbw"
yt = YouTube(url)

print("Title:", yt.title)
print("Author:", yt.author)
print("Length (seconds):", yt.length)
print("Views:", yt.views)
print("Publish date:", yt.publish_date)
print("Thumbnail URL:", yt.thumbnail_url)

# Show available captions
print("\nAvailable captions:")
for caption in yt.captions:
    print("-", caption)

# Try grabbing English captions
caption = yt.captions.get('a.en') or yt.captions.get('en')
if caption:
    caption_text = caption.generate_srt_captions()

    # Make sure the data folder exists
    output_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a file name using the video ID
    video_id = yt.video_id
    filename = os.path.join(output_dir, f"{video_id}_captions.srt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(caption_text)

    print(f"\n✅ Captions saved to: {filename}")
else:
    print("⚠️ No English captions available.")
