import sqlite3

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
connection.close()

print("Database ready!")