# themes.py
"""
Motywy aplikacji mkHTML.

Każdy motyw opisuje WSZYSTKIE kolory w jednym miejscu:
  - klucze "bg", "fg", "caret", ... i słowniki "html" / "css" - edytor i kolorowanie składni,
  - słownik "ui" - wygląd okna (menu, zakładki, przycisk zamykania zakładki).

Arkusz stylów całego okna ("app_qss") jest generowany automatycznie ze słownika "ui"
przez build_app_qss(), więc kolory wpisujemy tylko raz, a oba motywy mają identyczny zestaw reguł.
"""

# Klucze, które musi mieć słownik "ui" każdego motywu
UI_KEYS = (
    "window_bg", "window_fg",
    "menubar_bg", "menubar_fg",
    "menu_bg", "menu_fg", "menu_border",
    "menu_sel_bg", "menu_sel_fg", "menu_disabled_fg",
    "menu_separator", "menu_indicator",
    "tab_bg", "tab_fg", "tab_sel_bg", "tab_sel_fg", "tab_border",
    "close_fg", "close_active_fg", "close_hover_bg", "close_hover_fg",
)


def build_app_qss(ui):
    """Buduje arkusz stylów QSS okna głównego na podstawie słownika kolorów 'ui' motywu."""
    missing = [k for k in UI_KEYS if k not in ui]
    if missing:
        raise KeyError(f"Motyw: brak kolorów interfejsu: {', '.join(missing)}")

    rules = [
        ("QMainWindow", {
            "background-color": ui["window_bg"], "color": ui["window_fg"]}),

        # Pasek menu
        ("QMenuBar", {
            "background-color": ui["menubar_bg"], "color": ui["menubar_fg"]}),
        ("QMenuBar::item", {
            "background": "transparent", "padding": "4px 10px"}),
        ("QMenuBar::item:selected", {
            "background-color": ui["menu_sel_bg"], "color": ui["menu_sel_fg"]}),
        ("QMenuBar::item:pressed", {
            "background-color": ui["menu_sel_bg"], "color": ui["menu_sel_fg"]}),

        # Menu rozwijane i menu kontekstowe
        ("QMenu", {
            "background-color": ui["menu_bg"], "color": ui["menu_fg"],
            "border": f"1px solid {ui['menu_border']}"}),
        ("QMenu::item", {
            "background": "transparent", "padding": "4px 24px 4px 28px"}),
        ("QMenu::item:selected", {
            "background-color": ui["menu_sel_bg"], "color": ui["menu_sel_fg"]}),
        ("QMenu::item:disabled", {
            "color": ui["menu_disabled_fg"]}),
        ("QMenu::separator", {
            "height": "1px", "background": ui["menu_separator"], "margin": "4px 8px"}),
        ("QMenu::indicator", {
            "width": "8px", "height": "8px", "margin-left": "8px"}),
        ("QMenu::indicator:checked", {
            "background-color": ui["menu_indicator"], "border-radius": "2px"}),

        # Zakładki
        ("QTabWidget::pane", {
            "border": f"1px solid {ui['tab_border']}"}),
        ("QTabBar::tab", {
            "background": ui["tab_bg"], "color": ui["tab_fg"], "padding": "5px"}),
        ("QTabBar::tab:selected", {
            "background": ui["tab_sel_bg"], "color": ui["tab_sel_fg"], "font-weight": "bold"}),

        # Przycisk zamykania zakładki (QToolButton#tabClose tworzony w main_window.py)
        ("QToolButton#tabClose", {
            "background": "transparent", "border": "none", "color": ui["close_fg"],
            "font-size": "15px", "font-weight": "bold", "padding": "0px 4px"}),
        ('QToolButton#tabClose[active="true"]', {
            "color": ui["close_active_fg"]}),
        ("QToolButton#tabClose:hover", {
            "background-color": ui["close_hover_bg"], "color": ui["close_hover_fg"],
            "border-radius": "3px"}),
    ]
    return " ".join(
        selector + " { " + "; ".join(f"{prop}: {value}" for prop, value in props.items()) + "; }"
        for selector, props in rules
    )


THEMES = {
    "jasny": {
        "name": "Jasny",
        "bg": "#ffffff",
        "fg": "#000000",
        "caret": "#000000",
        "caret_line": "#e8e8e8",
        "selection_bg": "#a6d2ff",
        "selection_fg": "#000000",
        "margin_bg": "#f0f0f0",
        "margin_fg": "#888888",
        "ui": {
            "window_bg": "#f0f0f0",
            "window_fg": "#000000",
            "menubar_bg": "#f0f0f0",
            "menubar_fg": "#000000",
            "menu_bg": "#ffffff",
            "menu_fg": "#000000",
            "menu_border": "#c8c8c8",
            "menu_sel_bg": "#a6d2ff",
            "menu_sel_fg": "#000000",
            "menu_disabled_fg": "#a0a0a0",
            "menu_separator": "#d0d0d0",
            "menu_indicator": "#000000",
            "tab_bg": "#e0e0e0",
            "tab_fg": "#000000",
            "tab_sel_bg": "#ffffff",
            "tab_sel_fg": "#000000",
            "tab_border": "#c8c8c8",
            "close_fg": "#8a8a8a",
            "close_active_fg": "#000000",
            "close_hover_bg": "#d0d0d0",
            "close_hover_fg": "#000000"
        },
        "html": {
            "tag": "#0000ff",
            "attr": "#ff0000",
            "string": "#a31515",
            "entity": "#ff0000",
            "comment": "#008000"
        },
        "css": {
            "tag": "#0000ff",
            "class": "#ff0000",
            "id": "#ff0000",
            "prop": "#ff0000",
            "val": "#0000ff",
            "string": "#a31515",
            "pseudo": "#ff8000",
            "comment": "#008000"
        }
    },
    "ciemny": {
        "name": "Ciemny",
        "bg": "#2b2b2b",
        "fg": "#a9b7c6",
        "caret": "#ffffff",
        "caret_line": "#323232",
        "selection_bg": "#214283",
        "selection_fg": "#a9b7c6",
        "margin_bg": "#313335",
        "margin_fg": "#606366",
        "ui": {
            "window_bg": "#2b2b2b",
            "window_fg": "#a9b7c6",
            "menubar_bg": "#3c3f41",
            "menubar_fg": "#a9b7c6",
            "menu_bg": "#3c3f41",
            "menu_fg": "#a9b7c6",
            "menu_border": "#555555",
            "menu_sel_bg": "#4b6eaf",
            "menu_sel_fg": "#ffffff",
            "menu_disabled_fg": "#6b6b6b",
            "menu_separator": "#555555",
            "menu_indicator": "#a9b7c6",
            "tab_bg": "#3c3f41",
            "tab_fg": "#a9b7c6",
            "tab_sel_bg": "#2b2b2b",
            "tab_sel_fg": "#a9b7c6",
            "tab_border": "#3c3f41",
            "close_fg": "#8a919c",
            "close_active_fg": "#ffffff",
            "close_hover_bg": "#5a5d5f",
            "close_hover_fg": "#ffffff"
        },
        "html": {
            "tag": "#e8bf6a",
            "attr": "#bababa",
            "string": "#a5c261",
            "entity": "#6d9cbe",
            "comment": "#808080"
        },
        "css": {
            "tag": "#e8bf6a",
            "class": "#e8bf6a",
            "id": "#e8bf6a",
            "prop": "#9876aa",
            "val": "#a9b7c6",
            "string": "#a5c261",
            "pseudo": "#cc7832",
            "comment": "#808080"
        }
    },
    "polarny": {
        "name": "Polarny",
        "bg": "#2e3440",
        "fg": "#d8dee9",
        "caret": "#88c0d0",
        "caret_line": "#3b4252",
        "selection_bg": "#434c5e",
        "selection_fg": "#eceff4",
        "margin_bg": "#292e39",
        "margin_fg": "#4c566a",
        "ui": {
            "window_bg": "#2e3440",
            "window_fg": "#d8dee9",
            "menubar_bg": "#3b4252",
            "menubar_fg": "#d8dee9",
            "menu_bg": "#3b4252",
            "menu_fg": "#d8dee9",
            "menu_border": "#4c566a",
            "menu_sel_bg": "#5e81ac",
            "menu_sel_fg": "#eceff4",
            "menu_disabled_fg": "#6b7488",
            "menu_separator": "#4c566a",
            "menu_indicator": "#88c0d0",
            "tab_bg": "#3b4252",
            "tab_fg": "#d8dee9",
            "tab_sel_bg": "#2e3440",
            "tab_sel_fg": "#eceff4",
            "tab_border": "#3b4252",
            "close_fg": "#7b88a1",
            "close_active_fg": "#eceff4",
            "close_hover_bg": "#4c566a",
            "close_hover_fg": "#eceff4"
        },
        "html": {
            "tag": "#81a1c1",
            "attr": "#8fbcbb",
            "string": "#a3be8c",
            "entity": "#d08770",
            "comment": "#616e88"
        },
        "css": {
            "tag": "#81a1c1",
            "class": "#ebcb8b",
            "id": "#d08770",
            "prop": "#88c0d0",
            "val": "#b48ead",
            "string": "#a3be8c",
            "pseudo": "#bf616a",
            "comment": "#616e88"
        }
    }
}

# Arkusz stylów okna powstaje ze słownika "ui" - main_window.py odczytuje go jako theme["app_qss"].
for _theme in THEMES.values():
    _theme["app_qss"] = build_app_qss(_theme["ui"])