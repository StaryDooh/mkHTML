import sys
import re
import os
import json
import webbrowser
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtGui import QFont, QAction, QKeySequence, QColor, QIcon
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QRect
from PyQt6.Qsci import QsciScintilla, QsciLexerHTML, QsciLexerCSS

# --- KONFIGURACJA ŚCIEŻEK I USTAWIEŃ ---
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mkhtml_config.json")

def get_desktop_path():
    """Pobiera ścieżkę do Pulpitu za pomocą wbudowanych i bezpiecznych mechanizmów Qt."""
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)

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
            
            saved_dir = config.get("working_dir", desktop_path)
            if not os.path.exists(saved_dir):
                config["working_dir"] = desktop_path
            
            for key in ["x", "y", "width", "height"]:
                if key not in config or not isinstance(config[key], int):
                    config[key] = default_config[key]
                    
            config["x"] = max(0, config["x"])
            config["y"] = max(0, config["y"])
            
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
    """Autorska klasa edytora z obsługą autouzupełniania tagów, klamer, wcięć i snippetów."""
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.file_encoding = 'utf-8'
        self.void_tags = {'br', 'hr', 'img', 'input', 'meta', 'link', 'base', 'area', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
        
        # Prekompilacja wyrażeń regularnych dla maksymalnej wydajności
        self.rx_indent = re.compile(r'^([ \t]*)')
        self.rx_tag_trigger = re.compile(r'<?([a-zA-Z0-9-]+)>?\s*$')
        self.rx_valid_tag = re.compile(r'^[a-zA-Z0-9-]+$')
        self.rx_close_tag = re.compile(r'<([a-zA-Z0-9-]+)[^>]*>$')

        # Automatyczne zawijanie wierszy na słowach
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagByText)
        
        # Wyrównanie zawiniętego tekstu do wcięcia pierwszej linii
        self.setWrapIndentMode(QsciScintilla.WrapIndentMode.WrapIndentSame)

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        line, col = self.getCursorPosition()

        # Pobieranie tekstu linii tylko gdy zdarzenie wymaga analizy skrótów/składni
        needs_line_parse = key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab) or text in ('{', '"', "'", '>')
        full_line_text = self.text(line) if needs_line_parse else ""

        # 0. INTELIGENTNY ENTER MIĘDZY TAGAMI (np. <p>|</p> + Enter)
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not self.hasSelectedText():
            if 0 < col < len(full_line_text) and full_line_text[col-1] == '>' and full_line_text[col:col+2] == '</':
                indent_match = self.rx_indent.match(full_line_text)
                indent_str = indent_match.group(1) if indent_match else ""
                
                self.insert(f"\n{indent_str}    \n{indent_str}")
                self.setCursorPosition(line + 1, len(indent_str) + 4)
                return
            
            super().keyPressEvent(event)
            return

        # 1. OBSŁUGA SKRÓTÓW (TAB) I DYNAMICZNEGO ROZWIJANIA TAGÓW ORAZ LOREM IPSUM
        if key == Qt.Key.Key_Tab and not self.hasSelectedText():
            search_start = max(0, col - 200)
            chunk_before_cursor = full_line_text[search_start:col]
            match = self.rx_tag_trigger.search(chunk_before_cursor)
            
            if match:
                word = match.group(1).lower()
                matched_full_text = match.group(0)
                replace_len = len(matched_full_text)
                start_col = max(0, col - replace_len)
                
                is_html_mode = isinstance(self.lexer(), QsciLexerHTML) or self.lexer() is None
                is_valid_tag = bool(self.rx_valid_tag.match(word))
                
                if word == "lorem" or is_html_mode:
                    lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
                    
                    snippets = {
                        "html": (
                            "<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n"
                            "    <meta charset=\"UTF-8\">\n"
                            "    <title>Tytuł strony</title>\n"
                            "    <link rel=\"stylesheet\" href=\"style.css\">\n"
                            "</head>\n<body>\n    \n</body>\n</html>", 8, 4
                        ),
                        "a": ('<a href=""></a>', 0, 9),
                        "img": ('<img src="" alt="">', 0, 10),
                        "lorem": (lorem_text, 0, len(lorem_text))
                    }
                    
                    if word in snippets or word in self.void_tags or (is_html_mode and is_valid_tag):
                        indent_match = self.rx_indent.match(full_line_text)
                        current_indent = indent_match.group(1) if indent_match else ""
                        
                        self.setSelection(line, start_col, line, col)
                        self.removeSelectedText()
                        
                        if word in snippets:
                            snippet_text, line_offset, col_offset = snippets[word]
                            
                            if current_indent and '\n' in snippet_text:
                                lines = snippet_text.split('\n')
                                snippet_text = lines[0] + '\n' + '\n'.join(current_indent + l for l in lines[1:])
                                
                            self.insert(snippet_text)
                            
                            if line_offset == 0:
                                self.setCursorPosition(line, start_col + col_offset)
                            else:
                                self.setCursorPosition(line + line_offset, len(current_indent) + col_offset)
                            return
                            
                        elif word in self.void_tags:
                            tag_text = f"<{word}>"
                            self.insert(tag_text)
                            self.setCursorPosition(line, start_col + len(tag_text))
                            return
                        else:
                            tag_text = f"<{word}></{word}>"
                            self.insert(tag_text)
                            self.setCursorPosition(line, start_col + len(word) + 2)
                            return

            super().keyPressEvent(event)
            return

        # 2. OBSŁUGA ZAMYKANIA KLAMER DLA CSS ({)
        if text == '{' and isinstance(self.lexer(), QsciLexerCSS):
            indent_match = self.rx_indent.match(full_line_text)
            indent_str = indent_match.group(1) if indent_match else ""
            
            super().keyPressEvent(event)
            self.insert(f"\n{indent_str}    \n{indent_str}}}")
            self.setCursorPosition(line + 1, len(indent_str) + 4)
            return

        # 3. OBSŁUGA CUDZYSŁOWÓW I APOSTROFÓW (" oraz ')
        if text in ['"', "'"]:
            if col < len(full_line_text) and full_line_text[col] == text:
                self.setCursorPosition(line, col + 1)
                return
            
            super().keyPressEvent(event)
            self.insert(text)
            self.setCursorPosition(line, col + 1)
            return

        # 4. OBSŁUGA AUTOMATYCZNEGO ZAMYKANIA ZNACZNIKÓW HTML (>)
        if text == '>':
            search_start = max(0, col - 200)
            chunk_before_cursor = full_line_text[search_start:col] + '>'
            
            super().keyPressEvent(event)
            
            match = self.rx_close_tag.search(chunk_before_cursor)
            if match:
                tag_name = match.group(1).lower()
                if tag_name not in self.void_tags:
                    closing_tag = f"</{tag_name}>"
                    self.insert(closing_tag)
                    self.setCursorPosition(line, col + 1)
            return

        super().keyPressEvent(event)


class MkHTMLEditor(QMainWindow):
    """Główne okno aplikacji mkHTML z obsługą zakładek, ikony i zapamiętywaniem stanu okna."""
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.working_dir = self.config.get("working_dir", get_desktop_path())
        self.font = QFont("Consolas", 12)
        
        self.setWindowTitle("mkHTML v1.0.1.0")
        
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_dir, "ikona.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        x = self.config.get("x", 100)
        y = self.config.get("y", 100)
        w = self.config.get("width", 950)
        h = self.config.get("height", 680)
        
        # Precyzyjna weryfikacja widoczności okna na dostępnych monitorach (odporność na odpięty monitor)
        window_rect = QRect(x, y, w, h)
        is_visible = False
        for screen in QApplication.screens():
            intersection = screen.availableGeometry().intersected(window_rect)
            if intersection.width() >= 100 and intersection.height() >= 100:
                is_visible = True
                break
                
        if not is_visible:
            primary_geom = QApplication.primaryScreen().availableGeometry()
            x = primary_geom.x() + (primary_geom.width() - w) // 2
            y = primary_geom.y() + (primary_geom.height() - h) // 2
            
        self.setGeometry(x, y, w, h)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_window_title)
        
        self.setCentralWidget(self.tabs)
        self.create_menu()
        
        self.add_new_tab()

    def _atomic_save(self, file_path, content, encoding='utf-8'):
        """Bezpieczny, zablokowany przed kolizjami zapis pliku (Path-safe, AV-safe)."""
        abs_file_path = os.path.abspath(file_path)
        dir_name = os.path.dirname(abs_file_path)
        
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".mkhtml_save_", suffix=".tmp")
        
        try:
            try:
                with os.fdopen(fd, 'w', encoding=encoding) as f:
                    f.write(content)
            except Exception:
                os.close(fd)
                raise

            try:
                os.replace(tmp_path, abs_file_path)
            except OSError:
                with open(abs_file_path, 'w', encoding=encoding) as f_dest:
                    f_dest.write(content)
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise e

    def save_app_config(self):
        """Zapisuje bieżący katalog roboczy oraz geometrię okna na dysku."""
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
            self.setWindowTitle(f"mkHTML v1.0.1.0 - {file_str}{mod_str}")
        else:
            self.setWindowTitle("mkHTML v1.0.1.0")

    def update_lexer_for_editor(self, editor):
        """Ustawia odpowiedni lexer (HTML/CSS/Brak) oraz czyści stary z pamięci."""
        old_lexer = editor.lexer()

        def set_color(lex, hex_color, cls_ref, *attrs):
            for attr in attrs:
                if hasattr(cls_ref, attr):
                    lex.setColor(QColor(hex_color), getattr(cls_ref, attr))

        def apply_html_lexer():
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
            return lexer

        new_lexer = None
        if editor.current_file:
            lower_path = editor.current_file.lower()
            if lower_path.endswith('.css'):
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
                new_lexer = lexer
            elif lower_path.endswith(('.html', '.htm')):
                new_lexer = apply_html_lexer()
        else:
            new_lexer = apply_html_lexer()

        editor.setLexer(new_lexer)
        if old_lexer is not None:
            old_lexer.deleteLater()

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

        preview_action = QAction("Podgląd", self)
        preview_action.setShortcut(QKeySequence("F5"))
        preview_action.triggered.connect(self.run_in_browser)
        menu_bar.addAction(preview_action)

        visit_menu = menu_bar.addMenu("Odwiedź...")
        
        update_action = QAction("Pobierz najnowszą wersję", self)
        update_action.triggered.connect(lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/releases"))
        visit_menu.addAction(update_action)
        
        bug_action = QAction("Zgłoś błąd", self)
        bug_action.triggered.connect(lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/issues"))
        visit_menu.addAction(bug_action)
        
        relax_action = QAction("Zrelaksuj się", self)
        relax_action.triggered.connect(lambda: webbrowser.open("https://www.youtube.com/@StaryDooh"))
        visit_menu.addAction(relax_action)

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
        """Zamyka zakładkę po ewentualnym zapisaniu zmian i zwalnia pamięć edytora."""
        if self.maybe_save_tab(index):
            editor = self.tabs.widget(index)
            self.tabs.removeTab(index)
            if editor:
                editor.deleteLater()
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
                url = QUrl.fromLocalFile(os.path.abspath(editor.current_file)).toString()
                webbrowser.open(url)
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
                encoding_used = 'utf-8'
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='cp1250') as f:
                            content = f.read()
                        encoding_used = 'cp1250'
                    except UnicodeDecodeError:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()

                editor = self.current_editor()
                if editor and editor.current_file is None and not editor.isModified() and editor.text() == "":
                    editor.setText(content)
                    editor.current_file = file_path
                    editor.file_encoding = encoding_used
                    self.update_lexer_for_editor(editor)
                    editor.setModified(False)
                    idx = self.tabs.currentIndex()
                    self.tabs.setTabText(idx, os.path.basename(file_path))
                    self.update_window_title()
                else:
                    new_editor = self.add_new_tab(file_path=file_path, content=content)
                    new_editor.file_encoding = encoding_used

                self.working_dir = os.path.dirname(os.path.abspath(file_path))

            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return False

        if editor.current_file:
            try:
                self._atomic_save(editor.current_file, editor.text(), encoding=editor.file_encoding)
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
                self._atomic_save(editor.current_file, editor.text(), encoding=editor.file_encoding)
                editor.setModified(False)
                self.update_lexer_for_editor(editor)
                
                idx = self.tabs.indexOf(editor)
                if idx != -1:
                    self.tabs.setTabText(idx, os.path.basename(file_path))
                    
                self.update_window_title()
                self.working_dir = os.path.dirname(os.path.abspath(file_path))
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