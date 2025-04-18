# 🎮  Python Tutor powered by youtube videos and Chatbot

An interactive chatbot that lets you ask natural language questions about YouTube videos — powered by LangChain, OpenAI, and ChromaDB. Specialised in Youtube videos for learning python programming. 

---

## 🚀 Features

- 🔗 Paste a YouTube video URL about Python coding and embed it directly in the app
- 🧠 Ask questions about the content using natural language
- 📖 Vector search over transcript chunks with timestamp + chapter metadata
- 📺 Plays part of the video that answers the question
- 📟 Additional explanations and coding challenge 
- 🤖 Powered by Llama3 8B + LangChain RetrievalQA

---

[📊 View Project Presentation Slides](https://docs.google.com/presentation/d/19BNzcpygXF9NgYLnCB0zwoK9xLzAMUrQvNWI1IFxeGA/edit?usp=sharing)


---

## 🛠️ Tech Stack

| Component              | Description                                                  |
|------------------------|--------------------------------------------------------------|
| **Streamlit**          | Frontend UI for chat, video player, and code interaction     |
| **LangChain**          | Retrieval-Augmented Generation (RAG) orchestration           |
| **LangSmith**          | Tracing and debugging of LLM chains and prompts              |
| **ChatGroq (LLaMA3-8B)** | LLM used for answering questions and generating challenges |
| **OpenAIEmbeddings**   | Converts transcript chunks into vector representations       |
| **ChromaDB**           | Local vector database for storing per-video embeddings       |
| **pytubefix**          | Downloads captions and extracts video metadata               |
| **GPT-4 (optional)**   | Evaluates the quality of LLaMA3 responses post-hoc           |

---

## 📦 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/KJanzon/youtube-qa-chatbot.git
   cd youtube-qa-chatbot
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_key_here
   LANGCHAIN_API_KEY
   HUGGINGFACEHUB_API_TOKEN
   GROQ_API_KEY
   ```

5. **Run the app**
   ```bash
   streamlit run interfaces/streamlit_chat.py
   ```

---

## 📁 Folder Structure

```
├── app/                  # Video processing + transcript embedding
├── data/                 # Downloaded caption files (.srt)
├── interfaces/           # Streamlit front-end
├── utils/                # Helpers (e.g., clean_srt, time utils, chapter ranker)
├── vectorstore/          # ChromaDB persistent store (per-video)
├── .env                  # API key config (excluded from Git)
```

---

## 📸 Screenshot

<img width="897" alt="Screenshot 2025-04-18 at 09 07 07" src="https://github.com/user-attachments/assets/b9031295-43fa-4d17-ab91-2dd0315312dc" />
<img width="607" alt="Screenshot 2025-04-18 at 11 54 56" src="https://github.com/user-attachments/assets/3f9816da-a618-4991-8d17-b8cbb844686c" />
<img width="597" alt="Screenshot 2025-04-18 at 11 55 03" src="https://github.com/user-attachments/assets/f523bf57-ccae-4708-9ff8-37883d611940" />


## 🧠 TODO / Roadmap

- [ ] Multi-video querying (cross-video RAG)
- [ ] Reference official python tutorial to ensure correct answers (https://docs.python.org/3/tutorial/index.html)



