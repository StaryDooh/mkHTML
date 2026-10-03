import os
import re
import time
import codecs
import shutil
import tempfile
from pathlib import Path

from PyQt6.Qsci import QsciScintilla

# --- MAPOWANIE EOL ---
EOL = {
    QsciScintilla.EolMode.EolWindows: '\r\n',
    QsciScintilla.EolMode.EolUnix: '\n',
    QsciScintilla.EolMode.EolMac: '\r'
}

# Deklaracja kodowania w pliku: <meta charset="..."> / <meta http-equiv="Content-Type" content="...; charset=...">
# oraz @charset "..."; na początku pliku CSS. Szukamy w pierwszych kilobajtach, w bajtach (ASCII).
_RX_META_CHARSET = re.compile(rb'<meta[^>]*?charset\s*=\s*["\']?\s*([\w.:\-]+)', re.IGNORECASE | re.DOTALL)
_RX_CSS_CHARSET = re.compile(rb'^\s*@charset\s+["\']([\w.:\-]+)["\']', re.IGNORECASE)
_DECLARATION_SCAN_BYTES = 4096

def _declared_encoding(raw):
    """Zwraca nazwę kodowania zadeklarowanego w pliku HTML/CSS (nazwa kodeka Pythona) lub None."""
    head = raw[:_DECLARATION_SCAN_BYTES]
    match = _RX_META_CHARSET.search(head) or _RX_CSS_CHARSET.search(head)
    if not match:
        return None
    label = match.group(1).decode('ascii', 'ignore')
    try:
        name = codecs.lookup(label).name
        # Odrzucamy kodowania niezgodne z ASCII (np. UTF-16), bo tagi w pliku są odczytywalne jako ASCII.
        if 'a'.encode(name) != b'a':
            return None
    except (LookupError, UnicodeError):
        return None
    # US-ASCII traktujemy jako UTF-8 (jego nadzbiór), aby można było potem wpisać polskie znaki.
    return 'utf-8' if name == 'ascii' else name

def _candidate_encodings(raw):
    """Kolejność prób dekodowania pliku."""
    if raw.startswith(codecs.BOM_UTF8):
        order = ['utf-8-sig', 'cp1250']
    else:
        declared = _declared_encoding(raw)
        if raw.isascii():
            # Czysty ASCII: każde z kodowań da ten sam tekst, więc zachowujemy zadeklarowane.
            order = [declared or 'utf-8']
        else:
            # Poprawny UTF-8 z polskimi znakami jest praktycznie nie do pomylenia z kodowaniem
            # 8-bitowym, więc ma pierwszeństwo także przed (nieaktualną) deklaracją w pliku.
            order = ['utf-8']
            if declared:
                order.append(declared)
            order.append('cp1250')
    return list(dict.fromkeys(order))

def read_text_file(path):
    """Odczytuje plik tekstowy, wykrywa pliki binarne, ustala kodowanie (BOM, deklaracja w pliku) i EOL."""
    raw = Path(path).read_bytes()
    if b'\x00' in raw[:8192]:
        raise ValueError("Plik wygląda na plik binarny (wykryto bajty NUL).")
    
    for enc in _candidate_encodings(raw):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Nie rozpoznano kodowania pliku (obsługiwane: UTF-8, Windows-1250 "
                         "oraz kodowanie zadeklarowane w pliku, np. ISO-8859-2).")
    
    crlf = text.count('\r\n')
    lf = text.count('\n') - crlf
    
    if crlf or lf:
        mode = (QsciScintilla.EolMode.EolWindows if crlf >= lf else QsciScintilla.EolMode.EolUnix)
        text = re.sub(r'\r\n|\r|\n', EOL[mode], text)
    else:
        mode = QsciScintilla.EolMode.EolWindows if os.name == 'nt' else QsciScintilla.EolMode.EolUnix
    
    return text, enc, mode

def _default_file_mode():
    """Uprawnienia nowego pliku zgodne z umask (np. 0o644) zamiast 0o600 nadawanego przez mkstemp."""
    current_umask = os.umask(0)
    os.umask(current_umask)
    return 0o666 & ~current_umask

def _write_in_place(target, content, encoding):
    """Zapis bezpośredni (nieatomowy). Używany awaryjnie, gdy w katalogu nie da się utworzyć pliku tymczasowego."""
    data = content.encode(encoding)  # ewentualny błąd kodowania wystąpi, zanim plik zostanie tknięty
    with open(target, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

def _atomic_save(file_path, content, encoding='utf-8'):
    """Bezpieczny, zablokowany przed kolizjami zapis pliku z zachowaniem uprawnień i fsync."""
    target = os.path.realpath(file_path)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target),
                                        prefix=".mkhtml_save_", suffix=".tmp")
    except OSError:
        # Brak prawa tworzenia plików w katalogu (np. katalog tylko do odczytu), ale sam
        # plik może być zapisywalny - wtedy zapisujemy go bezpośrednio.
        if os.path.isfile(target) and os.access(target, os.W_OK):
            _write_in_place(target, content, encoding)
            return
        raise

    try:
        try:
            f = os.fdopen(fd, 'w', encoding=encoding, newline='')
        except Exception:
            os.close(fd)
            raise

        with f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        if os.path.exists(target):
            shutil.copymode(target, tmp_path)
        else:
            # Nowy plik: mkstemp nadaje 0o600, więc ustawiamy uprawnienia zgodne z umask.
            try:
                os.chmod(tmp_path, _default_file_mode())
            except OSError:
                pass

        for attempt in range(5):
            try:
                os.replace(tmp_path, target)
                return
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1 * (attempt + 1))

    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise