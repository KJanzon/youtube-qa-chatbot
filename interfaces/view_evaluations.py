import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="LLaMA3 Evaluations", layout="wide")
st.title("📊 LLaMA3 Answer Evaluations (via GPT-4)")

EVAL_FILE = "eval/evaluation_results.jsonl"

if not os.path.exists(EVAL_FILE):
    st.warning(f"No evaluations found at `{EVAL_FILE}`")
    st.stop()

# Load and parse evaluation logs
data = []
with open(EVAL_FILE, "r") as f:
    for line in f:
        try:
            row = json.loads(line)
            eval_text = row.get("evaluation", "")

            # Extract numeric scores
            relevance = accuracy = clarity = None
            for part in eval_text.split("\n"):
                if part.lower().startswith("relevance"):
                    relevance = int(part.split(":")[1].strip().split("/")[0])
                elif part.lower().startswith("accuracy"):
                    accuracy = int(part.split(":")[1].strip().split("/")[0])
                elif part.lower().startswith("clarity"):
                    clarity = int(part.split(":")[1].strip().split("/")[0])

            data.append({
                "Timestamp": row.get("timestamp"),
                "Query": row.get("query"),
                "Relevance": relevance,
                "Accuracy": accuracy,
                "Clarity": clarity,
                "Feedback": eval_text
            })
        except Exception as e:
            st.error(f"Error parsing line: {e}")

# Convert to DataFrame
df = pd.DataFrame(data)

# Show full table
st.subheader("📋 Evaluation Table")
st.dataframe(df, use_container_width=True)

# Averages
if not df.empty:
    st.subheader("📈 Average Scores")
    col1, col2, col3 = st.columns(3)
    col1.metric("Relevance", f"{df['Relevance'].mean():.2f} / 5")
    col2.metric("Accuracy", f"{df['Accuracy'].mean():.2f} / 5")
    col3.metric("Clarity", f"{df['Clarity'].mean():.2f} / 5")

    st.line_chart(df[["Relevance", "Accuracy", "Clarity"]])
