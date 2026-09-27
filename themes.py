# themes.py

THEMES = {
    "jasny": {
        "name": "Jasny",
        "app_qss": "QMainWindow { background-color: #f0f0f0; }",
        "bg": "#ffffff",
        "fg": "#000000",
        "caret": "#000000",
        "caret_line": "#e8e8e8",
        "selection_bg": "#a6d2ff",
        "selection_fg": "#000000",
        "margin_bg": "#f0f0f0",
        "margin_fg": "#888888",
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
        "app_qss": "QMainWindow { background-color: #2b2b2b; color: #a9b7c6; } QTabBar::tab { background: #3c3f41; color: #a9b7c6; padding: 5px; } QTabBar::tab:selected { background: #2b2b2b; font-weight: bold; }",
        "bg": "#2b2b2b",
        "fg": "#a9b7c6",
        "caret": "#ffffff",
        "caret_line": "#323232",
        "selection_bg": "#214283",
        "selection_fg": "#a9b7c6",
        "margin_bg": "#313335",
        "margin_fg": "#606366",
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
    }
}