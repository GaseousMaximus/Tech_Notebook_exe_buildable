# create_wo_gui.py
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QComboBox, QTextEdit, QWidget, QScrollArea
)
from wo_manager import create_work_order, save_work_order
from wo_data_classes import WorkOrder, Machine, Engine
from notes import save_note

class CreateWorkOrderWindow(QDialog):   # <- changed from QWidget to QDialog
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Work Order")
        self.resize(1200, 900)

        self.layout = QVBoxLayout(self)

        # --- Scrollable area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # --- WO Number ---
        self.content_layout.addWidget(QLabel("WO Number:"))
        self.wo_number = QLineEdit()
        self.content_layout.addWidget(self.wo_number)

        # --- Customer Fields ---
        self.content_layout.addWidget(QLabel("Customer First Name:"))
        self.customer_first = QLineEdit()
        self.content_layout.addWidget(self.customer_first)

        self.content_layout.addWidget(QLabel("Customer Last Name:"))
        self.customer_last = QLineEdit()
        self.content_layout.addWidget(self.customer_last)

        self.content_layout.addWidget(QLabel("Tag Number:"))
        self.tag_number = QLineEdit()
        self.content_layout.addWidget(self.tag_number)

        # --- Machine Fields ---
        self.content_layout.addWidget(QLabel("Machine Type:"))
        self.machine_type = QComboBox()
        self.machine_type.addItems(["Zero Turn", "Tractor", "Riding Mower", "Steering Wheel Z-Turn", "Walk Behind", "Push Mower", "Weed Eater", "Chain Saw", "Pressure Washer"])
        self.content_layout.addWidget(self.machine_type)

        self.content_layout.addWidget(QLabel("Machine Make:"))
        self.machine_make = QLineEdit()
        self.content_layout.addWidget(self.machine_make)

        self.content_layout.addWidget(QLabel("Machine Model:"))
        self.machine_model = QLineEdit()
        self.content_layout.addWidget(self.machine_model)

        self.content_layout.addWidget(QLabel("Machine Model Number:"))
        self.machine_model_number = QLineEdit()
        self.content_layout.addWidget(self.machine_model_number)

        self.content_layout.addWidget(QLabel("Machine Serial Number:"))
        self.machine_serial_number = QLineEdit()
        self.content_layout.addWidget(self.machine_serial_number)

        self.content_layout.addWidget(QLabel("Machine Year:"))
        self.machine_year = QSpinBox()
        self.machine_year.setRange(1980, 2030)
        self.content_layout.addWidget(self.machine_year)

        # --- Engine Fields ---
        self.content_layout.addWidget(QLabel("Engine Make:"))
        self.engine_make = QLineEdit()
        self.content_layout.addWidget(self.engine_make)

        self.content_layout.addWidget(QLabel("Engine Model:"))
        self.engine_model = QLineEdit()
        self.content_layout.addWidget(self.engine_model)

        self.content_layout.addWidget(QLabel("Engine Model Number:"))
        self.engine_model_number = QLineEdit()
        self.content_layout.addWidget(self.engine_model_number)

        self.content_layout.addWidget(QLabel("Engine Serial Number:"))
        self.engine_serial_number = QLineEdit()
        self.content_layout.addWidget(self.engine_serial_number)

        # --- Notes Fields ---
        self.notes_sections = {}
        for section_name, label_text in [
            ('service_requested', "Service Requested"),
            ('diagnosis', "Diagnosis"),
            ('work_notes', "Work Notes / Labor Tracking"),
            ('test_run', "Test Run / Wrap-Up Notes")
        ]:
            self.content_layout.addWidget(QLabel(label_text))
            text_edit = QTextEdit()
            text_edit.setMinimumHeight(100)
            self.content_layout.addWidget(text_edit)
            self.notes_sections[section_name] = text_edit

        # --- Buttons ---
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Create Work Order")
        self.save_btn.clicked.connect(self.create_wo_save)
        buttons_layout.addWidget(self.save_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(buttons_layout)
    print("create_wo_gui created")


    def create_wo_save(self):
        """Collect all field data and save work order and notes."""
        try:
        # --- Build dictionary of all work order fields ---
            fields = {
                "wo_number": self.wo_number.text().strip(),
                "customer_first": self.customer_first.text().strip(),
                "customer_last": self.customer_last.text().strip(),
                "customer_tag": self.tag_number.text().strip(),
                "machine_type": self.machine_type.currentText(),
                "machine_make": self.machine_make.text().strip(),
                "machine_model": self.machine_model.text().strip(),
                "machine_model_number": self.machine_model_number.text().strip(),
                "machine_serial_number": self.machine_serial_number.text().strip(),
                "machine_year": str(self.machine_year.value()),
                "engine_make": self.engine_make.text().strip(),
                "engine_model": self.engine_model.text().strip(),
                "engine_model_number": self.engine_model_number.text().strip(),
                "engine_serial_number": self.engine_serial_number.text().strip(),
                "status": "New"
            }

        # --- Create Work Order in the database ---
            from wo_manager import create_work_order
            wo_id = create_work_order(fields)
            if wo_id is None:
                raise ValueError("Failed to create work order. Check database connection or fields.")

        # --- Save all notes ---
            from notes import save_note
            for section, widget in self.notes_sections.items():
                text = widget.toPlainText().strip()
                save_note(wo_id, section, text)  # this works now because notes table exists

        # --- Close dialog ---
            self.accept()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save work order: {e}")


