# editor.py
import os
import re

from PyQt6.QtCore import Qt
from PyQt6.Qsci import QsciScintilla, QsciLexerHTML, QsciLexerCSS

from snippets import VOID_TAGS, KNOWN_TAGS, SNIPPETS

# --- MAPOWANIE EOL ---
EOL = {
    QsciScintilla.EolMode.EolWindows: '\r\n',
    QsciScintilla.EolMode.EolUnix: '\n',
    QsciScintilla.EolMode.EolMac: '\r'
}


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
        self.void_tags = VOID_TAGS
        self.known_tags = KNOWN_TAGS
        
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
                        indent_match = self.rx_indent.match(full_line_text)
                        current_indent = indent_match.group(1) if indent_match else ""
                        
                        self.setSelection(line, start_col, line, col)
                        self.removeSelectedText()
                        
                        if word in SNIPPETS:
                            snippet_text, line_offset, col_offset = SNIPPETS[word]
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