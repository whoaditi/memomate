import sqlite3
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, content
FROM memories
WHERE embedding IS NULL
""")

memories = cursor.fetchall()

for memory_id, content in memories:
    embedding = model.encode(content).tolist()

    cursor.execute(
        "UPDATE memories SET embedding = ? WHERE id = ?",
        (json.dumps(embedding), memory_id)
    )

connection.commit()
connection.close()

print(f"Added embeddings to {len(memories)} old memories.")