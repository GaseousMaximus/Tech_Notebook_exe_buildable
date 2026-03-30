# --- utils.py ---
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from datetime import datetime
from wo_manager import get_work_order_by_id, fetch_all_work_orders, fetch_work_order

def work_order_age_text_color(created_on_str: str) -> QColor:
    """Return text color based on how many days the work order has been open."""
    if not created_on_str:
        return QColor("white")  # default text

    try:
        created_on_dt = datetime.fromisoformat(created_on_str)
        days_open = (datetime.now() - created_on_dt).days

        if days_open <= 3:
            return QColor(0, 255, 0)    # bright green
        elif days_open <= 6:
            return QColor(255, 255, 0)  # yellow
        elif days_open <= 13:
            return QColor(255, 0, 0)    # red
        else:
            return QColor(255, 0, 255)  # magenta
    except Exception as e:
        print("[color error]", e, created_on_str)
        return QColor("white")


def format_date(created_on_str: str) -> str:
    """
    Return 'YYYY-MM-DD' or empty string if invalid.
    """
    if not created_on_str:
        return ""
    try:
        dt = datetime.strptime(created_on_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(created_on_str)

def refresh_table(table):
    table.setRowCount(0)  # clear old data

    rows = fetch_all_work_orders()
    for row_number, row_data in enumerate(rows):
        table.insertRow(row_number)
        created_on = row_data.get("created_on","")
        text_color = work_order_age_text_color(created_on)

        for col_number, key in enumerate(["id", "wo_number", "customer_last", "status", "created_on"]):
            data = row_data.get(key, "")
            data_str = data[:16] if key == "created_on" else str(data)
            item = QTableWidgetItem(data_str)
            # Set uniform dark background
            item.setBackground(QColor(0, 0, 0))
            # Set text color based on days open
            item.setForeground(text_color)
            # Make read-only
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Qt.ItemIsEditable
            table.setItem(row_number, col_number, item)


def safe_db_call(func, *args, **kwargs):
    """
    Safely call a database function with error catching.
    
    - func: the database function to call (eg., update_part, add_part, delete_part)
    - *args, **kwargs: arguments to pass to the function
    Returns the function's result or None if an error occurs.
    """
    from PySide6.QtWidgets import QMessageBox
    from datetime import datetime

    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Show user-friendly error
        QMessageBox.critical(None, "Database Error", f"An error occurred:\n{e}")
        # Log for developer
        print(f"[DB ERROR] {e}")
        with open ("error_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()} - {e}\n")
        return None
def now_time_iso() -> str:
    """
    Return the current local date/time as an ISO 8601 string with timezone offset.
    Example output: '2025-11-04T22:37:00-00-05:00'
    """
    now = datetime.now().astimezone()
    now = now.replace(microsecond=0)
    return now.isoformat()

def parse_time(time_str: str) -> datetime | None:
    """
    Convert an ISO-style timestamp string into a datetime object.
    
    Args:
        time_str (str): A string representing a date and time,
                        usually created by now_time_iso().
                        
    Returns:
        datetime | None: A datetime object if successful, or None if parsing fails.
    """
    if not time_str:
        return None
    
    try:
        # Convert the string to a datetime object.
        # Example input: "2025-11-04T22:30:00"
        # The fromisoformat() method understands the ISO format automatically.
        return datetime.fromisoformat(time_str)
    except Exception:
        # If the string is not in the correct format, fail gracefully.
        return None
    
def days_since(time_str: str) -> int:
    """
    Calculate how many days have passed since the given ISO timestamp string.
    
    Parameters:
        time_str (str): A timestamp string in ISO 8601 format,
                        e.g., '2025-11-04T21:12:00'.
                        
    Returns:
        int: Number of days between the timestamp and now.
    """
    try:
        # Convert the ISO string into a datetime object
        past_time = datetime.fromisoformat(time_str)

        # Get the current date and time
        now = datetime.now()

        # Calculate the time difference (returns a timedelta object)
        difference = now - past_time

        # Return only the number of whole days
        return difference.days
    
    except ValueError:
        # If the string isn't in proper ISO format
        print(f"[days_since] Invalid ISO time string: {time_str}")
        return 0
    

def fetch_single_work_order(wo_id):
    """
    Fetch a single work order by ID.
    
    Wraps the manager's fetch_work_order for clarity in GUI code.
    """
    return fetch_work_order(wo_id)


