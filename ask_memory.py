import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from ollama import chat


model = SentenceTransformer("all-MiniLM-L6-v2")

question = input("Ask MemoMate: ")

question_embedding = model.encode(question)
connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
SELECT type, content, embedding
FROM memories
WHERE embedding IS NOT NULL
""")

memories = cursor.fetchall()
connection.close()

results = []

for memory_type, content, embedding_json in memories:
    memory_embedding = np.array(json.loads(embedding_json))

    similarity = np.dot(question_embedding, memory_embedding) / (
        np.linalg.norm(question_embedding) *
        np.linalg.norm(memory_embedding)
    )

    results.append((similarity, memory_type, content))

results.sort(reverse=True)

relevant_memories = results[:3]

memory_text = "\n".join(
    f"- {memory_type}: {content}"
    for similarity, memory_type, content in relevant_memories
)

prompt = f"""
You are MemoMate, a personal memory assistant.

User's question:
{question}

Relevant memories from the user's database:
{memory_text}

Answer the user's question directly using ONLY these memories.

Rules:
- Treat these memories as facts about the user's past.
- Do not invent information.
- Do not perform tasks.
- Do not claim to send messages or take actions.
- If the memories don't contain the answer, say you don't know.
- Give a short, natural answer.
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

print("\nMemoMate:")
print(response.message.content)