import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rhy.db")

# Helper
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # Lets us access columns by name not just index
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and create tables if they don't exist
def init_db():
    conn = get_connection()
    # SQL commands to create tables if they don't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            title TEXT,
            created_at TEXT,
            summary TEXT DEFAULT '',
            summarized_through_id INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.commit() # Commits changes to the database/disk
    conn.close()

def create_conversation(title="New Conversation"):
    conn = get_connection()
    # '?' is a placeholder to tell the database to expect strictly a value, never as sql syntax aka SQL Injection Prevention
    cursor = conn.execute(
        "INSERT INTO conversations (title, created_at) VALUES (?, ?)", 
        (title, datetime.now().isoformat())
    )
    # Commits changes to the database/disk
    conn.commit()
    # Retrieves the ID of the newly created conversation
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def save_message(conversation_id, role, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)", 
        (conversation_id, role, content, datetime.now().isoformat())
    )
    # Commits changes to the database/disk
    conn.commit()
    conn.close()

# Builds message list for OLLAMA
def get_all_messages(conversation_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,)
    ).fetchall()
    conn.close()
    # Shape Ollama expects 
    return [{"id": row["id"], "role": row["role"], "content": row["content"]} for row in rows]

def get_summary(conversation_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT summary FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()
    conn.close()
    # Returns the summary if it exists, otherwise returns an empty string
    return row["summary"] if row["summary"] else ""

def save_summary(conversation_id, summary):
    conn = get_connection()
    conn.execute(
        "UPDATE conversations SET summary = ? WHERE id = ?",
        (summary, conversation_id)
    )
    conn.commit()
    conn.close()

def list_conversations():
    conn = get_connection()
    # DESC for newest conversation first
    rows = conn.execute(
        "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"], "created_at": row["created_at"]} for row in rows]

def get_summarized_through_id(conversation_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT summarized_through_id FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()
    conn.close()
    return row["summarized_through_id"] 

def save_summarized_through_id(conversation_id, message_id):
    conn = get_connection()
    conn.execute(
        "UPDATE conversations SET summarized_through_id = ? WHERE id = ?",
        (message_id, conversation_id)
    )
    conn.commit()
    conn.close()