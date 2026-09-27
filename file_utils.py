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

def read_text_file(path):
    """Odczytuje plik tekstowy, wykrywa pliki binarne, czyści BOM i ustala EOL."""
    raw = Path(path).read_bytes()
    if b'\x00' in raw[:8192]:
        raise ValueError("Plik wygląda na plik binarny (wykryto bajty NUL).")
    
    order = ('utf-8-sig', 'cp1250') if raw.startswith(codecs.BOM_UTF8) else ('utf-8', 'cp1250')
    for enc in order:
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Nie rozpoznano kodowania pliku (obsługiwane: UTF-8 / Windows-1250).")
    
    crlf = text.count('\r\n')
    lf = text.count('\n') - crlf
    
    if crlf or lf:
        mode = (QsciScintilla.EolMode.EolWindows if crlf >= lf else QsciScintilla.EolMode.EolUnix)
        text = re.sub(r'\r\n|\r|\n', EOL[mode], text)
    else:
        mode = QsciScintilla.EolMode.EolWindows if os.name == 'nt' else QsciScintilla.EolMode.EolUnix
    
    return text, enc, mode

def _atomic_save(file_path, content, encoding='utf-8'):
    """Bezpieczny, zablokowany przed kolizjami zapis pliku z zachowaniem uprawnień i fsync."""
    target = os.path.realpath(file_path)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target),
                                    prefix=".mkhtml_save_", suffix=".tmp")
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