import sqlite3
conn =sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts ( id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
content TEXT NOT NULL)""")

cursor.execute(
    " INSERT INTO posts (title, content) VALUES (?, ?)",
    ("MY FIRST post", " this data comes from the database")
)

conn.commit()
conn.close()

print("Database initialized successfully")