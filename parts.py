import sqlite3
from database import create_connection


class Part:
    def __init__(self, part_id, wo_id, quantity, description, part_number, location, our_cost=0.0, retail_cost=0.0, supplier="", status="", po_number="", ordered_on="", received_on="", pulled_on=""):
        self.part_id = part_id
        self.wo_id = wo_id
        self.quantity = quantity
        self.description = description
        self.part_number = part_number
        self.location = location
        self.our_cost = our_cost
        self.retail_cost = retail_cost
        self.supplier = supplier
        self.status = status
        self.po_number = po_number
        self.ordered_on = ordered_on
        self.received_on = received_on
        self.pulled_on = pulled_on
        
def create_parts_table():
    """Create the parts table if it doesn't exist."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            part_id INTEGER PRIMARY KEY AUTOINCREMENT,
            wo_id INTEGER,
            quantity INTEGER,
            description TEXT,
            part_number TEXT,
            location TEXT,
            our_cost REAL,
            retail_cost REAL,
            supplier TEXT,
            status TEXT,
            po_number TEXT,
            ordered_on TEXT,
            received_on TEXT,
            pulled_on TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_part(
    wo_id,
    quantity=1,
    description="",
    part_number="",
    location="",
    our_cost=0.0,
    retail_cost=0.0,
    supplier="",
    status="",
    po_number="",
    ordered_on="",
    received_on="",
    pulled_on=""
    ):
    """Add a new part to the database."""
    conn = create_connection()
    cursor = conn.cursor()

    # Round numeric costs to 2 decimal places
    our_cost = round(float(our_cost), 2)
    retail_cost = round(float(retail_cost), 2)

    cursor.execute("""
        INSERT INTO parts (
            wo_id, quantity, description, part_number, location,
            our_cost, retail_cost, supplier, status,
            po_number, ordered_on, received_on, pulled_on
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        wo_id, quantity, description, part_number, location,
        our_cost, retail_cost, supplier, status,
        po_number, ordered_on, received_on, pulled_on
    ))
    part_id = cursor.lastrowid # get the newly created part_id
    conn.commit()
    conn.close()
    return Part(
        part_id, wo_id, quantity, description, part_number, location,
        our_cost, retail_cost, supplier, status,
        po_number, ordered_on, received_on, pulled_on
    )

def get_parts_for_workorder(wo_id):
    """Return all parts associated with a workorder (placeholder for now)."""
    conn = create_connection()
    cursor = conn.cursor()
    # Example placeholder query; adjust based on your workorder table
    cursor.execute(
        """SELECT part_id, wo_id, quantity, description, part_number, location,
        our_cost, retail_cost, supplier, status,
        po_number, ordered_on, received_on, pulled_on FROM parts WHERE wo_id=?""", (wo_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Part(*row) for row in rows]

def update_part(
    part_id,
    quantity=None,
    description=None,
    part_number=None,
    location=None,
    our_cost=None,
    retail_cost=None,
    supplier=None,
    status=None,
    po_number=None,
    ordered_on=None,
    received_on=None,
    pulled_on=None
):
    """Update an existing part."""
    conn = create_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if quantity is not None:
        updates.append("quantity=?")
        values.append(quantity)
    if description is not None:
        updates.append("description=?")
        values.append(description)
    if part_number is not None:
        updates.append("part_number=?")
        values.append(part_number)
    if location is not None:
        updates.append("location=?")
        values.append(location)
    if our_cost is not None:
        updates.append("our_cost=?")
        values.append(round(float(our_cost), 2))
    if retail_cost is not None:
        updates.append("retail_cost=?")
        values.append(round(float(retail_cost), 2))
    if supplier is not None:
        updates.append("supplier=?")
        values.append(supplier)
    if status is not None:
        updates.append("status=?")
        values.append(status)
    if po_number is not None:
        updates.append("po_number=?")
        values.append(po_number)
    if ordered_on is not None:
        updates.append("ordered_on=?")
        values.append(ordered_on)
    if received_on is not None:
        updates.append("received_on=?")
        values.append(received_on)
    if pulled_on is not None:
        updates.append("pulled_on=?")
        values.append(pulled_on)

    values.append(part_id)
    if updates:
        cursor.execute(f"UPDATE parts SET {', '.join(updates)} WHERE part_id=?", values)
        conn.commit()
    conn.close()

def delete_part(part_id):
    """Delete a part from the database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parts WHERE part_id=?", (part_id,))
    conn.commit()
    conn.close()
