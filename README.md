# 🎮 YouTube Q&A Chatbot

An interactive Streamlit chatbot that lets you ask natural language questions about YouTube videos — powered by LangChain, OpenAI, and ChromaDB.

---

## 🚀 Features

- 🔗 Paste a YouTube video URL and embed it directly in the app
- 🧠 Ask questions about the content using natural language
- 📖 Vector search over transcript chunks with timestamp + chapter metadata
- ⏩ Clickable timestamps that jump to the exact moment in the embedded video
- 🔭 Fuzzy matching to prioritize answers from the most relevant **chapter**
- 📟 Sidebar shows **chapter titles** parsed from video description
- 🤖 Powered by OpenAI (GPT-3.5-turbo) + LangChain RetrievalQA

---

## 🛠️ Tech Stack

| Component     | Description                          |
|---------------|--------------------------------------|
| Streamlit     | UI framework                         |
| LangChain     | RAG pipeline (Retrieval-Augmented)   |
| OpenAI        | LLM + Embeddings                     |
| ChromaDB      | Vector store                         |
| pytubefix     | Captions & metadata extraction       |
| dotenv        | Secure API key loading               |

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

## 🙌 Acknowledgements

Built with ❤️ during the Ironhack Final Project by [@KJanzon](https://github.com/KJanzon)

---

## 🧠 TODO / Roadmap

- [ ] Upload your own `.srt` files manually
- [ ] Add Whisper API for automatic transcript generation
- [ ] Multi-video querying (cross-video RAG)
- [ ] LangSmith evaluation & tracing
- [ ] UI: Highlight chapter matches in chat output

