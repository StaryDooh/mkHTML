import sys
import re
import os
import json
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtGui import QFont, QAction, QKeySequence, QColor
from PyQt6.QtCore import Qt
from PyQt6.Qsci import QsciScintilla, QsciLexerHTML, QsciLexerCSS

# --- KONFIGURACJA ŚCIEŻEK I USTAWIEŃ ---
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml_config.json")

def get_desktop_path():
    """Pobiera ścieżkę do Pulpitu, uwzględniając polskie wersje systemu Windows."""
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    if not os.path.exists(desktop):
        desktop_pl = os.path.join(home, "Pulpit")
        if os.path.exists(desktop_pl):
            return desktop_pl
    return desktop

def load_config():
    """Wczytuje konfigurację (katalog roboczy, położenie i rozmiar okna)."""
    desktop_path = get_desktop_path()
    default_config = {
        "working_dir": desktop_path,
        "x": 100,
        "y": 100,
        "width": 950,
        "height": 680
    }
    
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not isinstance(config, dict):
                return default_config
            
            # Weryfikacja ścieżki
            saved_dir = config.get("working_dir", desktop_path)
            if not os.path.exists(saved_dir):
                config["working_dir"] = desktop_path
            
            # Weryfikacja parametrów geometrii
            for key in ["x", "y", "width", "height"]:
                if key not in config or not isinstance(config[key], int):
                    config[key] = default_config[key]
            
            return config
    except Exception:
        return default_config

def save_config(config_data):
    """Zapisuje aktualną konfigurację do pliku w profilu użytkownika."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Błąd zapisu konfiguracji: {e}")


class MyCodeEditor(QsciScintilla):
    """Autorska klasa edytora z obsługą autouzupełniania tagów, klamer i wcięć."""
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.void_tags = {'br', 'hr', 'img', 'input', 'meta', 'link', 'base', 'area', 'col', 'embed', 'param', 'source', 'track', 'wbr'}

    def keyPressEvent(self, event):
        # 0. ZAMIANA 2 SPACJI NA 4 SPACJE NA POCZĄTKU LINII
        if event.key() == Qt.Key.Key_Space:
            line, col = self.getCursorPosition()
            line_text = self.text(line)[:col]
            
            if re.fullmatch(r' +', line_text) and len(line_text) % 4 == 1:
                self.setSelection(line, col - 1, line, col)
                self.removeSelectedText()
                self.insert("    ")
                self.setCursorPosition(line, col + 3)
                return

        # 1. INTELIGENTNY ENTER MIĘDZY TAGAMI
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            
            if 0 < col < len(line_text) and line_text[col-1] == '>' and line_text[col:col+2] == '</':
                indent_match = re.match(r'^(\s*)', line_text)
                indent_str = indent_match.group(1) if indent_match else ""
                
                self.insert(f"\n{indent_str}    \n{indent_str}")
                self.setCursorPosition(line + 1, len(indent_str) + 4)
                return
            
            super().keyPressEvent(event)
            return

        # 2. OBSŁUGA SKRÓTÓW (TAB) I DYNAMICZNEGO ROZWIJANIA TAGÓW
        if event.key() == Qt.Key.Key_Tab:
            line, col = self.getCursorPosition()
            line_text = self.text(line)[:col]
            
            snippets = {
                "html": (
                    "<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n"
                    "    <meta charset=\"UTF-8\">\n"
                    "    <title>Tytuł strony</title>\n"
                    "    <link rel=\"stylesheet\" href=\"style.css\">\n"
                    "</head>\n<body>\n    \n</body>\n</html>", 8, 4
                ),
                "a": ("<a href=\"\"></a>", 0, 9),
                "img": ("<img src=\"\" alt=\"\">", 0, 10)
            }
            
            match = re.search(r'\b([a-zA-Z0-9]+)$', line_text)
            
            if match:
                word = match.group(1).lower()
                word_len = len(word)
                is_html_mode = isinstance(self.lexer(), QsciLexerHTML) or self.lexer() is None
                
                if is_html_mode:
                    if word in snippets:
                        snippet_text, line_offset, col_offset = snippets[word]
                        self.setSelection(line, col - word_len, line, col)
                        self.removeSelectedText()
                        self.insert(snippet_text)
                        
                        if line_offset == 0:
                            self.setCursorPosition(line, col - word_len + col_offset)
                        else:
                            self.setCursorPosition(line + line_offset, col_offset)
                        return 
                    else:
                        self.setSelection(line, col - word_len, line, col)
                        self.removeSelectedText()
                        
                        if word in self.void_tags:
                            tag_text = f"<{word}>"
                            self.insert(tag_text)
                            self.setCursorPosition(line, col - word_len + len(tag_text))
                        else:
                            tag_text = f"<{word}></{word}>"
                            self.insert(tag_text)
                            self.setCursorPosition(line, col - word_len + len(word) + 2)
                        return

        # 3. OBSŁUGA ZAMYKANIA KLAMER DLA CSS ({)
        if event.text() == '{':
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            
            indent_match = re.match(r'^\s*', line_text)
            indent_str = indent_match.group(0) if indent_match else ""
            
            super().keyPressEvent(event)
            self.insert(f"\n{indent_str}    \n{indent_str}}}")
            self.setCursorPosition(line + 1, len(indent_str) + 4)
            return

        # 4. OBSŁUGA CUDZYSŁOWÓW I APOSTROFÓW (" oraz ')
        if event.text() in ['"', "'"]:
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            
            if col < len(line_text) and line_text[col] == event.text():
                self.setCursorPosition(line, col + 1)
                return
            
            super().keyPressEvent(event)
            self.insert(event.text())
            self.setCursorPosition(line, col + 1)
            return

        super().keyPressEvent(event)

        # 5. OBSŁUGA AUTOMATYCZNEGO ZAMYKANIA ZNACZNIKÓW HTML (>)
        if event.text() == '>':
            line, col = self.getCursorPosition()
            line_text = self.text(line)[:col]
            match = re.search(r'<([a-zA-Z0-9]+)[^>]*>$', line_text)
            
            if match:
                tag_name = match.group(1).lower()
                if tag_name not in self.void_tags:
                    closing_tag = f"</{tag_name}>"
                    self.insert(closing_tag)
                    self.setCursorPosition(line, col)


class MkHTMLEditor(QMainWindow):
    """Główne okno aplikacji mkHTML v0.0.2.1 z obsługą zakładek i zapamiętywaniem stanu okna."""
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.working_dir = self.config.get("working_dir", get_desktop_path())
        self.font = QFont("Consolas", 12)
        
        self.setWindowTitle("mkHTML v0.0.2.1")
        
        # Przywracanie ostatniego rozmiaru i położenia okna
        x = self.config.get("x", 100)
        y = self.config.get("y", 100)
        w = self.config.get("width", 950)
        h = self.config.get("height", 680)
        self.setGeometry(x, y, w, h)
        
        # Kontroler zakładek
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_window_title)
        
        self.setCentralWidget(self.tabs)
        self.create_menu()
        
        # Otwórz pierwszą pustą zakładkę na start
        self.add_new_tab()

    def save_app_config(self):
        """Zapisuje bieżący katalog roboczy oraz geometrię okna."""
        geom = self.geometry()
        config_data = {
            "working_dir": self.working_dir,
            "x": geom.x(),
            "y": geom.y(),
            "width": geom.width(),
            "height": geom.height()
        }
        save_config(config_data)

    def current_editor(self) -> MyCodeEditor:
        """Zwraca aktywny edytor w bieżącej zakładce."""
        return self.tabs.currentWidget()

    def add_new_tab(self, file_path=None, content=""):
        """Dodaje nową zakładkę z edytorem."""
        editor = MyCodeEditor()
        editor.setUtf8(True)
        editor.setFont(self.font)
        editor.setMarginsFont(self.font)
        editor.setMarginWidth(0, "0000")
        editor.setMarginLineNumbers(0, True)
        
        editor.current_file = file_path
        if content:
            editor.setText(content)
            
        self.update_lexer_for_editor(editor)
        editor.setModified(False)
        
        # Śledzenie zmian tekstu do gwiazdki (*) w zakładce
        editor.modificationChanged.connect(
            lambda modified, ed=editor: self.on_modification_changed(ed, modified)
        )
        
        title = os.path.basename(file_path) if file_path else "Nowy plik"
        index = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(index)
        self.update_window_title()
        return editor

    def on_modification_changed(self, editor, modified):
        """Dodaje lub usuwa gwiazdkę (*) z tytułu zakładki przy zmianach."""
        idx = self.tabs.indexOf(editor)
        if idx != -1:
            base_name = os.path.basename(editor.current_file) if editor.current_file else "Nowy plik"
            title = f"{base_name} *" if modified else base_name
            self.tabs.setTabText(idx, title)
            self.update_window_title()

    def update_window_title(self):
        """Aktualizuje tytuł głównego okna aplikacji."""
        editor = self.current_editor()
        if editor:
            file_str = editor.current_file if editor.current_file else "Nowy plik"
            mod_str = " *" if editor.isModified() else ""
            self.setWindowTitle(f"mkHTML v0.0.2.1 - {file_str}{mod_str}")
        else:
            self.setWindowTitle("mkHTML v0.0.2.1")

    def update_lexer_for_editor(self, editor):
        """Ustawia odpowiedni lexer (HTML/CSS) dla podanego edytora."""
        def set_color(lex, hex_color, cls_ref, *attrs):
            for attr in attrs:
                if hasattr(cls_ref, attr):
                    lex.setColor(QColor(hex_color), getattr(cls_ref, attr))

        if editor.current_file and editor.current_file.lower().endswith('.css'):
            lexer = QsciLexerCSS(editor)
            lexer.setDefaultFont(self.font)
            lexer.setDefaultColor(QColor("#24292e"))
            
            set_color(lexer, "#d73a49", QsciLexerCSS, 'Tag')
            set_color(lexer, "#6f42c1", QsciLexerCSS, 'ClassSelector')
            set_color(lexer, "#005cc5", QsciLexerCSS, 'IDSelector')
            set_color(lexer, "#008080", QsciLexerCSS, 'CSS1Property', 'CSS2Property', 'CSS3Property', 'UnknownProperty')
            set_color(lexer, "#e36209", QsciLexerCSS, 'Value')
            set_color(lexer, "#22863a", QsciLexerCSS, 'DoubleQuotedString', 'SingleQuotedString', 'String')
            set_color(lexer, "#9e1c23", QsciLexerCSS, 'PseudoClass')
            
            if hasattr(QsciLexerCSS, 'Comment'):
                comment_font = QFont(self.font)
                comment_font.setItalic(True)
                lexer.setColor(QColor("#6a737d"), QsciLexerCSS.Comment)
                lexer.setFont(comment_font, QsciLexerCSS.Comment)

        else:
            lexer = QsciLexerHTML(editor)
            lexer.setDefaultFont(self.font)
            lexer.setDefaultColor(QColor("#24292e"))
            
            set_color(lexer, "#005cc5", QsciLexerHTML, 'Tag', 'UnknownTag')
            set_color(lexer, "#6f42c1", QsciLexerHTML, 'Attribute', 'UnknownAttribute')
            set_color(lexer, "#22863a", QsciLexerHTML, 'HTMLDoubleQuotedString', 'HTMLSingleQuotedString')
            set_color(lexer, "#e36209", QsciLexerHTML, 'Entity')
            
            if hasattr(QsciLexerHTML, 'HTMLComment'):
                comment_font = QFont(self.font)
                comment_font.setItalic(True)
                lexer.setColor(QColor("#6a737d"), QsciLexerHTML.HTMLComment)
                lexer.setFont(comment_font, QsciLexerHTML.HTMLComment)

        editor.setLexer(lexer)
        editor.setIndentationsUseTabs(False)
        editor.setTabWidth(4)
        editor.setIndentationWidth(4)
        editor.setTabIndents(True)
        editor.setAutoIndent(True)
        editor.setBackspaceUnindents(True)

    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Plik")
        
        new_action = QAction("Nowy", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Otwórz...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Zapisz", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Zapisz jako...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Zakończ", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("Edycja")
        
        undo_action = QAction("Cofnij", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(lambda: self.current_editor() and self.current_editor().undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Ponów", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self.current_editor() and self.current_editor().redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Wytnij", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(lambda: self.current_editor() and self.current_editor().cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Kopiuj", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(lambda: self.current_editor() and self.current_editor().copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Wklej", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(lambda: self.current_editor() and self.current_editor().paste())
        edit_menu.addAction(paste_action)

        run_menu = menu_bar.addMenu("Uruchom")
        run_browser_action = QAction("Uruchom w przeglądarce", self)
        run_browser_action.setShortcut(QKeySequence("F5"))
        run_browser_action.triggered.connect(self.run_in_browser)
        run_menu.addAction(run_browser_action)

    def maybe_save_tab(self, index):
        """Weryfikuje niezapisane zmiany w konkretnej zakładce."""
        editor = self.tabs.widget(index)
        if not editor or not editor.isModified():
            return True

        self.tabs.setCurrentIndex(index)
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("mkHTML - Niezapisane zmiany")
        file_name = os.path.basename(editor.current_file) if editor.current_file else "Nowy plik"
        msg_box.setText(f"Plik '{file_name}' zawiera niezapisane zmiany.\nCzy chcesz je zapisać?")
        
        btn_save = msg_box.addButton("Zapisz", QMessageBox.ButtonRole.AcceptRole)
        btn_discard = msg_box.addButton("Nie zapisuj", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = msg_box.addButton("Anuluj", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        clicked = msg_box.clickedButton()
        if clicked == btn_save:
            return self.save_file()
        elif clicked == btn_cancel:
            return False
            
        return True

    def close_tab(self, index):
        """Zamyka zakładkę po ewentualnym zapisaniu zmian."""
        if self.maybe_save_tab(index):
            self.tabs.removeTab(index)
            if self.tabs.count() == 0:
                self.add_new_tab()

    def closeEvent(self, event):
        """Zamykanie całego programu - sprawdza wszystkie zakładki i zapisuje konfigurację."""
        for i in range(self.tabs.count() - 1, -1, -1):
            if not self.maybe_save_tab(i):
                event.ignore()
                return
        
        self.save_app_config()
        event.accept()

    def run_in_browser(self):
        editor = self.current_editor()
        if not editor:
            return

        if not editor.current_file:
            QMessageBox.information(self, "Zapisz plik", "Przed uruchomieniem w przeglądarce musisz zapisać plik.")
            if not self.save_file_as():
                return
            
        if editor.current_file:
            if editor.current_file.lower().endswith(('.html', '.htm')):
                if editor.isModified():
                    self.save_file()
                webbrowser.open(f"file:///{os.path.abspath(editor.current_file)}")
            else:
                QMessageBox.warning(self, "Uwaga", "Możesz uruchomić w przeglądarce tylko pliki HTML.")

    def new_file(self):
        """Tworzy nową zakładkę z nowym plikiem."""
        self.add_new_tab()

    def open_file(self):
        """Otwiera plik w nowej zakładce (lub zastępuje pustą niezmodyfikowaną)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Otwórz plik", self.working_dir, "Pliki Web (*.html *.htm *.css);;Wszystkie pliki (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                editor = self.current_editor()
                if editor and editor.current_file is None and not editor.isModified() and editor.text() == "":
                    editor.setText(content)
                    editor.current_file = file_path
                    self.update_lexer_for_editor(editor)
                    editor.setModified(False)
                    idx = self.tabs.currentIndex()
                    self.tabs.setTabText(idx, os.path.basename(file_path))
                    self.update_window_title()
                else:
                    self.add_new_tab(file_path=file_path, content=content)

                self.working_dir = os.path.dirname(file_path)
                self.save_app_config()

            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return False

        if editor.current_file:
            try:
                with open(editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(editor.text())
                editor.setModified(False)
                idx = self.tabs.indexOf(editor)
                if idx != -1:
                    self.tabs.setTabText(idx, os.path.basename(editor.current_file))
                self.update_window_title()
                return True
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        editor = self.current_editor()
        if not editor:
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz plik jako", self.working_dir, "Pliki HTML (*.html *.htm);;Pliki CSS (*.css);;Wszystkie pliki (*)"
        )
        if file_path:
            editor.current_file = file_path
            try:
                with open(editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(editor.text())
                editor.setModified(False)
                self.update_lexer_for_editor(editor)
                
                idx = self.tabs.indexOf(editor)
                if idx != -1:
                    self.tabs.setTabText(idx, os.path.basename(file_path))
                    
                self.update_window_title()
                self.working_dir = os.path.dirname(file_path)
                self.save_app_config()
                return True
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
                return False
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MkHTMLEditor()
    window.show()
    sys.exit(app.exec())