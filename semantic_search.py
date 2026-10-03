import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

question = input("Search MemoMate: ")

question_embedding = model.encode(question)

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, type, content, embedding
FROM memories
WHERE embedding IS NOT NULL
""")

memories = cursor.fetchall()
connection.close()


results = []

for memory_id, memory_type, content, embedding_json in memories:
    memory_embedding = np.array(json.loads(embedding_json))

    similarity = np.dot(question_embedding, memory_embedding) / (
        np.linalg.norm(question_embedding) *
        np.linalg.norm(memory_embedding)
    )

    results.append((similarity, memory_type, content))


results.sort(reverse=True)


print("\nMost relevant memories:\n")

for similarity, memory_type, content in results[:3]:
    print(f"{similarity:.3f} | {memory_type} | {content}")