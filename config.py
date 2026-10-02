# config.py
import os
import json
import logging
from PyQt6.QtCore import QStandardPaths

from themes import THEMES

# --- STAŁE APLIKACJI ---
APP_VERSION = "1.0.3.4"
LOG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml.log")
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml_config.json")

# ... (reszta dotychczasowego kodu config.py) ...

try:
    logging.basicConfig(
        filename=LOG_FILE, 
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except OSError:
    logging.basicConfig(level=logging.ERROR)

def _excepthook(exc_type, exc, tb):
    logging.error("Nieobsłużony wyjątek", exc_info=(exc_type, exc, tb))
    if QApplication.instance():
        QMessageBox.critical(
            None, 
            "mkHTML - Błąd", 
            f"Wystąpił nieoczekiwany błąd:\n{exc}\n\nSzczegóły: {LOG_FILE}"
        )

def get_desktop_path():
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)

def load_config():
    desktop_path = get_desktop_path()
    default_config = {
        "working_dir": desktop_path,
        "x": 100,
        "y": 100,
        "width": 950,
        "height": 680,
        "theme": "jasny"
    }
    
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if not isinstance(config, dict):
            return default_config
        
        saved_dir = config.get("working_dir", desktop_path)
        if not os.path.exists(saved_dir):
            config["working_dir"] = desktop_path
        
        for key in ["x", "y", "width", "height"]:
            if key not in config or not isinstance(config[key], int):
                config[key] = default_config[key]
        
        if config.get("theme") not in THEMES:
            config["theme"] = "jasny"
        
        config["x"] = max(0, config["x"])
        config["y"] = max(0, config["y"])
        
        return config
    except Exception:
        return default_config

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        logging.error(f"Błąd zapisu konfiguracji: {e}")