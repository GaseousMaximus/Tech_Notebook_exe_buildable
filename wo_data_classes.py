# --- DATA CLASSES --- "wo_data_classes.py"

from PySide6.QtGui import QColor, QBrush
import sqlite3
from datetime import datetime # for auto timestamps
from database import create_connection
from config import DB_PATH


class Machine:
    def __init__(self, tag_number="", type="", make="", model="", model_number="", serial_number="", year=""):
        """
        
        Initialize a machine object.
        
        Parameters:
        - tag_number: Number on the blue plastic tag attached to the unit
        - type: Type of machine (e.g., Tractor(T), Z-Turn(Z.T.), Push Mower(P.M.), Snow Blower(S.B.), Salt Spreader(S.P), ect.)
        - make: Manufacturer (e.g., Toro, Ferris, Cub Cadet, ect.)
        - model: Model name (e.g., Titan, IS300, ect.)
        - model_number: The number on sticker tag or frame from manufacturer 
        - serial_number: The unique sn: for the machine
        - year: Year the machine was made
        """  

        self.tag_number = tag_number
        self.type = type
        self.make = make
        self.model = model
        self.model_number = model_number
        self.serial_number = serial_number
        self.year = year

    def __str__(self):
        return f"{self.year} {self.make} (SN: {self.serial_number}),Tag: {self.tag_number}"


class Engine:
    def __init__(self, make="", model="",model_number="", serial_number=""):
        """
        
        Initialize an engine object.
        
        Parameters:
        - make: Engine manufacturer
        - model: Engine model (name)
        - model_number: Engine model number
        - serial_number: Engine serial number   
        """
        self.make = make
        self.model = model
        self.model_number = model_number
        self.serial_number = serial_number
    
    def __str__(self):
        return f"Engine {self.make} {self.model} ({self.model_number}), (SN: {self.serial_number})," 
    

class WorkOrder:
    def __init__(self, wo_number, customer_first="", customer_last="", customer_tag="", machine=None, engine=None, status= "Open", created_on=None, updated_on=None):
        """
        Initialize a work order object.
        
        Parameters:
        - wo_number: Unique identifier for the work order
        - customer_first: Customer's first name
        - customer_last: Customer's last name
        - customer_tag: Customer's tag number
        - machine: Machine object associated with this work order
        - engine: Engine object associated with this work order
        - status: Work order status (default "Open")
        - created_on: Timestamp of creation (sring or datetime)
        - updated_on: Timestamp of last update (string or datetime)
        """

        self.wo_number = wo_number
        self.customer_first = customer_first
        self.customer_last = customer_last
        self.customer_tag = customer_tag
        self.machine = machine
        self.engine = engine
        self.status = status
        self.created_on = created_on if created_on else datetime.now().isoformat()
        self.updated_on = updated_on # will be set automatically when saving
        
        self.notes = []
        self.parts = [] 
    
    def days_open(self):
        created_date = datetime.fromisoformat(self.created_on)
        return (datetime.now() - created_date).days    

    def add_note(self, note_text, timestamp=None):
        """ Add a note to this work order."""
        note = {"text": note_text, "timestamp": timestamp}
        self.notes.append(note)

    def add_part(self, part):
        """ Add a part to this work order."""
        self.parts.append(part)

    def __str__(self):
        machine_info = str(self.machine) if self.machine else "No machine"
        engine_info = str(self.engine) if self.engine else "No engine"
        return (f"WorkOrder {self.wo_number} | Customer: {self.customer_last} {self.customer_first} "
                f"| Status: {self.status}\nMachine: {machine_info}\nEngine: {engine_info}\n"
                f"Notes: {len(self.notes)} | Parts: {len(self.parts)}")
    
    def save_to_db(self):
        """Save this work order, its machine, and engine to the database."""

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        self.id = cursor.lastrowid

        machine_id = None
        if self.machine:
            cursor.execute("""
                INSERT INTO machines(tag_number, type, make, model, model_number, serial_number, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.machine.tag_number,
                self.machine.type,
                self.machine.make, 
                self.machine.model, 
                self.machine.model_number,
                self.machine.serial_number,
                self.machine.year
            ))
            machine_id = cursor.lastrowid

        engine_id = None
        if self.engine:
            cursor.execute("""
                INSERT INTO engines (machine_id, make, model, model_number, serial_number)
                VALUES (?, ?, ?, ?, ?)
            """, (
                machine_id,
                self.engine.make,
                self.engine.model,
                self.engine.model_number,
                self.engine.serial_number
            ))
            engine_id = cursor.lastrowid

        self.updated_on = datetime.now().isoformat() # auto-update timestamp
                               
        cursor.execute("""
            INSERT INTO work_orders (
                wo_number, customer_first, customer_last, customer_tag, machine_id, engine_id, machine_type, machine_make,
                machine_model, machine_model_number, machine_serial_number, machine_year, engine_make, engine_model,
                engine_model_number, engine_serial_number, status, created_on, updated_on)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,? ,? ,?, ?, ?, ?, ?, ?)
        """, (            
            self.wo_number, 
            self.customer_first,
            self.customer_last,
            self.customer_tag,
            machine_id,
            engine_id,
            self.machine.type if self.machine else None,
            self.machine.make if self.machine else None,
            self.machine.model if self.machine else None,
            self.machine.model_number if self.machine else None,
            self.machine.serial_number if self.machine else None,
            self.machine.year if self.machine else None,
            self.engine.make if self.engine else None,
            self.engine.model if self.engine else None,
            self.engine.model_number if self.engine else None,
            self.engine.serial_number if self.engine else None,
            self.status,
            self.created_on, 
            self.updated_on
        ))


        # --- Save notes (if any) ---
        wo_id = cursor.lastrowid  # get the newly created work order ID
        for section_name, text_edit in getattr(self, "notes_sections", {}).items():
            text = text_edit.toPlainText().strip()
            if text:  # only save non-empty notes
                cursor.execute("""
                    INSERT INTO notes (wo_id, section, note_text)
                    VALUES (?, ?, ?)
                """, (wo_id, section_name, text))
                
                
        conn.commit()
        conn.close()
        print(f"WorkOrder {self.wo_number} save to database")

    
    def print_aligned(self):
        """Print all work order info in aligned columns for easy reading."""
        data = {
            "wo_number": self.wo_number,
            "customer_first": self.customer_first,
            "customer_last": self.customer_last,
            "status": self.status,
            "machine_type": self.machine.type if self.machine else "",
            "machine_make": self.machine.make if self.machine else "",
            "machine_model": self.machine.model if self.machine else "",
            "machine_model_number": self.machine.model_number if self.machine else "",
            "machine_serial_number": self.machine.serial_number if self.machine else "",
            "machine_year": self.machine.year if self.machine else "",
            "engine_make": self.engine.make if self.engine else "",
            "engine_model": self.engine.model if self.engine else "",
            "engine_model_number": self.engine.model_number if self.engine else "",
            "engine_serial_number": self.engine.serial_number if self.engine else "",
        }
        max_len = max(len(key) for key in data.keys())
        for key, value in data.items():
            print(f"{key.ljust(max_len)}  {value}")