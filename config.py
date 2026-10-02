# config.py
import os
import json
import logging
from PyQt6.QtCore import QStandardPaths

from themes import THEMES

# --- STAŁE APLIKACJI ---
APP_VERSION = "1.0.3.8-dev"
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300
LOG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml.log")
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml_config.json")

try:
    logging.basicConfig(
        filename=LOG_FILE, 
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except OSError:
    logging.basicConfig(level=logging.ERROR)

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
        "maximized": False,
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
        
        # Położenie może być ujemne (monitor po lewej/nad głównym) - nie przycinamy go.
        # Widoczność okna na dostępnych ekranach sprawdza main_window.
        for key in ["x", "y", "width", "height"]:
            value = config.get(key)
            if not isinstance(value, int) or isinstance(value, bool):
                config[key] = default_config[key]
        
        if config["width"] < MIN_WINDOW_WIDTH:
            config["width"] = default_config["width"]
        if config["height"] < MIN_WINDOW_HEIGHT:
            config["height"] = default_config["height"]
        
        if not isinstance(config.get("maximized"), bool):
            config["maximized"] = False
        
        if config.get("theme") not in THEMES:
            config["theme"] = "jasny"
        
        return config
    except Exception:
        return default_config

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        logging.error(f"Błąd zapisu konfiguracji: {e}")
