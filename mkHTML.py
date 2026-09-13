import sys
import re
import os
import json
import webbrowser
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QAction, QKeySequence, QColor
from PyQt6.QtCore import Qt
from PyQt6.Qsci import QsciScintilla, QsciLexerHTML, QsciLexerCSS

# --- KONFIGURACJA ŚCIEŻEK ---
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
    """Wczytuje konfigurację; jeśli nie ma pliku lub ścieżka nie istnieje, zwraca Pulpit."""
    desktop_path = get_desktop_path()
    if not os.path.exists(CONFIG_FILE):
        save_config(desktop_path)
        return desktop_path

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            saved_dir = config.get("working_dir", desktop_path)
            
            if os.path.exists(saved_dir):
                return saved_dir
            else:
                save_config(desktop_path)
                return desktop_path
    except Exception:
        return desktop_path

def save_config(work_dir):
    """Zapisuje aktualny katalog roboczy do pliku konfiguracyjnego w profilu użytkownika."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"working_dir": work_dir}, f, indent=4)
    except Exception as e:
        print(f"Błąd zapisu konfiguracji: {e}")


class MyCodeEditor(QsciScintilla):
    """Autorska klasa edytora z obsługą autouzupełniania tagów, klamer i wcięć."""
    def __init__(self):
        super().__init__()
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

        # 2. OBSŁUGA SKRÓTÓW (TAB)
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
                "a": ("<a href=\"\"></a>", 0, 9)
            }
            
            match = re.search(r'\b([a-zA-Z0-9_]+)$', line_text)
            if match:
                word = match.group(1)
                if word in snippets:
                    snippet_text, line_offset, col_offset = snippets[word]
                    self.setSelection(line, col - len(word), line, col)
                    self.removeSelectedText()
                    self.insert(snippet_text)
                    if line_offset == 0:
                        self.setCursorPosition(line, col - len(word) + col_offset)
                    else:
                        self.setCursorPosition(line + line_offset, col_offset)
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

        # Domyślna obsługa reszty klawiszy
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
    """Główne okno aplikacji mkHTML v0.0.1.1."""
    def __init__(self):
        super().__init__()
        self.current_file = None 
        self.working_dir = load_config()
        
        self.setWindowTitle("mkHTML v0.0.1.1 - Nowy plik")
        self.setGeometry(100, 100, 900, 650)
        
        self.editor = MyCodeEditor()
        self.editor.setUtf8(True)
        
        self.font = QFont("Consolas", 12)
        self.editor.setFont(self.font)
        self.editor.setMarginsFont(self.font)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginLineNumbers(0, True)
        
        self.update_lexer()
        
        self.setCentralWidget(self.editor)
        self.create_menu()
        self.editor.setModified(False)

    def update_lexer(self):
        def set_color(lex, hex_color, cls_ref, *attrs):
            for attr in attrs:
                if hasattr(cls_ref, attr):
                    lex.setColor(QColor(hex_color), getattr(cls_ref, attr))

        if self.current_file and self.current_file.lower().endswith('.css'):
            lexer = QsciLexerCSS(self.editor)
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
            lexer = QsciLexerHTML(self.editor)
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

        self.editor.setLexer(lexer)
        
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)
        self.editor.setIndentationWidth(4)
        self.editor.setTabIndents(True)
        self.editor.setAutoIndent(True)
        self.editor.setBackspaceUnindents(True)

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
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Ponów", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Wytnij", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Kopiuj", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Wklej", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        run_menu = menu_bar.addMenu("Uruchom")
        run_browser_action = QAction("Uruchom w przeglądarce", self)
        run_browser_action.setShortcut(QKeySequence("F5"))
        run_browser_action.triggered.connect(self.run_in_browser)
        run_menu.addAction(run_browser_action)

    def maybe_save(self):
        """Weryfikacja niezapisanych zmian z polskimi przyciskami."""
        if not self.editor.isModified():
            return True

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("mkHTML - Niezapisane zmiany")
        msg_box.setText("Dokument zawiera niezapisane zmiany.\nCzy chcesz je zapisać?")
        
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

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def run_in_browser(self):
        if not self.current_file:
            QMessageBox.information(self, "Zapisz plik", "Przed uruchomieniem w przeglądarce musisz zapisać plik.")
            if not self.save_file_as():
                return
            
        if self.current_file:
            if self.current_file.lower().endswith(('.html', '.htm')):
                if self.editor.isModified():
                    self.save_file()
                webbrowser.open(f"file:///{os.path.abspath(self.current_file)}")
            else:
                QMessageBox.warning(self, "Uwaga", "Możesz uruchomić w przeglądarce tylko pliki HTML.")

    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("mkHTML v0.0.1.1 - Nowy plik")
            self.update_lexer()
            self.editor.setModified(False)

    def open_file(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Otwórz plik", self.working_dir, "Pliki Web (*.html *.htm *.css);;Wszystkie pliki (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.editor.setText(f.read())
                    self.current_file = file_path
                    self.setWindowTitle(f"mkHTML v0.0.1.1 - {os.path.basename(file_path)}")
                    self.update_lexer()
                    self.editor.setModified(False)
                    
                    self.working_dir = os.path.dirname(file_path)
                    save_config(self.working_dir)
                    
                except Exception as e:
                    QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.text())
                self.editor.setModified(False)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz plik jako", self.working_dir, "Pliki HTML (*.html *.htm);;Pliki CSS (*.css);;Wszystkie pliki (*)"
        )
        if file_path:
            self.current_file = file_path
            self.setWindowTitle(f"mkHTML v0.0.1.1 - {os.path.basename(file_path)}")
            
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.text())
                self.editor.setModified(False)
                self.update_lexer()
                
                self.working_dir = os.path.dirname(file_path)
                save_config(self.working_dir)
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