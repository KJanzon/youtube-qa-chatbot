from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import urllib.parse

VIDEO_ID = "rfscVS0vtbw"  # used for linking to timestamps

def format_youtube_link(timestamp: str) -> str:
    """Convert HH:MM:SS to YouTube seconds and return link."""
    h, m, s = map(int, timestamp.split(":"))
    total_seconds = h * 3600 + m * 60 + s
    return f"https://www.youtube.com/watch?v={VIDEO_ID}&t={total_seconds}s"

def main():
    print("📡 Loading Chroma vectorstore...")
    vectorstore = Chroma(
        persist_directory="vectorstore/youtube",
        embedding_function=OpenAIEmbeddings()
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
        retriever=retriever,
        return_source_documents=True
    )

    while True:
        query = input("\n💬 Ask a question about the video (or type 'exit'): ")
        if query.lower() in ("exit", "quit"):
            break

            # 🔍 Debug: show what was retrieved
        docs = retriever.get_relevant_documents(query)
        print(f"\n🔍 Retrieved {len(docs)} documents.")
        for i, doc in enumerate(docs[:3]):
            ts = doc.metadata.get("timestamp", "??:??:??")
            print(f"→ {i+1}. [{ts}] {doc.page_content[:100]}...")

        print("🤖 Thinking...")
        result = qa_chain.invoke({"query": query})  

        print("\n🧠 Answer:")
        print(result["result"])

        print("\n📚 Sources:")
        if result["source_documents"]:
            for doc in result["source_documents"]:
                ts = doc.metadata.get("timestamp", "??:??:??")
                link = format_youtube_link(ts)
                snippet = doc.page_content[:100].replace("\n", " ")
                print(f"→ Around [{ts}] {link}")
                print(f"   \"{snippet}...\"")
        else:
            print("No source documents returned.")


if __name__ == "__main__":
    main()
