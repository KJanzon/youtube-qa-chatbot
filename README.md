# 🎮  Python Tutor powered by youtube videos and Chatbot

An interactive chatbot that lets you ask natural language questions about YouTube videos — powered by LangChain, OpenAI, and ChromaDB. Specialised in Youtube videos for learning python programming. 

---

## 🚀 Features

- 🔗 Paste a YouTube video URL about Python coding and embed it directly in the app
- 🧠 Ask questions about the content using natural language
- 📖 Vector search over transcript chunks with timestamp + chapter metadata
- 📺 Plays part of the video that answers the question
- 📟 Additional explanations and coding challenge from a LLM
- 🤖 Powered by Llama3 8B + LangChain RetrievalQA

---

## 🛠️ Tech Stack

| Component              | Description                                                  |
|------------------------|--------------------------------------------------------------|
| **Streamlit**          | Frontend UI for chat, video player, and code interaction     |
| **LangChain**          | Retrieval-Augmented Generation (RAG) orchestration           |
| **ChatGroq (LLaMA3-8B)** | LLM used for answering questions and generating challenges |
| **OpenAIEmbeddings**   | Converts transcript chunks into vector representations       |
| **ChromaDB**           | Local vector database for storing per-video embeddings       |
| **pytubefix**          | Downloads captions and extracts video metadata               |
| **dotenv**             | Loads environment variables and API keys                     |
| **Custom Code Runner** | Executes user-submitted Python code safely                   |
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

4. **Add your OpenAI API key**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_key_here
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

_(Optional — add a screenshot here)_


---

## 🧠 TODO / Roadmap

- [ ] Multi-video querying (cross-video RAG)



