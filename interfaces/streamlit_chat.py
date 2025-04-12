import streamlit as st
from dotenv import load_dotenv
import os
import re
from urllib.parse import urlparse, parse_qs

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

# Load environment variables
load_dotenv()

# --- Helpers ---
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ("youtu.be", "www.youtu.be"):
        return parsed_url.path[1:]
    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
        if parsed_url.path.startswith(('/embed/', '/v/')):
            return parsed_url.path.split('/')[2]
    return None

def timestamp_to_seconds(ts):
    h, m, s = map(int, ts.split(":"))
    return h * 3600 + m * 60 + s

# --- Streamlit UI ---
st.set_page_config(page_title="YouTube Q&A Bot", layout="wide")
st.title("🤖 YouTube Video Q&A Chatbot")

video_url = st.sidebar.text_input("Paste YouTube video link:")

if video_url:
    video_id = extract_video_id(video_url)
    if not video_id:
        st.sidebar.error("❌ Invalid YouTube URL")
    else:
        st.video(f"https://www.youtube.com/watch?v={video_id}")

        st.sidebar.success("✅ Video loaded")

        # Load vectorstore
        persist_dir = "vectorstore/youtube"
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # Set up LLM chain
        llm = ChatOpenAI(model_name="gpt-3.5-turbo")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        # Chat input
        query = st.chat_input("Ask a question about the video...")

        if query:
            st.chat_message("user").write(query)

            with st.spinner("🤖 Thinking..."):
                result = qa_chain.invoke({"query": query})

            st.chat_message("assistant").write(result["result"])

            # Show sources with timestamps and links
            with st.expander("📚 Sources"):
                for doc in result["source_documents"]:
                    ts = doc.metadata.get("timestamp", "00:00:00")
                    seconds = timestamp_to_seconds(ts)
                    jump_link = f"https://www.youtube.com/watch?v={video_id}&t={seconds}s"
                    snippet = doc.page_content[:200].replace("\n", " ")
                    st.markdown(f"[{ts} ▶️]({jump_link}) — _{snippet}..._", unsafe_allow_html=True)
