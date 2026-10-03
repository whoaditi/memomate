import sqlite3

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, type, content, created_at
FROM memories
ORDER BY id DESC
""")

memories = cursor.fetchall()

for memory in memories:
    print(memory)

connection.close()