# 📺 YouTube Q&A Chatbot

An interactive Streamlit chatbot app that lets you ask natural language questions about a YouTube video — powered by LangChain, OpenAI, and ChromaDB.

---

## 🚀 Features

- 🔗 Paste a YouTube video URL
- 🧠 Ask questions about the video's content
- 🧾 Uses vector search over parsed transcript data (from .srt captions)
- ⏩ Clickable timestamps jump to the right moment in the embedded video
- 🤖 LLM-powered answers using OpenAI (gpt-3.5-turbo)

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) – UI framework
- [LangChain](https://www.langchain.com/) – RAG pipeline
- [OpenAI](https://platform.openai.com/) – LLM + embeddings
- [ChromaDB](https://www.trychroma.com/) – Vector storage
- [pytubefix](https://github.com/JuanBindez/pytubefix) – YouTube caption downloader

---

## 📦 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/KJanzon/youtube-qa-chatbot.git
cd youtube-qa-chatbot
```

### 2. Set up virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_key_here
```

### 5. Run the app
```bash
streamlit run interfaces/streamlit_chat.py
```

---

## 📁 Folder Structure
```
├── app/                  # Embedding + processing logic
├── data/                 # .srt files (captions)
├── interfaces/           # Streamlit UI app
├── utils/                # Helper scripts (e.g. clean_srt.py)
├── vectorstore/          # ChromaDB persistent data (excluded from Git)
├── .env                  # Your API key (excluded from Git)
```

---

## 📸 Screenshot
_(Optional — add a screenshot here of the running app)_

---

## 🙌 Acknowledgements
Built with love during the Ironhack Final Project 💙

---

## 🧠 TODO / Roadmap
- [ ] Allow uploading `.srt` files manually
- [ ] Automatic subtitle extraction
- [ ] Support for multi-video RAG
- [ ] LangSmith evaluation & tracing

