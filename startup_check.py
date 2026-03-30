# --- startup_check.py ---
# Check that all required files exist
# Check that required packages (like PySide6) are installed
# Print clean results so you know if the app is ready to launch

# --- Standard Imports ---
import os # Load module - operating system
import sys
import datetime
import importlib.util

# --- Import Registry (for audit or dynamic use) ---
IMPORTS = [
    "os",
    "sys",
    "datetime",
    "importlib.util"
]

ROOT = os.path.abspath(os.path.dirname(__file__)) # fixed reference point
print(f" Root path: {ROOT}")

REQUIRED_FILES = [
    "main_app_launcher.py",
    "wo_gui.py",
    "wo_data_classes.py",
    "database.py",
    "parts.py"
]    # A list of relative file paths that must exist for the app to run. “These files must be present before launching.”

def check_files():
    missing = [] # local variabe to hold any missing file paths.
    for file in REQUIRED_FILES: # Loops through global list.
        full_path = os.path.join(ROOT, file)
        if not os.path.isfile(full_path): # Check for missing files.
            missing.append(file)    # Adds if missing.
    return missing    # Returns missing file paths
    
REQUIRED_PACKAGES = [
    "PySide6",
    "reportlab"
]

def check_packages():   # checks for packages like above
    missing = []
    for pkg in REQUIRED_PACKAGES:
        if importlib.util.find_spec(pkg) is None:
            missing.append(pkg)
    return missing
    
def main():   # Execution hub
    print(" Checking project integrity...\n")
    missing_files = check_files()
    missing_packages = check_packages()
    if missing_files:
        print("X Missing files:")
        for f in missing_files:
            print(f"   -{f}")
    else:
            print("All required files are present.")
    if missing_packages:
        print("\n X Missing packages:")
        for p in missing_packages:
            print(f"   - {p}")
        print("\n Run: uv install " + " ".join(missing_packages))
    else:
        print(" All required packages are installed.")
    if not missing_files and not missing_packages:
        print("\n Ready to launch.")
    else:
        print("\n Fix the issues above before launching.")
        
if __name__ == "__main__":
    main()
      