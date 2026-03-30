#1. Paths and File Locations
#2. Connection Settings
#3. User Preferences / Settings
#4. Feature Toggles / Flags
#5. Security / Credentials
#6. Environment or Mode
#7. Logging / Debugging Options
#8. Timeouts / Limits / Resource Settings
#9. Miscellaneous / Custom Options
#File formats: Config files come in various formats:
#INI (config.ini) – simple key-value pairs
#YAML (config.yaml) – human-readable hierarchical data
#JSON (config.json) – structured data, widely used in web apps
#TOML (config.toml) – modern INI alternative
#XML (config.xml) – hierarchical, older style
# --- config.py ---
from pathlib import Path
import sys

# --- Root and base directories ---
if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).parent
else: 
    ROOT_DIR = Path(__file__).resolve().parent

DB_FILE = "tech_notebook.db"
DB_PATH = ROOT_DIR / DB_FILE      #For the exact full path your SQLite connection will use. 
