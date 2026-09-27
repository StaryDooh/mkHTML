import sys
import re
import os
import time
import webbrowser
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtGui import QFont, QFontDatabase, QAction, QKeySequence, QColor, QIcon
from PyQt6.QtCore import Qt, QRect
from PyQt6.Qsci import QsciScintilla, QsciLexerHTML, QsciLexerCSS

# --- IMPORT Z ZEWNĘTRZNYCH MODUŁÓW ---
from config import THEMES, LOG_FILE, get_desktop_path, load_config, save_config
from file_utils import read_text_file, _atomic_save

# --- MAPOWANIE EOL ---
EOL = {
    QsciScintilla.EolMode.EolWindows: '\r\n',
    QsciScintilla.EolMode.EolUnix: '\n',
    QsciScintilla.EolMode.EolMac: '\r'
}

# --- LOGOWANIE I OBSŁUGA BŁĘDÓW ---
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

class MyCodeEditor(QsciScintilla):
    """Autorska klasa edytora z obsługą autouzupełniania tagów, klamer, wcięć i snippetów."""
    def __init__(self):
        super().__init__()
        
        if os.name == 'nt':
            self.setEolMode(QsciScintilla.EolMode.EolWindows)
        else:
            self.setEolMode(QsciScintilla.EolMode.EolUnix)
        
        self.current_file = None
        self.file_encoding = 'utf-8'
        self.void_tags = {'br', 'hr', 'img', 'input', 'meta', 'link', 'base', 'area', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
        
        self.known_tags = {
            'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'blockquote',
            'body', 'br', 'button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist',
            'dd', 'del', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption',
            'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr',
            'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map',
            'mark', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p',
            'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section',
            'select', 'small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup', 'svg', 'table',
            'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'u',
            'ul', 'var', 'video', 'wbr'
        }
        
        self.rx_indent = re.compile(r'^([ \t]*)')
        self.rx_tag_trigger = re.compile(r'<?([a-zA-Z0-9-]+)>?\s*$')
        self.rx_close_tag = re.compile(r'<([a-zA-Z0-9-]+)[^>]*>$')

        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagByText)
        self.setWrapIndentMode(QsciScintilla.WrapIndentMode.WrapIndentSame)

    def get_eol(self):
        """Zwraca aktywny ciąg EOL ustawiony w edytorze."""
        mode = self.eolMode()
        return EOL.get(mode, '\n')

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        line, col = self.getCursorPosition()
        eol = self.get_eol()

        needs_line_parse = key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab) or text in ('{', '"', "'", '>')
        full_line_text = self.text(line) if needs_line_parse else ""

        # 0. INTELIGENTNY ENTER MIĘDZY TAGAMI (np. <p>|</p> + Enter)
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not self.hasSelectedText():
            if 0 < col < len(full_line_text) and full_line_text[col-1] == '>' and full_line_text[col:col+2] == '</':
                indent_match = self.rx_indent.match(full_line_text)
                indent_str = indent_match.group(1) if indent_match else ""
                
                self.insert(f"{eol}{indent_str}    {eol}{indent_str}")
                self.setCursorPosition(line + 1, len(indent_str) + 4)
                return
            
            super().keyPressEvent(event)
            return

        # 1. OBSŁUGA SKRÓTÓW (TAB) I DYNAMICZNEGO ROZWIJANIA TAGÓW
        if key == Qt.Key.Key_Tab and not self.hasSelectedText():
            search_start = max(0, col - 200)
            chunk_before_cursor = full_line_text[search_start:col]
            
            if not chunk_before_cursor.endswith('>'):
                match = self.rx_tag_trigger.search(chunk_before_cursor)
                
                if match:
                    word = match.group(1).lower()
                    matched_full_text = match.group(0)
                    replace_len = len(matched_full_text)
                    start_col = max(0, col - replace_len)
                    
                    is_html_mode = isinstance(self.lexer(), QsciLexerHTML)
                    is_valid_tag = word in self.known_tags
                    
                    pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
                    style = self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, max(0, pos - 1))
                    is_valid_context = not is_html_mode or style in (0, 1, 2)
                    
                    if is_valid_context and (word == "lorem" or (is_html_mode and is_valid_tag)):
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
                        
                        indent_match = self.rx_indent.match(full_line_text)
                        current_indent = indent_match.group(1) if indent_match else ""
                        
                        self.setSelection(line, start_col, line, col)
                        self.removeSelectedText()
                        
                        if word in snippets:
                            snippet_text, line_offset, col_offset = snippets[word]
                            snippet_text = snippet_text.replace('\n', eol)
                            
                            if current_indent and eol in snippet_text:
                                lines = snippet_text.split(eol)
                                snippet_text = lines[0] + eol + eol.join(current_indent + l for l in lines[1:])
                            
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
            if self.hasSelectedText():
                line_from, index_from, line_to, index_to = self.getSelection()
                sel_text = self.selectedText()
                self.replaceSelectedText("{" + sel_text + "}")
                if line_from == line_to:
                    self.setSelection(line_from, index_from, line_to, index_to + 2)
                return

            indent_match = self.rx_indent.match(full_line_text)
            indent_str = indent_match.group(1) if indent_match else ""
            
            super().keyPressEvent(event)
            self.insert(f"{eol}{indent_str}    {eol}{indent_str}}}")
            self.setCursorPosition(line + 1, len(indent_str) + 4)
            return

        # 3. OBSŁUGA CUDZYSŁOWÓW I APOSTROFÓW (" oraz ')
        if text in ['"', "'"]:
            if self.hasSelectedText():
                line_from, index_from, line_to, index_to = self.getSelection()
                sel_text = self.selectedText()
                self.replaceSelectedText(text + sel_text + text)
                if line_from == line_to:
                    self.setSelection(line_from, index_from, line_to, index_to + 2)
                return

            if col < len(full_line_text) and full_line_text[col] == text:
                self.setCursorPosition(line, col + 1)
                return
            
            char_before = full_line_text[col-1] if col > 0 else ''
            if char_before.isalnum():
                super().keyPressEvent(event)
                return
            
            super().keyPressEvent(event)
            self.insert(text)
            self.setCursorPosition(line, col + 1)
            return

        # 4. OBSŁUGA AUTOMATYCZNEGO ZAMYKANIA ZNACZNIKÓW HTML (>)
        if text == '>':
            if self.hasSelectedText():
                super().keyPressEvent(event)
                return
                
            search_start = max(0, col - 200)
            chunk_before_cursor = full_line_text[search_start:col] + '>'
            
            super().keyPressEvent(event)
            
            if isinstance(self.lexer(), QsciLexerHTML):
                match = self.rx_close_tag.search(chunk_before_cursor)
                if match:
                    inner_content = match.group(0)[:-1].rstrip()
                    if not inner_content.endswith('/'):
                        tag_name = match.group(1).lower()
                        
                        pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
                        style_before = self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, max(0, pos - 2))
                        
                        if tag_name in self.known_tags and tag_name not in self.void_tags and style_before < 40:
                            closing_tag = f"</{tag_name}>"
                            self.insert(closing_tag)
                            self.setCursorPosition(line, col + 1)
            return

        super().keyPressEvent(event)


class MkHTMLEditor(QMainWindow):
    """Główne okno aplikacji mkHTML z obsługą zakładek i zapamiętywaniem stanu okna."""
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.working_dir = self.config.get("working_dir", get_desktop_path())
        self.current_theme = self.config.get("theme", "jasny")
        
        families = QFontDatabase.families()
        modern_fonts = ["JetBrains Mono", "Fira Code", "Cascadia Code", "Hack", "Roboto Mono", "Consolas", "Courier New"]
        chosen_font = "Consolas"
        
        for mf in modern_fonts:
            if mf in families:
                chosen_font = mf
                break
        
        self.font = QFont(chosen_font, 12)
        
        self.setWindowTitle("mkHTML v1.0.3.1")
        
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
        self.setStyleSheet(THEMES.get(self.current_theme, THEMES["jasny"]).get("app_qss", ""))
        
        self.create_menu()
        self.add_new_tab()

    def save_app_config(self):
        geom = self.geometry()
        config_data = {
            "working_dir": self.working_dir,
            "x": geom.x(),
            "y": geom.y(),
            "width": geom.width(),
            "height": geom.height(),
            "theme": self.current_theme
        }
        save_config(config_data)

    def current_editor(self) -> MyCodeEditor:
        return self.tabs.currentWidget()

    def add_new_tab(self, file_path=None, content="", encoding='utf-8', eol_mode=None):
        """Dodaje nową zakładkę z konfiguracją kodowania i końców linii."""
        editor = MyCodeEditor()
        editor.setUtf8(True)
        editor.setFont(self.font)
        editor.setMarginsFont(self.font)
        editor.setMarginWidth(0, "0000")
        editor.setMarginLineNumbers(0, True)
        
        editor.current_file = file_path
        editor.file_encoding = encoding
        
        if eol_mode is not None:
            editor.setEolMode(eol_mode)
        
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
        idx = self.tabs.indexOf(editor)
        if idx != -1:
            base_name = os.path.basename(editor.current_file) if editor.current_file else "Nowy plik"
            title = f"{base_name} *" if modified else base_name
            self.tabs.setTabText(idx, title)
            self.update_window_title()

    def update_window_title(self):
        editor = self.current_editor()
        if editor:
            file_str = editor.current_file if editor.current_file else "Nowy plik"
            mod_str = " *" if editor.isModified() else ""
            self.setWindowTitle(f"mkHTML v1.0.3.1 - {file_str}{mod_str}")
        else:
            self.setWindowTitle("mkHTML v1.0.3.1")

    def update_lexer_for_editor(self, editor):
        theme_data = THEMES.get(self.current_theme, THEMES["jasny"])
        old_lexer = editor.lexer()

        def reset_lexer_styles(lex):
            bg_color = QColor(theme_data["bg"])
            fg_color = QColor(theme_data["fg"])
            for i in range(128):
                lex.setColor(fg_color, i)
                lex.setPaper(bg_color, i)
                lex.setFont(self.font, i)

        def set_color(lex, hex_color, cls_ref, *attrs):
            for attr in attrs:
                if hasattr(cls_ref, attr):
                    lex.setColor(QColor(hex_color), getattr(cls_ref, attr))
                    lex.setPaper(QColor(theme_data["bg"]), getattr(cls_ref, attr))

        def apply_html_lexer():
            lexer = QsciLexerHTML(editor)
            reset_lexer_styles(lexer)
            
            html_colors = theme_data["html"]
            set_color(lexer, html_colors["tag"], QsciLexerHTML, 'Tag', 'UnknownTag')
            set_color(lexer, html_colors["attr"], QsciLexerHTML, 'Attribute', 'UnknownAttribute')
            set_color(lexer, html_colors["string"], QsciLexerHTML, 'HTMLDoubleQuotedString', 'HTMLSingleQuotedString')
            set_color(lexer, html_colors["entity"], QsciLexerHTML, 'Entity')
            
            if hasattr(QsciLexerHTML, 'HTMLComment'):
                comment_font = QFont(self.font)
                comment_font.setItalic(True)
                lexer.setColor(QColor(html_colors["comment"]), QsciLexerHTML.HTMLComment)
                lexer.setPaper(QColor(theme_data["bg"]), QsciLexerHTML.HTMLComment)
                lexer.setFont(comment_font, QsciLexerHTML.HTMLComment)
            return lexer

        def apply_css_lexer():
            lexer = QsciLexerCSS(editor)
            reset_lexer_styles(lexer)
            
            css_colors = theme_data["css"]
            set_color(lexer, css_colors["tag"], QsciLexerCSS, 'Tag')
            set_color(lexer, css_colors["class"], QsciLexerCSS, 'ClassSelector')
            set_color(lexer, css_colors["id"], QsciLexerCSS, 'IDSelector')
            set_color(lexer, css_colors["prop"], QsciLexerCSS, 'CSS1Property', 'CSS2Property', 'CSS3Property', 'UnknownProperty')
            set_color(lexer, css_colors["val"], QsciLexerCSS, 'Value')
            set_color(lexer, css_colors["string"], QsciLexerCSS, 'DoubleQuotedString', 'SingleQuotedString', 'String')
            set_color(lexer, css_colors["pseudo"], QsciLexerCSS, 'PseudoClass')
            
            if hasattr(QsciLexerCSS, 'Comment'):
                comment_font = QFont(self.font)
                comment_font.setItalic(True)
                lexer.setColor(QColor(css_colors["comment"]), QsciLexerCSS.Comment)
                lexer.setPaper(QColor(theme_data["bg"]), QsciLexerCSS.Comment)
                lexer.setFont(comment_font, QsciLexerCSS.Comment)
            return lexer

        new_lexer = None
        if editor.current_file and editor.current_file.lower().endswith('.css'):
            new_lexer = apply_css_lexer()
        else:
            new_lexer = apply_html_lexer()

        editor.setLexer(new_lexer)
        if old_lexer is not None:
            old_lexer.deleteLater()

        editor.setPaper(QColor(theme_data["bg"]))
        editor.setColor(QColor(theme_data["fg"]))
        editor.setCaretForegroundColor(QColor(theme_data["caret"]))
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(QColor(theme_data["caret_line"]))
        editor.setSelectionBackgroundColor(QColor(theme_data["selection_bg"]))
        editor.setSelectionForegroundColor(QColor(theme_data["selection_fg"]))
        
        editor.setMarginsBackgroundColor(QColor(theme_data["margin_bg"]))
        editor.setMarginsForegroundColor(QColor(theme_data["margin_fg"]))

        editor.setIndentationsUseTabs(False)
        editor.setTabWidth(4)
        editor.setIndentationWidth(4)
        editor.setTabIndents(True)
        editor.setAutoIndent(True)
        editor.setBackspaceUnindents(True)

    def set_theme(self, theme_key):
        if theme_key not in THEMES:
            return
        
        self.current_theme = theme_key
        
        for tk, action in self.theme_actions.items():
            action.setChecked(tk == theme_key)
        
        self.setStyleSheet(THEMES[theme_key].get("app_qss", ""))
        
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor:
                self.update_lexer_for_editor(editor)
        
        self.save_app_config()

    def _add_action(self, parent_menu, text, slot, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        parent_menu.addAction(action)
        return action

    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Plik")
        self._add_action(file_menu, "Nowy", self.new_file, QKeySequence.StandardKey.New)
        self._add_action(file_menu, "Otwórz...", self.open_file, QKeySequence.StandardKey.Open)
        self._add_action(file_menu, "Zapisz", self.save_file, QKeySequence.StandardKey.Save)
        self._add_action(file_menu, "Zapisz jako...", self.save_file_as)
        file_menu.addSeparator()
        self._add_action(file_menu, "Zakończ", self.close, QKeySequence.StandardKey.Quit)
        
        edit_menu = menu_bar.addMenu("Edycja")
        self._add_action(edit_menu, "Cofnij", lambda: self.current_editor() and self.current_editor().undo(), QKeySequence.StandardKey.Undo)
        self._add_action(edit_menu, "Ponów", lambda: self.current_editor() and self.current_editor().redo(), QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Wytnij", lambda: self.current_editor() and self.current_editor().cut(), QKeySequence.StandardKey.Cut)
        self._add_action(edit_menu, "Kopiuj", lambda: self.current_editor() and self.current_editor().copy(), QKeySequence.StandardKey.Copy)
        self._add_action(edit_menu, "Wklej", lambda: self.current_editor() and self.current_editor().paste(), QKeySequence.StandardKey.Paste)

        theme_menu = menu_bar.addMenu("Motyw")
        self.theme_actions = {}
        for theme_key, theme_info in THEMES.items():
            action = QAction(theme_info["name"], self)
            action.setCheckable(True)
            action.setChecked(theme_key == self.current_theme)
            action.triggered.connect(lambda checked, tk=theme_key: self.set_theme(tk))
            theme_menu.addAction(action)
            self.theme_actions[theme_key] = action

        self._add_action(menu_bar, "Podgląd", self.run_in_browser, QKeySequence("F5"))

        visit_menu = menu_bar.addMenu("Odwiedź...")
        self._add_action(visit_menu, "Pobierz najnowszą wersję", lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/releases"))
        self._add_action(visit_menu, "Zgłoś błąd", lambda: webbrowser.open("https://github.com/StaryDooh/mkHTML/issues"))
        self._add_action(visit_menu, "Zrelaksuj się", lambda: webbrowser.open("https://www.youtube.com/@StaryDooh"))

    def maybe_save_tab(self, index):
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
        msg_box.addButton("Nie zapisuj", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = msg_box.addButton("Anuluj", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        clicked = msg_box.clickedButton()
        if clicked == btn_save:
            return self.save_file()
        elif clicked == btn_cancel:
            return False
        
        return True

    def close_tab(self, index):
        if self.maybe_save_tab(index):
            editor = self.tabs.widget(index)
            self.tabs.removeTab(index)
            if editor:
                editor.deleteLater()
            if self.tabs.count() == 0:
                self.add_new_tab()

    def closeEvent(self, event):
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
                if editor.isModified() and not self.save_file():
                    return
                
                safe_url = Path(editor.current_file).resolve().as_uri()
                webbrowser.open(safe_url)
            else:
                QMessageBox.warning(self, "Uwaga", "Możesz uruchomić w przeglądarce tylko pliki HTML.")

    def new_file(self):
        self.add_new_tab()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Otwórz plik", self.working_dir, "Pliki Web (*.html *.htm *.css);;Wszystkie pliki (*)"
        )
        if not file_path:
            return

        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor and editor.current_file:
                is_duplicate = False
                try:
                    is_duplicate = os.path.samefile(file_path, editor.current_file)
                except (FileNotFoundError, OSError):
                    is_duplicate = (os.path.normcase(os.path.abspath(file_path)) 
                                    == os.path.normcase(os.path.abspath(editor.current_file)))
                
                if is_duplicate:
                    self.tabs.setCurrentIndex(i)
                    return

        try:
            content, encoding, eol_mode = read_text_file(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Błąd otwarcia pliku", f"Nie udało się otworzyć pliku:\n{e}")
            return

        curr_ed = self.current_editor()
        
        if (curr_ed is not None and curr_ed.current_file is None 
                and not curr_ed.isModified() and curr_ed.text() == ""):
            
            curr_ed.file_encoding = encoding
            if eol_mode is not None:
                curr_ed.setEolMode(eol_mode)
            
            curr_ed.current_file = file_path
            curr_ed.setText(content)
            self.update_lexer_for_editor(curr_ed)
            curr_ed.setModified(False)
            
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
            self.update_window_title()
        else:
            self.add_new_tab(file_path=file_path, content=content, encoding=encoding, eol_mode=eol_mode)

        self.working_dir = os.path.dirname(os.path.abspath(file_path))

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return False

        if editor.current_file:
            try:
                _atomic_save(editor.current_file, editor.text(), encoding=editor.file_encoding)
                editor.setModified(False)
                idx = self.tabs.indexOf(editor)
                if idx != -1:
                    self.tabs.setTabText(idx, os.path.basename(editor.current_file))
                self.update_window_title()
                return True
            except UnicodeEncodeError:
                reply = QMessageBox.question(
                    self,
                    "Błąd kodowania znaków",
                    f"Plik zawiera znaki, których nie można zapisać w kodowaniu {editor.file_encoding}.\n"
                    f"Czy chcesz zmienić kodowanie pliku na UTF-8 i zapisać?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    editor.file_encoding = 'utf-8'
                    return self.save_file()
                return False
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self, *args):
        editor = self.current_editor()
        if not editor:
            return False

        if args and isinstance(args[0], str):
            file_path = args[0]
            selected_filter = ""
        else:
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Zapisz plik jako", self.working_dir, "Pliki HTML (*.html *.htm);;Pliki CSS (*.css);;Wszystkie pliki (*)"
            )
            
        if not file_path:
            return False

        if not os.path.splitext(file_path)[1]:
            if 'HTML' in selected_filter:
                file_path += '.html'
            elif 'CSS' in selected_filter:
                file_path += '.css'

        try:
            _atomic_save(file_path, editor.text(), encoding=editor.file_encoding)
            
            editor.current_file = file_path
            editor.setModified(False)
            self.update_lexer_for_editor(editor)
            
            idx = self.tabs.indexOf(editor)
            if idx != -1:
                self.tabs.setTabText(idx, os.path.basename(file_path))
            
            self.update_window_title()
            self.working_dir = os.path.dirname(os.path.abspath(file_path))
            return True
            
        except UnicodeEncodeError:
            reply = QMessageBox.question(
                self,
                "Błąd kodowania znaków",
                f"Plik zawiera znaki, których nie można zapisać w kodowaniu {editor.file_encoding}.\n"
                f"Czy chcesz zmienić kodowanie pliku na UTF-8 i zapisać?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                editor.file_encoding = 'utf-8'
                return self.save_file_as(file_path)
            return False
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys.excepthook = _excepthook
    window = MkHTMLEditor()
    window.show()
    sys.exit(app.exec())