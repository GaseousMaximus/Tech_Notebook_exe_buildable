# wo_manager.py
# Handles all database operations related to work orders
# This separates data logic from the GUI logic in wo_gui.py

import sqlite3
from config import DB_PATH
from parts import add_part
from database import create_connection


def _connect():
    """Return a SQLite connection object."""
    return sqlite3.connect(DB_PATH)


def _dict_from_row(cursor, row):
    """Convert a sqlite3.Row into a Python dict."""
    return {description[0]: row[idx] for idx, description in enumerate(cursor.description)}


def get_work_order_by_id(wo_id: int) -> dict | None:
    """Return a dictionary for a single work order."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # allows dict-style access to columns
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM work_orders WHERE id = ?", (wo_id,))
        row = cursor.fetchone()
        return _dict_from_row(cursor, row) if row else None
    except Exception as e:
        print(f"[ERROR] get_work_order_by_id({wo_id}): {e}")
        return None
    finally:
        conn.close()


def fetch_all_work_orders() -> list[dict]:
    """
    Fetch all work orders in the database.

    Returns a list of dictionaries, one per work order.
    """
    try:
        conn = _connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM work_orders ORDER BY created_on DESC")
        rows = cursor.fetchall()
        return [_dict_from_row(cursor, row) for row in rows]
    except Exception as e:
        print(f"[ERROR] fetch_all_work_orders: {e}")
        return []
    finally:
        conn.close()


def create_work_order(fields: dict) -> int | None:
    """
    Create a new work order with the provided fields.
    Returns the new work order ID or None if failed.
    """
    try:
        conn = _connect()
        cursor = conn.cursor()

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = tuple(fields.values())

        sql = f"INSERT INTO work_orders ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"[ERROR] create_work_order: {e}")
        return None
    finally:
        conn.close()            

    
def update_work_order(wo_id, updates):
    """Update work order fields based on a dict of updates."""
    if not updates:
        return False  # nothing to update
    
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [wo_id]
    query = f"UPDATE work_orders SET {set_clause} WHERE id = ?"
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    print("work order updated")
    return True
    

def add_part_to_db(wo_id, part_data):
    """
    Add a new part to the database.

    Parameters:
    - wo_id (int): ID of the work order the part belongs to
    - part_data (dict): Dictionary containing part fields:
        quantity, description, part_number, location, status, supplier
    """
    if not part_data.get("description"):
        raise ValueError("Description cannot be empty.")

    # Connect to DB and ensure WO exists
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM work_orders WHERE id=?", (wo_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise ValueError(f"Work order {wo_id} not found.")

    # Add part
    add_part(wo_id=wo_id, **part_data)
    print("part has been added")
    conn.close()


# wo_manager.py

def save_work_order(wo_id, updates):
    """
    Update a work order in the database.
    
    Parameters:
    - wo_id: ID of the work order to update
    - updates: dictionary of fields to update {field_name: new_value}
    
    Raises ValueError if no updates provided.
    """
    if not updates:
        raise ValueError("No fields to update.")

    import sqlite3
    from config import DB_PATH

    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [wo_id]
    query = f"UPDATE work_orders SET {set_clause} WHERE id = ?"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    print("work order has been saved")
    conn.close()


# wo_manager.py

def delete_work_order(wo_id):
    """
    Delete a work order and all related parts from the database.
    """
    import sqlite3
    from config import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete all parts linked to this work order first
    cursor.execute("DELETE FROM parts WHERE wo_id = ?", (wo_id,))

    # Then delete the work order itself
    cursor.execute("DELETE FROM work_orders WHERE id = ?", (wo_id,))

    conn.commit()
    print(f"work order has been deleted")
    conn.close()


def fetch_work_order(wo_id):
    """Helper wrapper for fetching a work order by ID."""
    return get_work_order_by_id(wo_id)
