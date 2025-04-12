from dotenv import load_dotenv
load_dotenv()
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from utils.clean_srt import parse_srt  # make sure __init__.py is present in utils/


def embed_transcript(srt_path: str, persist_dir: str = "vectorstore/youtube"):
    print(f"📄 Loading transcript from: {srt_path}")
    parsed_chunks = parse_srt(srt_path)

    docs = []
    for chunk in parsed_chunks:
        docs.append(Document(
            page_content=chunk["text"],
            metadata={"timestamp": chunk["timestamp"]}
        ))

    print(f"✂️ Chunked {len(docs)} sections with timestamps.")

    # Create embeddings
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
