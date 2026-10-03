import sqlite3

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("""
ALTER TABLE memories
ADD COLUMN embedding TEXT
""")

connection.commit()
connection.close()

print("Embedding column added!")