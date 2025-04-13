from dotenv import load_dotenv
load_dotenv()
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from utils.clean_srt import parse_srt
from utils.time import timestamp_to_seconds



def embed_transcript(srt_path: str, persist_dir: str = "vectorstore/youtube"):
    from app.youtube_processor import extract_chapters  # moved here to break circular import

    print(f"📄 Loading transcript from: {srt_path}")
    parsed_chunks = parse_srt(srt_path)

    # Get video ID and chapters
    video_id = os.path.basename(srt_path).split("_")[0]
    chapters = extract_chapters(video_id)

    # Preprocess chapter timestamps into seconds for fast lookup
    chapters_sorted = sorted(chapters, key=lambda c: c["seconds"])

    docs = []
    for chunk in parsed_chunks:
        ts = timestamp_to_seconds(chunk["timestamp"])

        # Find current chapter (last one before this timestamp)
        current_chapter = next((c["title"] for c in reversed(chapters_sorted) if ts >= c["seconds"]), None)

        docs.append(Document(
            page_content=chunk["text"],
            metadata={
                "timestamp": chunk["timestamp"],
                "chapter_title": current_chapter or "Unknown"
            }
        ))

    print(f"✂️ Chunked {len(docs)} sections with timestamps and chapters.")

    # Embed and persist
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    vectorstore.persist()

    print(f"✅ Embedded and stored in: {persist_dir}")
    return vectorstore

if __name__ == "__main__":
    # For manual testing
    embed_transcript("data/rfscVS0vtbw_captions.srt")
