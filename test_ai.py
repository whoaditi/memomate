from ollama import chat

text = """
I need to send Rahul the project files tomorrow
and I also think we should use a recommendation
system for our college project.
"""

prompt = f"""
You are the memory extraction system for MemoMate.

Read the user's message and extract:
1. Tasks
2. Ideas
3. People
4. Important personal notes

Return ONLY valid JSON in this format:

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

print(response.message.content)