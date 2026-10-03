import sqlite3

connection = sqlite3.connect("memomate.db")
cursor = connection.cursor()

cursor.execute("DELETE FROM memories")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='memories'")

connection.commit()
connection.close()

print("Memory database cleared")