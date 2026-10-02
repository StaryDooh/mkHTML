# ui_menu.py
import webbrowser
from PyQt6.QtGui import QAction, QKeySequence
from themes import THEMES


def _add_action(window, parent_menu, text, slot, shortcut=None):
    action = QAction(text, window)
    if shortcut:
        action.setShortcut(shortcut)
    action.triggered.connect(slot)
    parent_menu.addAction(action)
    return action


def create_menu(window):
    """Tworzy pasek menu dla podanego okna aplikacji."""
    menu_bar = window.menuBar()
    
    # Menu Plik
    file_menu = menu_bar.addMenu("Plik")
    _add_action(window, file_menu, "Nowy", window.new_file, QKeySequence.StandardKey.New)
    _add_action(window, file_menu, "Otwórz...", window.open_file, QKeySequence.StandardKey.Open)
    _add_action(window, file_menu, "Zapisz", window.save_file, QKeySequence.StandardKey.Save)
    _add_action(window, file_menu, "Zapisz jako...", window.save_file_as)
    file_menu.addSeparator()
    _add_action(window, file_menu, "Zakończ", window.close, QKeySequence.StandardKey.Quit)
    
    # Menu Edycja
    edit_menu = menu_bar.addMenu("Edycja")
    _add_action(window, edit_menu, "Cofnij", lambda: window.current_editor() and window.current_editor().undo(), QKeySequence.StandardKey.Undo)
    _add_action(window, edit_menu, "Ponów", lambda: window.current_editor() and window.current_editor().redo(), QKeySequence.StandardKey.Redo)
    edit_menu.addSeparator()
    _add_action(window, edit_menu, "Wytnij", lambda: window.current_editor() and window.current_editor().cut(), QKeySequence.StandardKey.Cut)
    _add_action(window, edit_menu, "Kopiuj", lambda: window.current_editor() and window.current_editor().copy(), QKeySequence.StandardKey.Copy)
    _add_action(window, edit_menu, "Wklej", lambda: window.current_editor() and window.current_editor().paste(), QKeySequence.StandardKey.Paste)

    # Menu Motyw
    theme_menu = menu_bar.addMenu("Motyw")
    window.theme_actions = {}
    for theme_key, theme_info in THEMES.items():
        action = QAction(theme_info["name"], window)
        action.setCheckable(True)
        action.setChecked(theme_key == window.current_theme)
        action.triggered.connect(lambda checked, tk=theme_key: window.set_theme(tk))
        theme_menu.addAction(action)
        window.theme_actions[theme_key] = action

    # Przycisk Podgląd
    _add_action(window, menu_bar, "Podgląd", window.run_in_browser, QKeySequence("F5"))

    # Menu Odwiedź...
    visit_menu = menu_bar.addMenu("Odwiedź...")
    _add_action(window, visit_menu, "Pobierz najnowszą wersję", lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/releases"))
    _add_action(window, visit_menu, "Zgłoś błąd", lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/issues"))
    _add_action(window, visit_menu, "Zrelaksuj się", lambda: webbrowser.open("https://www.youtube.com/@StaryDooh"))