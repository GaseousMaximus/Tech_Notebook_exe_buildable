# --- notes.py ---
import sqlite3
from database import create_connection


def create_notes_table():
    """Ensure the notes table exists."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wo_id INTEGER,
            section TEXT,
            note_text TEXT,
            FOREIGN KEY (wo_id) REFERENCES work_orders(id) ON DELETE CASCADE
        )
    """)
    conn.commit()   
    conn.close()

def save_note(wo_id, section, note_text):
    """Insert or update a note for a specific work order and section."""
    create_notes_table() # Ensure the table exists
    conn = create_connection()
    cursor = conn.cursor()

    # Check if a note already exists for this esction
    cursor.execute(
        "SELECT id FROM notes WHERE wo_id = ? AND section = ?",
        (wo_id, section)
    )
    existing = cursor.fetchone()

    if existing:
        # Update existing note
        cursor.execute(
            "UPDATE notes SET note_text = ? WHERE id = ?",
            (note_text, existing[0]) 
        )
    else:
        # Insert new note
        cursor.execute(
            "INSERT INTO notes (wo_id, section, note_text) VALUES (?, ?, ?)",
            (wo_id, section, note_text)
        )
    
    conn.commit()
    conn.close()
    

def load_notes(wo_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT section, note_text FROM notes WHERE wo_id=?",
        (wo_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    # Convert rows into {section: note_text} dictionary
    return {section: note_text for section, note_text in rows}



# Only run if this file is executed directly
if __name__ == "__main__":
    create_notes_table()