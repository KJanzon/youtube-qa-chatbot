import streamlit as st
from dotenv import load_dotenv
import os
import shutil
import time
import re
import sys
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_groq import ChatGroq

from app.youtube_processor import process_and_embed_video, extract_chapters, extract_video_id
from utils.time import timestamp_to_seconds
from utils.chapters import rank_sources_by_chapter_similarity
from utils.code_runner import run_user_code

# Load environment variables
load_dotenv()

# --- Streamlit config ---
st.set_page_config(page_title="YouTube Q&A Bot", layout="wide")
st.title("🤖 YouTube Video Q&A Chatbot")

# --- Session state init ---
for key, default in {
    "video_timestamp": 0,
    "chat_history": [],
    "jump_triggered": False,
    "auto_play": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Sidebar: Input ---
video_url = st.sidebar.text_input("Paste YouTube video link:")

# Save video URL in session
if video_url and "video_url" not in st.session_state:
    st.session_state.video_url = video_url
video_url = st.session_state.get("video_url", "")

if video_url:
    try:
        video_id = extract_video_id(video_url)
        st.session_state.video_id = video_id
        persist_dir = os.path.join("vectorstore", "youtube", video_id)

        # Clear vectorstore
        if st.sidebar.button("🗑️ Clear vectorstore cache for this video"):
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir)
                time.sleep(0.5)
                os.makedirs(persist_dir, exist_ok=True)
                st.sidebar.success("🧹 Cache cleared. Reprocessing will occur on reload.")

        if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
            process_and_embed_video(video_url, persist_dir=persist_dir)
            st.sidebar.success("✅ Video processed and embedded")
        else:
            st.sidebar.info("📂 Using cached vectorstore")

        # Chapters
        chapters = extract_chapters(video_id)
        if chapters:
            st.sidebar.markdown("### 📑 Video Chapters")
            for chap in chapters:
                if st.sidebar.button(f"⏩ {chap['timestamp']} - {chap['title']}", key=f"chapter_{chap['seconds']}"):
                    st.session_state.video_timestamp = chap["seconds"]
                    st.session_state.auto_play = True
                    st.session_state.jump_triggered = True
        else:
            st.sidebar.markdown("_No chapters found in the video description._")

        # Set up retrieval
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # LLM setup
        llm = ChatGroq(model="llama3-8b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        # --- Chat input ---
        query = st.chat_input("Ask a question about the video...")

        if query:
            st.session_state.chat_history.append(("user", query))

            with st.spinner("🤖 Thinking..."):
                result = qa_chain.invoke({"query": query})
                result["source_documents"] = rank_sources_by_chapter_similarity(
                    query, result["source_documents"], chapters
                )

                # Challenge generation prompt
                # Generate a follow-up challenge that's different from the example
                assistant_answer = result["result"]

                challenge_prompt = (
                f"The user just learned from this assistant response:\n\"\"\"\n{assistant_answer}\n\"\"\"\n\n"
                f"Now, write a very short Python challenge for a beginner to test their understanding of the same concept. "
                f"⚠️ Important: Do not copy the example above. Make it different but still related. "
                f"Only output the challenge instructions in 1–2 sentences — no code or explanation."
                )
                challenge = llm.invoke(challenge_prompt).content.strip()
                st.session_state.challenge = challenge

            # Store assistant reply and sources
            st.session_state.chat_history.append(("assistant", result["result"]))
            st.session_state.last_result_docs = result["source_documents"]

            # Set jump only if it's a new query (not rerun)
            if result["source_documents"] and not st.session_state.get("jump_triggered"):
                ts = result["source_documents"][0].metadata.get("timestamp", "00:00:00")
                st.session_state.video_timestamp = timestamp_to_seconds(ts)
                st.session_state.auto_play = False

        # --- Display chat history ---
        for i, (role, msg) in enumerate(st.session_state.chat_history):
            with st.chat_message(role):
                st.write(msg)

                if role == "assistant":
                    match = re.search(r"```(?:python)?\n(.*?)```", msg, re.DOTALL)
                    if match:
                        code = match.group(1)
                        st.markdown("🧪 Try the example below:")
                        editable_code = st.text_area("📝 Edit & Run Python", value=code, height=200, key=f"code_{i}")
                        if st.button("▶️ Run Code", key=f"run_{i}"):
                            with st.spinner("Running..."):
                                output = run_user_code(editable_code)
                            st.code(output or "✅ No output", language="text")

                # Show challenge for newest assistant message
                if role == "assistant" and i == len(st.session_state.chat_history) - 1:
                    challenge = st.session_state.get("challenge", "")
                    if challenge:
                        st.markdown("🧩 Your Challenge:")
                        st.info(challenge)
                        user_solution = st.text_area("💡 Write your solution here:", height=200, key=f"solution_{i}")
                        if st.button("✅ Run My Solution", key=f"solution_run_{i}"):
                            with st.spinner("Running your solution..."):
                                output = run_user_code(user_solution)
                            st.code(output or "✅ No output", language="text")

        # --- Source documents ---
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

        # --- Video player ---
        start = st.session_state.video_timestamp
        autoplay_flag = 1 if st.session_state.auto_play else 0
        embed_url = f"https://www.youtube.com/embed/{video_id}?start={start}&autoplay={autoplay_flag}"
        st.components.v1.iframe(embed_url, height=360)

        # Reset jump flag after render
        if st.session_state.jump_triggered:
            st.session_state.jump_triggered = False

    except Exception as e:
        st.sidebar.error(str(e))
