# snippets.py
"""
Moduł zawierający dane statyczne dla edytora: 
szablony autouzupełniania (snippets) oraz zbiory tagów HTML.
"""

# Zbiór tagów samozamykających (void tags)
VOID_TAGS = {
    'br', 'hr', 'img', 'input', 'meta', 'link', 'base', 'area', 
    'col', 'embed', 'param', 'source', 'track', 'wbr'
}

# Pełna lista rozpoznawanych tagów HTML
KNOWN_TAGS = {
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

# Tekst wypełniający
LOREM_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# Słownik szablonów (struktura: krotka(tekst_do_wstawienia, offset_linii, offset_kolumny))
SNIPPETS = {
    "html": (
        "<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n"
        "    <meta charset=\"UTF-8\">\n"
        "    <title>Tytuł strony</title>\n"
        "    <link rel=\"stylesheet\" href=\"style.css\">\n"
        "</head>\n<body>\n    \n</body>\n</html>", 8, 4
    ),
    "a": ('<a href=""></a>', 0, 9),
    "img": ('<img src="" alt="">', 0, 10),
    "lorem": (LOREM_TEXT, 0, len(LOREM_TEXT))
}