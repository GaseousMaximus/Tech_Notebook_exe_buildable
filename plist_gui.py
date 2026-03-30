import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QComboBox, QMessageBox, QStyledItemDelegate
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from utils import safe_db_call
from parts import (
    get_parts_for_workorder,
    update_part,
    add_part,
    delete_part
)

class StatusDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems([
            "In Stock",
            "Out of Stock",
            "On Order",
            "Pulled",
            "Installed",
            "Other"
        ])
        combo.setEditable(True)
        return combo

    def setEditorData(self, editor, index):
        value = index.data()
        idx = editor.findText(value)
        if idx >= 0:
            editor.setCurrentIndex(idx)
        else:
            editor.setEditText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


class PartsListWindow(QWidget):
    def __init__(self, wo_id):
        super().__init__()
        self.wo_id = wo_id
        self.setWindowTitle(f"Parts List for Work Order #{wo_id}")
        self.resize(1600, 1000)

        self.layout = QVBoxLayout(self)

        # Header
        self.header_label = QLabel(f"Parts List for Work Order #{self.wo_id}")
        self.header_label.setFont(QFont("Arial", 18))
        self.layout.addWidget(self.header_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "part_id", "Quantity", "Description", "Part #", "Location",
            "Our Cost", "Retail Cost", "Supplier", "Status", "P.O #",
            "Ordered on", "Received on", "Pulled on"
        ])
        self.table.setItemDelegateForColumn(8, StatusDelegate())
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.table.setColumnHidden(0, True)  # hide part_id
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.table.cellChanged.connect(self.cell_edited)

        # Info label
        self.info_label = QLabel("")
        self.layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Part")
        self.delete_button = QPushButton("Delete Selected")
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_part_row)
        self.delete_button.clicked.connect(self.delete_selected_part)
        self.close_button.clicked.connect(self.close)

        # Load data
        self.load_parts()

    def load_parts(self):
        """Load all parts from the database into the table."""
        try:
            parts = safe_db_call(get_parts_for_workorder, self.wo_id)
            self.table.blockSignals(True)
            self.table.setRowCount(0)
            for row_index, part in enumerate(parts):
                self.table.insertRow(row_index)
                # Set part_id with UserRole
                part_id_item = QTableWidgetItem()
                part_id_item.setData(Qt.UserRole, part.part_id)
                self.table.setItem(row_index, 0, part_id_item)

                row_values = (
                    part.quantity, part.description, part.part_number, part.location,
                    part.our_cost, part.retail_cost, part.supplier, part.status,
                    part.po_number, part.ordered_on, part.received_on, part.pulled_on
                )
                for col_index, value in enumerate(row_values, start=1):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.table.setItem(row_index, col_index, item)
            self.table.blockSignals(False)
        except Exception as e:
            QMessageBox.warning(self, "Load Failed", f"Could not load parts: {e}")

    def cell_edited(self, row, column):
        if column == 0:
            return  # part_id column is hidden

        field_map = {
            1: "quantity", 2: "description", 3: "part_number", 4: "location",
            5: "our_cost", 6: "retail_cost", 7: "supplier", 8: "status",
            9: "po_number", 10: "ordered_on", 11: "received_on", 12: "pulled_on"
        }
        field = field_map.get(column)
        if not field:
            return

        part_id_item = self.table.item(row, 0)
        part_id = part_id_item.data(Qt.UserRole)
        new_value = self.table.item(row, column).text()

        try:
            # Only convert numeric fields
            if field in ("quantity",):
                new_value = int(new_value)
            elif field in ("our_cost", "retail_cost"):
                new_value = float(new_value) if new_value else 0.0

            success = safe_db_call(update_part, part_id, **{field: new_value})
            if success is not None:
                self.info_label.setText(f"Updated {field} for part ID {part_id}")
        except Exception as e:
            QMessageBox.warning(self, "Update Failed", f"Could not update {field}: {e}")

    def add_part_row(self):
        try:
            part = safe_db_call(add_part, self.wo_id)
            if part:
                self.load_parts()
                self.info_label.setText(f"Added part ID {part.part_id}")
        except Exception as e:
            QMessageBox.warning(self, "Add Failed", f"Could not add part: {e}")

    def delete_selected_part(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a part to delete")
            return

        part_id_item = self.table.item(row, 0)
        part_id = part_id_item.data(Qt.UserRole)

        try:
            success = safe_db_call(delete_part, part_id)
            if success is not None:
                self.load_parts()
                self.info_label.setText(f"Deleted part ID {part_id}")
        except Exception as e:
            QMessageBox.warning(self, "Delete Failed", f"Could not delete part: {e}")
