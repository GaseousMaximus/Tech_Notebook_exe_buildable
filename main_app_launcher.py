# --- THIS IS THE MAIN GUI --- "main_app_launcher.py"
import traceback
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from home_page_gui import HomePage
from database import initialize_database
from startup_check import main as startup_check


try:
    startup_check()
except SystemExit:
    print("Startup check failed. Fix issues before launching.")
    sys.exit(1)

initialize_database()

print("Startup check successful")

# --- Start Qt Application ---
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv) 

    
# --- Set global app font ---    
app_font = QFont()
app_font.setPointSize(16)
app.setFont(app_font)


# --- Load Home Page Windoew ---
window = HomePage()
window.showMaximized()


# --- Confirm successful launch
print(" Tech Notebook App launched successfully")


# --- Start Even Loop ---
sys.exit(app.exec())






    
