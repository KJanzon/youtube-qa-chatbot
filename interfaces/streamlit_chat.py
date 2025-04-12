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

# --- Streamlit config ---
st.set_page_config(page_title="YouTube Q&A Bot", layout="wide")
st.title("🤖 YouTube Video Q&A Chatbot")

# Initialize session state
if "video_timestamp" not in st.session_state:
    st.session_state.video_timestamp = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "jump_triggered" not in st.session_state:
    st.session_state.jump_triggered = False
if "auto_play" not in st.session_state:
    st.session_state.auto_play = False

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

# --- Sidebar: video input ---
video_url = st.sidebar.text_input("Paste YouTube video link:")

if video_url:
    video_id = extract_video_id(video_url)
    if not video_id:
        st.sidebar.error("❌ Invalid YouTube URL")
    else:
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
            st.session_state.chat_history.append(("user", query))
            with st.spinner("🤖 Thinking..."):
                result = qa_chain.invoke({"query": query})
            st.session_state.chat_history.append(("assistant", result["result"]))
            st.session_state.last_result_docs = result["source_documents"]
            if result["source_documents"]:
                ts = result["source_documents"][0].metadata.get("timestamp", "00:00:00")
                st.session_state.video_timestamp = timestamp_to_seconds(ts)
                st.session_state.auto_play = False

        # Display chat history
        for role, msg in st.session_state.chat_history:
            st.chat_message(role).write(msg)

        # Show sources with timestamps and jump buttons
        if "last_result_docs" in st.session_state:
            with st.expander("📚 Sources"):
                for i, doc in enumerate(st.session_state.last_result_docs):
                    ts = doc.metadata.get("timestamp", "00:00:00")
                    seconds = timestamp_to_seconds(ts)
                    snippet = doc.page_content[:200].replace("\n", " ")

                    col1, col2 = st.columns([1, 6])
                    with col1:
                        if st.button(f"⏩ {ts}", key=f"jump_{i}"):
                            st.session_state.video_timestamp = seconds
                            st.session_state.jump_triggered = True
                            st.session_state.auto_play = True
                    with col2:
                        st.markdown(f"_{snippet}..._")

        # Embed video LAST to reflect current timestamp
        start = st.session_state.video_timestamp
        autoplay_flag = 1 if st.session_state.auto_play else 0
        embed_url = f"https://www.youtube.com/embed/{video_id}?start={start}&autoplay={autoplay_flag}"
        st.components.v1.iframe(embed_url, height=360)

        # Reset jump trigger
        if st.session_state.jump_triggered:
            st.session_state.jump_triggered = False
