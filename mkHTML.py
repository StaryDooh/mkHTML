# mkHTML.py
import sys
import logging

from PyQt6.QtWidgets import QApplication, QMessageBox

from config import LOG_FILE  # import konfiguruje też logowanie (config.py)
from main_window import MkHTMLEditor


def _excepthook(exc_type, exc, tb):
    logging.error("Nieobsłużony wyjątek", exc_info=(exc_type, exc, tb))
    if QApplication.instance():
        QMessageBox.critical(
            None, 
            "mkHTML - Błąd", 
            f"Wystąpił nieoczekiwany błąd:\n{exc}\n\nSzczegóły: {LOG_FILE}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys.excepthook = _excepthook
    window = MkHTMLEditor()
    window.show()
    sys.exit(app.exec())