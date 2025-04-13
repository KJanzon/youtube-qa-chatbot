import streamlit as st
from dotenv import load_dotenv
import os
import shutil
from urllib.parse import urlparse, parse_qs
import time
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

from app.youtube_processor import process_and_embed_video, extract_chapters, extract_video_id
from utils.time import timestamp_to_seconds
from utils.chapters import rank_sources_by_chapter_similarity

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

# --- Sidebar: video input ---
video_url = st.sidebar.text_input("Paste YouTube video link:")

if video_url:
    try:
        video_id = extract_video_id(video_url)
        persist_dir = os.path.join("vectorstore", "youtube", video_id)

        # Button to clear cache for this video
        if st.sidebar.button("🗑️ Clear vectorstore cache for this video"):
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir)
                time.sleep(0.5)
                os.makedirs(persist_dir, exist_ok=True)
                st.sidebar.success("🧹 Cache cleared. Reprocess will occur on reload.")

        if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
            process_and_embed_video(video_url, persist_dir=persist_dir)
            st.sidebar.success("✅ Video processed and embedded")
        else:
            st.sidebar.info("📂 Using cached vectorstore")

        # Display chapters if available
        chapters = extract_chapters(video_id)
        if chapters:
            st.sidebar.markdown("### 📑 Video Chapters")
            for chap in chapters:
                if st.sidebar.button(f"⏩ {chap['timestamp']} - {chap['title']}", key=f"chapter_{chap['seconds']}"):
                    st.session_state.video_timestamp = chap["seconds"]
                    st.session_state.auto_play = True
        else:
            st.sidebar.markdown("_No chapters found in the video description._")

        # Load vectorstore
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

                  # ⬇️ Step 2: Reorder sources to prioritize relevant chapter
                result["source_documents"] = rank_sources_by_chapter_similarity(
                query, result["source_documents"], chapters)
    
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

    except Exception as e:
        st.sidebar.error(str(e))
