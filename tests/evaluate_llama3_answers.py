import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI()

# Path to file containing chat logs (one JSON per line)
INPUT_FILE = "eval/llama3_logs.jsonl"
OUTPUT_FILE = "eval/evaluation_results.jsonl"
MODEL = "gpt-4"  # or "gpt-4o"

def evaluate_response(entry):
    query = entry["query"]
    llama3_answer = entry["llama3_answer"]
    challenge = entry.get("challenge", "")
    sources = entry.get("sources", [])

    prompt = f"""
You are an expert Python evaluator. A student assistant (powered by LLaMA 3) answered a question. Evaluate their answer.

---
Question:
{query}

Student's Answer:
{llama3_answer}

Challenge Given:
{challenge}

Sources (from the video transcript):
{json.dumps(sources, indent=2)}

Please rate the assistant's answer on a scale from 1 to 5:
- Relevance (does it answer the question?)
- Accuracy (is it technically correct?)
- Clarity (is it easy to understand?)

Respond in this format:
Relevance: x/5
Accuracy: x/5
Clarity: x/5
Optional Feedback: <one-line summary>
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a Python instructor grading student responses."},
                {"role": "user", "content": prompt}
            ]
        )
        entry["evaluation"] = response.choices[0].message.content
    except Exception as e:
        entry["evaluation"] = f"Error during evaluation: {e}"

    return entry


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    # Clear output file before writing new results
    open(OUTPUT_FILE, "w").close()

    with open(INPUT_FILE, "r") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    results = []
    for i, entry in enumerate(entries):
        print(f"Evaluating entry {i+1}/{len(entries)}...")
        evaluated = evaluate_response(entry)
        results.append(evaluated)

        # Save incrementally
        with open(OUTPUT_FILE, "a") as out:
            out.write(json.dumps(evaluated) + "\n")

    print("✅ Evaluation complete. Results saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
