import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "legalease.db")

def init_db():
    """Initializes the SQLite database table for legal documents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT NOT NULL,
            parties TEXT NOT NULL,
            terms TEXT,
            effective_date TEXT,
            custom_instructions TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_document(document_type: str, parties: str, terms: str, effective_date: str, custom_instructions: str, content: str) -> int:
    """Saves a generated legal document to the SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO documents (document_type, parties, terms, effective_date, custom_instructions, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (document_type, parties, terms, effective_date, custom_instructions or "", content, now_str))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def get_all_documents():
    """Retrieves all saved legal documents from the database ordered by newest first."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, document_type, parties, terms, effective_date, custom_instructions, content, created_at
        FROM documents
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    docs = [dict(row) for row in rows]
    conn.close()
    return docs

def get_document_by_id(doc_id: int):
    """Retrieves a single document by ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_document_by_id(doc_id: int) -> bool:
    """Deletes a document from the database by ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
