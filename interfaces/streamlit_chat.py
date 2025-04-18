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
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

from app.youtube_processor import process_and_embed_video, extract_chapters, extract_video_id
from utils.time import timestamp_to_seconds
from utils.chapters import rank_sources_by_chapter_similarity
from utils.code_runner import run_user_code

import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Custom prompt focused on Python programming
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant that answers questions about Python programming. Write a very short answer to the question, and provide an example"

---

Context:
{context}

---

User Question: {question}

Answer:
"""
)

# --- Streamlit config ---
st.set_page_config(page_title="YouTube Q&A Bot", layout="wide")
st.title("🤖 YouTube Video Q&A Chatbot")

# --- Session state init ---
for key, default in {
    "video_timestamp": 0,
    "chat_history": [],
    "jump_triggered": False,
    "auto_play": False,
    "last_result_docs_list": [],
    "challenge_list": [],
    "learn_more_open": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Sidebar: Input ---
video_url = st.sidebar.text_input("Paste YouTube video link:")

if video_url and "video_url" not in st.session_state:
    st.session_state.video_url = video_url
video_url = st.session_state.get("video_url", "")

if video_url:
    try:
        video_id = extract_video_id(video_url)
        st.session_state.video_id = video_id
        persist_dir = os.path.join("vectorstore", "youtube", video_id)

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

        chapters = extract_chapters(video_id)
        if chapters:
            st.sidebar.markdown("### 📁 Video Chapters")
            for chap in chapters:
                if st.sidebar.button(f"⏩ {chap['timestamp']} - {chap['title']}", key=f"chapter_{chap['seconds']}"):
                    st.session_state.video_timestamp = chap["seconds"]
                    st.session_state.auto_play = True
                    st.session_state.jump_triggered = True
        else:
            st.sidebar.markdown("_No chapters found in the video description._")

        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        llm = ChatGroq(model="llama3-8b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
        qa_chain = RetrievalQA(
            retriever=retriever,
            combine_documents_chain=load_qa_chain(llm, chain_type="stuff", prompt=QA_PROMPT),
            return_source_documents=True
        )

        query = st.chat_input("Ask a question about the video...")

        if query:
            st.session_state.chat_history.append(("user", query))

            with st.spinner("🤖 Thinking..."):
                result = qa_chain.invoke({"query": query})
                result["source_documents"] = rank_sources_by_chapter_similarity(
                    query, result["source_documents"], chapters
                )
                assistant_answer = result["result"]

                challenge_prompt = (
                    f"The user just learned from this assistant response:\n\"\"\"\n{assistant_answer}\n\"\"\"\n\n"
                    f"Now, write a very short Python challenge for a beginner to test their understanding of the same concept. "
                    f"⚠️ Important: Do not copy the example above. Make it different but still related. "
                    f"Only output the challenge instructions in 1–2 sentences — no code or explanation."
                )
                challenge = llm.invoke(challenge_prompt).content.strip()

            ts = result["source_documents"][0].metadata.get("timestamp", "00:00:00") if result["source_documents"] else "00:00:00"
            assistant_entry = {
                "message": assistant_answer,
                "timestamp": timestamp_to_seconds(ts)
            }
            st.session_state.chat_history.append(("assistant", assistant_entry))
            st.session_state.last_result_docs_list.append(result["source_documents"])
            st.session_state.challenge_list.append(challenge)
            st.session_state.learn_more_open.append(False)
            # ✅ Log interaction for evaluation
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "llama3_answer": assistant_answer,
                "challenge": challenge,
                "sources": [
                    {
                        "timestamp": doc.metadata.get("timestamp", ""),
                        "text": doc.page_content
                    }
                    for doc in result["source_documents"]
                ]
            }
            os.makedirs("eval", exist_ok=True)
            with open("eval/llama3_logs.jsonl", "a") as f:
                f.write(json.dumps(log_data) + "\n")


        assistant_index = 0
        for i, (role, msg) in enumerate(st.session_state.chat_history):
            with st.chat_message(role):
                if role == "user":
                    st.write(msg)
                elif role == "assistant":
                    seconds = msg["timestamp"]
                    video_id = st.session_state.get("video_id", "")
                    embed_url = f"https://www.youtube.com/embed/{video_id}?start={seconds}&autoplay=0"
                    #st.markdown(f"`[debug] video timestamp:` `{seconds}` seconds")
                    st.components.v1.iframe(embed_url, height=360)

                    if assistant_index < len(st.session_state.last_result_docs_list):
                        with st.expander("📚 Sources", expanded=False):
                            for j, doc in enumerate(st.session_state.last_result_docs_list[assistant_index]):
                                doc_ts = doc.metadata.get("timestamp", "00:00:00")
                                seconds_doc = timestamp_to_seconds(doc_ts)
                                snippet = doc.page_content[:200].replace("\n", " ")
                                col1, col2 = st.columns([1, 6])
                                with col1:
                                    if st.button(f"⏩ {doc_ts}", key=f"jump_{assistant_index}_{j}"):
                                        st.session_state.video_timestamp = seconds_doc
                                        st.session_state.jump_triggered = True
                                        st.session_state.auto_play = True
                                with col2:
                                    st.markdown(f"_{snippet}..._")

                    while len(st.session_state.learn_more_open) <= assistant_index:
                        st.session_state.learn_more_open.append(False)

                    if st.button("📚 Learn more", key=f"learn_more_btn_{assistant_index}"):
                        st.session_state.learn_more_open[assistant_index] = not st.session_state.learn_more_open[assistant_index]

                    if st.session_state.learn_more_open[assistant_index]:
                        with st.expander("💬 Assistant's Answer and Challenge", expanded=True):
                            st.markdown("### 🤖 Assistant's Answer")
                            st.write(msg["message"])

                            match = re.search(r"```(?:python)?\n(.*?)```", msg["message"], re.DOTALL)
                            if match:
                                code = match.group(1)
                                st.markdown("🧚 Try the example below:")
                                editable_code = st.text_area("🖍️ Edit & Run Python", value=code, height=200, key=f"code_{assistant_index}")
                                if st.button("▶️ Run Code", key=f"run_{assistant_index}"):
                                    with st.spinner("Running..."):
                                        output = run_user_code(editable_code)
                                    st.code(output or "✅ No output", language="text")

                            challenge = st.session_state.challenge_list[assistant_index] if assistant_index < len(st.session_state.challenge_list) else ""
                            if challenge:
                                st.markdown("### 🤩 Your Challenge")
                                st.info(challenge)
                                user_solution = st.text_area("💡 Write your solution here:", height=200, key=f"solution_{assistant_index}")
                                if st.button("✅ Run My Solution", key=f"solution_run_{assistant_index}"):
                                    with st.spinner("Running your solution..."):
                                        output = run_user_code(user_solution)
                                    st.code(output or "✅ No output", language="text")
                    assistant_index += 1

        if st.session_state.jump_triggered:
            st.session_state.jump_triggered = False

        st.components.v1.html(
            """
            <script>
            window.scrollTo(0, document.body.scrollHeight);
            </script>
            """,
            height=0,
        )

    except Exception as e:
        st.sidebar.error(str(e))
