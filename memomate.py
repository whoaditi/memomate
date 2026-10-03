import sqlite3
import json
from ollama import chat
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
def save_memory(memory_type, content):
    connection = sqlite3.connect("memomate.db")
    cursor = connection.cursor()

    embedding = embedding_model.encode(content).tolist()

    cursor.execute(
        "INSERT INTO memories (type, content, embedding) VALUES (?, ?, ?)",
        (memory_type, content, json.dumps(embedding))
    )

    connection.commit()
    connection.close()

text = input("What happened? ")

prompt = f"""
You are the memory extraction system for MemoMate.

Extract from the user's message:
1. Tasks
2. Ideas
3. People
4. Important personal notes

Return ONLY valid JSON:

{{
    "tasks": [],
    "ideas": [],
    "people": [],
    "notes": []
}}

User message:
{text}
"""

response = chat(
    model="gemma3:1b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

raw_response = response.message.content.strip()

print("\nAI response:")
print(raw_response)

if raw_response.startswith("```"):
    raw_response = raw_response.replace("```json", "").replace("```", "").strip()

result = json.loads(raw_response)

for task in result.get("taskes", []):
    save_memory("task", task)

for idea in result.get("ideas", []):
    save_memory("idea", idea)

for person in result.get("people", []):
    save_memory("person", person)

for note in result.get("notes", []):
    save_memory("note", note)

print("\nMemory saved successfully!")