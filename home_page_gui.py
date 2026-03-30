# --- home_page_gui.py ---
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QPushButton, QLineEdit    
)
from PySide6.QtCore import Qt
from wo_gui import WorkOrderDetailWindow
from create_wo_gui import CreateWorkOrderWindow
from utils import refresh_table
from steam_gauge import SteamGauge

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tech Notebook Home")

        # --- Create main layout ---
        main_layout = QVBoxLayout()
        print(f"Main layout created.")

        # --- Top: Gauges Placeholder --- 
        top_layout = QHBoxLayout()

        self.avg_wo_age_gauge = SteamGauge(min_value=0, max_value=30)
        self.avg_wo_age_gauge.setFixedSize(200,200)
        self.avg_wo_age_gauge.set_fetch_function(self.get_average_work_order_age)
        top_layout.addWidget(self.avg_wo_age_gauge)
        label = QLabel("Ave WO Age")
        label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(label)

        main_layout.addLayout(top_layout)
        print(f"Top gauges created.")  

        # --- Middle: Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "WO Number", "Customer Last Name", "Status", "Start Date"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(5):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)
        print(f"Middle work order table created")

        # --- Bottom buttons ---
        bottom_layout = QHBoxLayout()

        self.btn_create = QPushButton("Create Work Order")
        self.btn_create.setFixedSize(200, 60)
        self.btn_create.clicked.connect(self.handle_create)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search work orders...")
        self.search_input.setFixedSize(400, 60)

        self.btn_close = QPushButton("Close App")                 # <-- new button
        self.btn_close.setFixedSize(150, 60)
        self.btn_close.clicked.connect(self.close)               # <-- closes main window
        
        bottom_layout.addWidget(self.btn_create, alignment=Qt.AlignLeft)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.search_input, alignment=Qt.AlignRight)
        bottom_layout.addWidget(self.btn_close, alignment=Qt.AlignRight)
        main_layout.addLayout(bottom_layout)
        print(f"Bottom buttons created")
        
        # --- Signals ---
        self.table.cellDoubleClicked.connect(self.on_work_order_double_click)
        print(f"Signal connected")

        # --- Track open detail windows ---
        self.open_detail_windows = []
        print(f"Open detail window successful")
        
        # --- Load initial data ---
        refresh_table(self.table)
        print(f"Table refreshed")

        # --- Apply lauout at the very end ---
        self.setLayout(main_layout)


    # --- Event: Double click to open detail window ---
    def on_work_order_double_click(self, row, column):
        print("double-click detected.")

        wo_id_item = self.table.item(row, 0)
        if not wo_id_item:
            print("No wo_id_item found - returning.")
            return
        
        try:
            wo_id = int(wo_id_item.text())
        except ValueError:
            return # invalid ID in the table
        detail_window = WorkOrderDetailWindow(wo_id)
        self.open_detail_windows.append(detail_window)
        detail_window.work_order_deleted.connect(
            lambda: refresh_table(self.table)
        )

        detail_window.show()
        print(f"Work order double clicked")


    def handle_create(self):
        dialog = CreateWorkOrderWindow()
        if dialog.exec():
            refresh_table(self.table)
        print(f"create work order dialog")

    def get_average_work_order_age(self):
        from wo_manager import fetch_all_work_orders
        import datetime

        rows = fetch_all_work_orders()
        if not rows:
            return 0
        
        total_days = 0
        count = 0
        today = datetime.date.today()

        for row in rows:
            start_date_str = row.get("created_on")
            if not start_date_str:
                continue
            try:
                start_date = datetime.datetime.fromisoformat(start_date_str).date()          
            except ValueError:
                continue

            delta = today - start_date
            total_days += delta.days
            count += 1

        return total_days / count if count > 0 else 0   

    
    