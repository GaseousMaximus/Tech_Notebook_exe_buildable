# --- wo_gui.py ---
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox, QPushButton, 
    QMessageBox, QComboBox, QTableWidget, QTableWidgetItem, QWidget, QLabel, 
    QScrollArea, QStackedWidget, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont 

from wo_manager import fetch_work_order, update_work_order
from parts import get_parts_for_workorder
from notes import load_notes
from wo_print import generate_wo_pdf
from plist_gui import PartsListWindow
from wo_data_classes import WorkOrder, Machine, Engine
from config import DB_FILE
from utils import safe_db_call


class WorkOrderDetailWindow(QWidget):
    """Work Order Detail GUI for editing/viewing a single work order."""

    work_order_deleted = Signal()
    work_order_saved = Signal()
    
    def __init__(self, wo_id):
        super().__init__()
        self.wo_id = wo_id
        self.setWindowTitle(f"Work Order #{wo_id}")
        self.resize(1200, 900)

        # --- Load Work Order Data ---
        self.wo_data = fetch_work_order(wo_id)
        print("Work order data is loaded")

        # --- Main layout ---
        self.layout = QVBoxLayout(self)
        print("Main layout done")

        # --- Scrollable area setup ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        self.font = QFont()
        self.font.setPointSize(16)

        self.content_widget.setStyleSheet("""
            QLabel { font-size: 14pt; }
            QLineEdit, QComboBox, QSpinBox { font-size: 14pt; min-height: 36px; padding: 4px; }
            QPushButton { font-size: 14pt; min-height: 40px; padding: 6px 10px; }
        """)

        # --- Build form fields ---
        self.build_form_fields()
        print("Fields have been built")

        # --- Notes sections ---
        self.build_notes_sections()
        self.load_notes_from_db()
        print("Notes built and loaded")

        # --- Buttons layout ---
        self.build_buttons()
        print("Buttons built")

    # ---------------------- Form Fields ----------------------
    def build_form_fields(self):
        # --- WO Number ---
        self.content_layout.addWidget(QLabel("WO Number:"))
        wo_number_value = self.wo_data.get('wo_number', '') if self.wo_data else ''
        self.wo_number_input = QLineEdit(str(wo_number_value))
        self.wo_number_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.wo_number_input)

        # --- Status ---
        self.content_layout.addWidget(QLabel("Status:"))
        status_value = self.wo_data.get('status', '') if self.wo_data else ''
        self.status_input = QLineEdit(status_value)
        self.status_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.status_input)

        # --- Customer Name ---
        self.content_layout.addWidget(QLabel("First Name:"))
        customer_first_value = self.wo_data.get('customer_first', '') if self.wo_data else ''
        self.customer_first_input = QLineEdit(customer_first_value)
        self.customer_first_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.customer_first_input)

        self.content_layout.addWidget(QLabel("Last Name:"))
        customer_last_value = self.wo_data.get('customer_last', '') if self.wo_data else ''
        self.customer_last_input = QLineEdit(customer_last_value)
        self.customer_last_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.customer_last_input)

        # --- Machine Fields ---
        self.add_machine_fields()

        # --- Engine Fields ---
        self.add_engine_fields()

    def add_machine_fields(self):
        # Type
        self.content_layout.addWidget(QLabel("Machine Type:"))
        machine_type_value = self.wo_data.get('machine_type', '') if self.wo_data else ''
        self.machine_type_input = QLineEdit(machine_type_value)
        self.machine_type_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.machine_type_input)

        # Make
        self.content_layout.addWidget(QLabel("Machine Make:"))
        machine_make_value = self.wo_data.get('machine_make', '') if self.wo_data else ''
        self.machine_make_input = QLineEdit(machine_make_value)
        self.machine_make_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.machine_make_input)

        # Model
        self.content_layout.addWidget(QLabel("Machine Model:"))
        machine_model_value = self.wo_data.get('machine_model', '') if self.wo_data else ''
        self.machine_model_input = QLineEdit(machine_model_value)
        self.machine_model_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.machine_model_input)

        # Model Number
        self.content_layout.addWidget(QLabel("Machine Model Number:"))
        machine_model_number_value = self.wo_data.get('machine_model_number', '') if self.wo_data else ''
        self.machine_model_number_input = QLineEdit(machine_model_number_value)
        self.machine_model_number_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.machine_model_number_input)

        # Serial Number
        self.content_layout.addWidget(QLabel("Machine Serial Number:"))
        machine_serial_number_value = self.wo_data.get('machine_serial_number', '') if self.wo_data else ''
        self.machine_serial_number_input = QLineEdit(machine_serial_number_value)
        self.machine_serial_number_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.machine_serial_number_input)

        # Year
        self.content_layout.addWidget(QLabel("Machine Year:"))
        machine_year_value = self.wo_data.get('machine_year', '') if self.wo_data else ''
        self.machine_year_input = QLineEdit()
        self.machine_year_input.setText(str(machine_year_value))
        self.machine_year_input.setFixedHeight(40)
        self.content_layout.addWidget(self.machine_year_input)

    def add_engine_fields(self):
        # Make
        self.content_layout.addWidget(QLabel("Engine Make:"))
        engine_make_value = self.wo_data.get('engine_make', '') if self.wo_data else ''
        self.engine_make_input = QLineEdit(engine_make_value)
        self.engine_make_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.engine_make_input)

        # Model
        self.content_layout.addWidget(QLabel("Engine Model:"))
        engine_model_value = self.wo_data.get('engine_model', '') if self.wo_data else ''
        self.engine_model_input = QLineEdit(engine_model_value)
        self.engine_model_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.engine_model_input)

        # Model Number
        self.content_layout.addWidget(QLabel("Engine Model Number:"))
        engine_model_number_value = self.wo_data.get('engine_model_number', '') if self.wo_data else ''
        self.engine_model_number_input = QLineEdit(engine_model_number_value)
        self.engine_model_number_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.engine_model_number_input)

        # Serial Number
        self.content_layout.addWidget(QLabel("Engine Serial Number:"))
        engine_serial_number_value = self.wo_data.get('engine_serial_number', '') if self.wo_data else ''
        self.engine_serial_number_input = QLineEdit(engine_serial_number_value)
        self.engine_serial_number_input.setMinimumHeight(40)
        self.content_layout.addWidget(self.engine_serial_number_input)

    # ---------------------- Notes Sections ----------------------
    def build_notes_sections(self):
        self.notes_sections = {}
        for section_name, label_text in [
            ('service_requested', "Service Requested"),
            ('diagnosis', "Diagnosis"),
            ('work_notes', "Work Notes / Labor Tracking"),
            ('test_run', "Test Run / Wrap-Up Notes")
        ]:
            self.content_layout.addWidget(QLabel(label_text))
            text_edit = QTextEdit()
            text_edit.setPlaceholderText(f"Enter {label_text} here...")
            text_edit.setMinimumHeight(100)
            self.content_layout.addWidget(text_edit)
            self.notes_sections[section_name] = text_edit
            print("Notes build complete")

        
    # ---------------------- Buttons ----------------------
    def build_buttons(self):
        """Create all buttons for the work order window."""

    # --- Top row: Parts List and Checklist ---
        top_buttons_layout = QHBoxLayout()
        self.partslist_btn = QPushButton("Parts List")
        self.checklist_btn = QPushButton("Check List")
        top_buttons_layout.addWidget(self.partslist_btn)
        top_buttons_layout.addWidget(self.checklist_btn)
        self.layout.addLayout(top_buttons_layout)

        # Connect top row buttons
        self.partslist_btn.clicked.connect(self.open_partslist_gui)
        self.checklist_btn.clicked.connect(self.open_checklist_window)

        # --- Bottom row: Save, Delete, Print, Close Window ---
        bottom_buttons_layout = QHBoxLayout()

        # Save Changes
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet("background-color: blue; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_changes)
        bottom_buttons_layout.addWidget(self.save_btn)

        # Delete Work Order
        self.delete_btn = QPushButton("Delete Work Order")
        self.delete_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_work_order)
        bottom_buttons_layout.addWidget(self.delete_btn)

        # Print Work Order
        self.print_btn = QPushButton("Print Work Order")
        self.print_btn.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.print_btn.clicked.connect(self.handle_wo_print)
        bottom_buttons_layout.addWidget(self.print_btn)

        # Close Work Order Window
        self.close_window_btn = QPushButton("Close Work Order Window")
        self.close_window_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.close_window_btn.clicked.connect(self.close_wo_window)
        bottom_buttons_layout.addWidget(self.close_window_btn)

        self.layout.addLayout(bottom_buttons_layout)

        print("Buttons built and organized")


    # ---------------------- Methods ----------------------
    def load_parts(self):
        self.table.blockSignals(True)
        parts = get_parts_for_workorder(self.wo_id)
        self.table.setRowCount(0)
        for row_index, part in enumerate(parts):
            self.table.insertRow(row_index)
            id_item = QTableWidgetItem()
            id_item.setData(Qt.UserRole, part.part_id)
            self.table.setItem(row_index, 0, id_item)

            row_values = (
                part.quantity, part.description, part.part_number, part.location,
                part.our_cost, part.retail_cost, part.supplier, part.status,
                part.po_number, part.ordered_on, part.received_on, part.pulled_on
            )

            for col_index, value in enumerate(row_values, start=1):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.table.setItem(row_index, col_index, item)
        print("Parts load complete")

    def save_changes(self):
        """Update work order fields in DB and refresh in-memory data."""
        new_values = {
            "wo_number": self.wo_number_input.text().strip(),
            "status": self.status_input.text().strip(),
            "customer_first": self.customer_first_input.text().strip(),
            "customer_last": self.customer_last_input.text().strip(),
            "machine_type": self.machine_type_input.text().strip(),
            "machine_make": self.machine_make_input.text().strip(),
            "machine_model": self.machine_model_input.text().strip(),
            "machine_model_number": self.machine_model_number_input.text().strip(),
            "machine_serial_number": self.machine_serial_number_input.text().strip(),
            "machine_year": self.machine_year_input.text().strip(),
            "engine_make": self.engine_make_input.text().strip(),
            "engine_model": self.engine_model_input.text().strip(),
            "engine_model_number": self.engine_model_number_input.text().strip(),
            "engine_serial_number": self.engine_serial_number_input.text().strip()
        }

        try:
            updated = update_work_order(self.wo_id, new_values)
            self.wo_data.update(new_values)
            from notes import save_note
            for section_name, text_edit in self.notes_sections.items():
                text = text_edit.toPlainText().strip()
                save_note(self.wo_id, section_name, text)
                self.work_order_saved.emit()
            if updated:
                QMessageBox.information(self, "Saved", "Work order and notes updated successfully.")
            else:
                QMessageBox.information(self, "Saved", "Notes saved successfully. No changes in main fields.")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Error saving work order or noes: {e}")
        print("Save changes and notes complete")
        self.work_order_saved.emit()
        
    def add_part_to_db(self):
        """Add part via manager and refresh table."""
        from wo_manager import add_part_to_db as manager_add_part

        part_data = {
            "quantity": self.part_qty_input.value(),
            "description": self.part_desc_input.text().strip(),
            "part_number": self.part_number_input.text().strip(),
            "location": self.part_location_input.text().strip(),
            "status": self.part_status_input.text().strip() or "In Stock",
            "supplier": self.part_supplier_input.text().strip()
        }

        try:
            manager_add_part(self.wo_id, part_data)
        except ValueError as e:
            QMessageBox.warning(self.partslist_window, "Error", str(e))
            return

        self.load_parts()
        self.clear_part_inputs()
        print("Part add to DB complete")

    def clear_part_inputs(self):
        self.part_qty_input.setValue(1)
        self.part_desc_input.clear()
        self.part_number_input.clear()
        self.part_location_input.clear()
        self.part_status_input.setText("In Stock")
        self.part_supplier_input.clear()
        print("Parts input clear")

    def open_checklist_window(self):
        self.checklist_window = QWidget()
        self.checklist_window.setWindowTitle("Check List")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Checklist feature not implemented yet."))
        self.checklist_window.setLayout(layout)
        self.checklist_window.resize(500, 400)
        self.checklist_window.show()
        print("Checklist window open")

    def open_partslist_gui(self):
        self.parts_window = PartsListWindow(self.wo_id)
        self.parts_window.show()
        print("Partslist window open")

    def handle_wo_print(self):
        inputs = {
            "wo_number": self.wo_number_input.text(),
            "status": self.status_input.text(),
            "machine_year": self.machine_year_input.text(),
            "machine_make": self.machine_make_input.text(),
            "machine_model": self.machine_model_input.text(),
            "machine_serial_number": self.machine_serial_number_input.text(),
            "engine_make": self.engine_make_input.text(),
            "engine_model": self.engine_model_input.text(),
            "engine_serial_number": self.engine_serial_number_input.text(),
        }
        generate_wo_pdf(self.wo_data, self.notes_sections, inputs)
        print("Work order print prepared with current input values")

    def save_all_notes(self):
        """Save each note section to the databse."""
        from notes import save_note
        for section_name, text_edit in self.notes_sections.items():
            text = text_edit.toPlainText().strip()
            save_note(self.wo_id, section_name, text)

        QMessageBox.information(self, "Notes Saved", "All notes have been saved successfully.")
        print("All notes are saved")

    def load_notes_from_db(self):
        try:
            notes_dict = load_notes(self.wo_id)
        except Exception as e:
            print(f"Error loading notes for work order {self.wo_id}: {e}")
            return
        for section, text_edit in self.notes_sections.items():
            if section in notes_dict:
                text_edit.setPlainText(notes_dict[section])
            else:
                text_edit.clear()
        print("Notes loaded")

    def delete_work_order(self):
        from wo_manager import delete_work_order
        confirm = QMessageBox.question(
            self,
            "Delete Work Order",
            "Are you sure you want to delete this work order and all related parts?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return
        try:
            delete_work_order(self.wo_id)
            QMessageBox.information(self, "Deleted", "Work order deleted successfully.")
            self.work_order_deleted.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete work order: {e}")
        self.work_order_deleted.emit()

    def close_wo_window(self):
        """Prompt user to close the work order window."""
        confirm = QMessageBox.question(
            self,
            "Close Work Order",
            "Are you sure you want to close this work order window?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.close()
            print(f"Work order window {self.wo_id} closed.")


        
