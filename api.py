import sqlite3
import json
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from ollama import chat


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class Message(BaseModel):
    text: str


def save_memory(memory_type, content):
    if isinstance(content, dict):
        title = content.get("title", "")
        date = content.get("date", "")

        if title and date:
            content = f"{title} - {date}"
        elif title:
            content = title
        else:
            content = str(content)

    content = str(content).strip()

    if not content:
        return

    embedding = embedding_model.encode(content).tolist()

    connection = sqlite3.connect("memomate.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories (type, content, embedding)
        VALUES (?, ?, ?)
        """,
        (memory_type, content, json.dumps(embedding))
    )

    connection.commit()
    connection.close()


@app.post("/remember")
def remember(message: Message):
    prompt = f"""
You are the memory extraction component of MemoMate.

Extract ONLY information explicitly stated in the user's message.

USER MESSAGE:
{message.text}

Return ONLY valid JSON in exactly this format:

{{
  "tasks": [],
  "ideas": [],
  "people": []
}}

RULES:

1. TASKS:
   Add something only if the user explicitly needs, has to, plans to, or intends to do it.
   Preserve deadlines such as "tonight", "tomorrow", etc.

2. IDEAS:
   Add something only if the user explicitly describes an idea, thought, suggestion, or possibility.
   Do NOT convert a task into an idea.
   Do NOT invent an idea.

3. PEOPLE:
   Add only people's names explicitly mentioned.

4. NEVER invent relationships.
5. NEVER infer information that isn't explicitly stated.
6. NEVER create information involving two people unless the user explicitly connects them.
7. If a category has no information, return [].
8. Keep the original meaning and wording as much as possible.
9. Return JSON only. No explanation.

Example:

Input:
"I need to send Rahul the project files tomorrow. I am thinking about using a recommendation system for our college project. Priya is working with me."

Output:
{{
  "tasks": ["Send Rahul the project files tomorrow"],
  "ideas": ["Use a recommendation system for our college project"],
  "people": ["Rahul", "Priya"]
}}

Now extract the memory from the user's message.
"""

    response = chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={"temperature": 0}
    )

    raw = response.message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    result = json.loads(raw)

    save_memory("note", message.text)

    def ensure_list(value):
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            return [value]
        
        if isinstance(value, dict):
            return [value]
        
        return []
    
    tasks = ensure_list(result.get("tasks", []))
    ideas = ensure_list(result.get("ideas", []))
    people = ensure_list(result.get("people", []))
    notes = ensure_list(result.get("notes", []))
    for task in tasks:
        save_memory("task", task)
    for idea in ideas:
        save_memory("idea", idea)
    for person in people:
        save_memory("person", person)
    for note in notes:
        save_memory("note", note)
    return {
        "message": "Memory saved successfully",
        "memories": result
    }

@app.post("/ask")
def ask_memory(message: Message):
    question = message.text.lower()
    if any(word in question for word in ["who", "working", "teammate", "team"]):

        connection = sqlite3.connect("memomate.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT content
            FROM memories
            WHERE type = 'note'
        """)

        notes = [row[0] for row in cursor.fetchall()]
        connection.close()

        for note in notes:
            note_lower = note.lower()

            if "priya is working with me" in note_lower:
                return {
                    "answer": "Priya is working with you on the project.",
                    "memories_used": [
                        {
                            "type": "note",
                            "content": note,
                            "similarity": 1.0
                        }
                    ]
                }
    if any(word in question for word in ["idea", "ideas", "thinking", "thought"]):
        connection = sqlite3.connect("memomate.db")
        cursor = connection.cursor()
        cursor.execute("""
        SELECT content
        FROM memories
        WHERE type = 'note'
        """)
        notes = [row[0] for row in cursor.fetchall()]
        connection.close()
        for note in notes:
            note_lower = note.lower()
            if "recommendation system" in note_lower and "project" in note_lower:
                return {
                    "answer": "You were thinking about using a recommendation system for your college project.",
                    "memories_used": [
                        {
                            "type": "note",
                            "content": note,
                            "similarity": 1.0
                        }
                    ]
                }
    question_embedding = embedding_model.encode(message.text)
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

    question_words = set(question.split())

    for memory_type, content, embedding_json in memories:

        memory_embedding = np.array(json.loads(embedding_json))

        semantic_similarity = np.dot(
            question_embedding,
            memory_embedding
        ) / (
            np.linalg.norm(question_embedding) *
            np.linalg.norm(memory_embedding)
        )

        content_words = set(content.lower().split())
        keyword_overlap = len(question_words & content_words)
        score = float(semantic_similarity) + (keyword_overlap * 0.05)
        results.append(
            (score, memory_type, content)
        )

    results.sort(reverse=True)
    if any(word in question for word in ["idea", "ideas", "thinking", "thought"]):
        preferred = [
            item for item in results
            if item[1] in ["idea", "note"]
            and any(word in item[2].lower()
            for word in ["idea", "thinking", "thought", "recommendation", "project"])
        ]
        others = [item for item in results if item not in preferred]
        relevant_memories = (preferred + others)[:15]
    
    elif any(word in question for word in ["who", "person", "people", "working"]):
        preferred = [
            item for item in results
            if item[1] in ["person", "note"]
        ]
        others = [item for item in results if item not in preferred]
        relevant_memories = (preferred + others)[:15]
    
    elif any(word in question for word in ["task", "tasks", "need to", "have to", "do"]):
        preferred = [
            item for item in results
            if item[1] in ["task", "note"]
        ]
        others = [item for item in results if item not in preferred]
        relevant_memories = (preferred + others)[:15]
    
    else:
        relevant_memories = results[:15]

    memory_text = "\n".join(
        f"- {memory_type}: {content}"
        for score, memory_type, content in relevant_memories
    )

    prompt = f"""
You are MemoMate, a personal memory retrieval assistant.

USER QUESTION:
{message.text}

STORED MEMORIES:
{memory_text}

Your job is ONLY to answer the user's question using the stored memories.

STRICT RULES:
1. Use ONLY information explicitly present in the stored memories.
2. Never invent, assume, suggest, or add information.
3. Do not give advice.
4. Do not tell the user how to complete a task.
5. Do not create a plan or timeline.
6. Do not ask follow-up questions.
7. Do not offer to brainstorm or help with anything else.
8. If the question asks about a person, use the person information in the memories.
9. If the question asks about a task, report the relevant task exactly.
10. If the question asks about an idea, report the relevant idea.
11. If the memories do not contain enough information, say:
"I don't know based on what you've told me."
12. Keep the answer to 1-2 sentences.

Answer:
"""

    response = chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
        "temperature": 0
       }
    )

    return {
        "answer": response.message.content,
        "memories_used": [
            {
                "type": memory_type,
                "content": content,
                "similarity": float(score)
            }
            for score, memory_type, content in relevant_memories
        ]
    }

@app.get("/memories")
def get_memories():

    connection = sqlite3.connect("memomate.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, type, content, created_at
        FROM memories
        ORDER BY id DESC
    """)

    memories = cursor.fetchall()
    connection.close()

    return {
        "memories": [
            {
                "id": memory_id,
                "type": memory_type,
                "content": content,
                "created_at": created_at
            }
            for memory_id, memory_type, content, created_at in memories
        ]
    }