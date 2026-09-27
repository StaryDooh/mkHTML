# Dokumentacja struktury modułowej aplikacji mkHTML

Niniejszy dokument opisuje docelowy podział monolitycznego kodu aplikacji **mkHTML** na odrębne, wyspecjalizowane moduły. Architektura ta opiera się na wzorcu *Separation of Concerns* (rozdzielenie odpowiedzialności), co ma na celu ułatwienie testowania, czytelność kodu oraz bezpieczną rozbudowę aplikacji o nowe funkcje.

## Struktura plików i odpowiedzialność modułów

### 1. `mkHTML.py` (Punkt wejścia aplikacji)
Główny skrypt uruchomieniowy. Jest to najkrótszy plik w projekcie, pozbawiony logiki biznesowej.
* **Zadania:**
  * Inicjalizacja obiektu `QApplication`.
  * Konfiguracja globalnego przechwytywania wyjątków (`sys.excepthook`).
  * Utworzenie i wyświetlenie głównego okna programu.
  * Uruchomienie głównej pętli zdarzeń (`app.exec()`).

* **Zrobiono:**

  Główny moduł aplikacji `mkHTML.py` został odchudzony o logikę obsługi konfiguracji, kolorystyki oraz operacji wejścia/wyjścia (I/O). Pełni funkcję integratora systemu, spijającego wyodrębnione moduły (`config`, `file_utils`, `themes`) z interfejsem użytkownika[cite: 1].

  * **Logika Edytora (`MyCodeEditor`):**
    * Dziedziczenie po `QsciScintilla` i dostosowanie ustawień zawijania wierszy oraz marginesów.
    * Zaawansowana obsługa zdarzeń klawiatury (`keyPressEvent`):
      * **Inteligentny Enter:** automatyczne rozbijanie i wcinanie tekstu między tagami (np. `<p>|</p>` + Enter).
      * **Autouzupełnianie z klawiszem Tab:** dynamiczne rozwijanie tagów HTML, wstawianie struktur dla `html`, `a`, `img` oraz tekstu `lorem`.
      * **Automatyczne parowanie znaków:** domykanie klamer `{` (z automatycznym wcięciem w CSS), cudzysłowów `"` oraz apostrofów `'`.
      * **Zamykanie znaczników HTML:** automatyczne generowanie tagów zamykających (np. `</tag>`) po wpisaniu znaku `>` z pomijaniem tagów samozamykających (`void_tags`).

  * **Okno Główne i Interfejs (`MkHTMLEditor`):**
    * Obsługa wielu dokumentów w zakładkach (`QTabWidget`) z sygnalizacją niezapisanych zmian (`*`).
    * Dynamiczne nakładanie kolorystyki i lekserów (`QsciLexerHTML`, `QsciLexerCSS`) na podstawie słowników z modułu `themes.py`.
    * Zarządzanie cyklem życia pliku – wywoływanie bezpiecznego odczytu i zapisu (`read_text_file`, `_atomic_save`) z modułu `file_utils.py`.
    * Tworzenie paska menu (Plik, Edycja, Motyw, Podgląd F5, Odwiedź...) oraz integracja z przeglądarką internetową.

  * **Inicjalizacja i Bezpieczeństwo:**
    * Wczytywanie ustawień okna i ostatniego motywu przy użyciu `load_config()` i `save_config()`.
    * Przechwytywanie nieobsłużonych błędów poprzez `sys.excepthook = _excepthook` z prezentacją problemu w oknie dialogowym `QMessageBox`.

### 2. `config.py` (Zarządzanie konfiguracją i logowaniem)
Moduł odpowiedzialny za środowisko i ustawienia aplikacji.
* **Zadania:**
  * Definicja stałych ścieżek (np. plik konfiguracyjny `.mkhtml_config.json`, plik logów `.mkhtml.log`).
  * Inicjalizacja systemu logowania (wraz z zabezpieczeniem typu *fallback* w przypadku błędu zapisu na dysku).
  * Funkcje `load_config()` i `save_config()` do odczytu i zapisu stanu okna, wybranego motywu oraz ostatniego katalogu roboczego.

* **Zrobiono:**

  Moduł `config.py` wyodrębniony z pliku `mkHTML_4.py` koncentruje się na konfiguracji środowiska, logowaniu oraz zarządzaniu plikami ustawień. Kod zawiera również niezbędne importy, które pozwolą mu działać niezależnie.

  * **Ścieżki i logi:** Moduł inicjalizuje system logowania i definiuje ścieżki do plików `.mkhtml_config.json` oraz `.mkhtml.log` w katalogu domowym użytkownika.

  * **Obsługa błędów:** Zawiera funkcję `_excepthook`, która przechwytuje nieobsłużone wyjątki i wyświetla je za pomocą okna `QMessageBox` z modułu `PyQt6.QtWidgets`.
  
  * **Odczyt i zapis ustawień:** Posiada funkcje `load_config` i `save_config`, które parsują plik JSON i ustalają m.in. początkową pozycję okna, domyślny motyw oraz ścieżkę do pulpitu przy użyciu `QStandardPaths`.   

### 3. `themes.py` (Baza motywów wizualnych)
Moduł przechowujący definicje wyglądu edytora i całej aplikacji.
* **Zadania:**
  * Przechowywanie słownika `THEMES` z paletami kolorów dla trybów: Jasny, Ciemny, Rzutnik, Dracula, itp.
  * Zawiera definicje stylów globalnych QSS dla komponentów (pasek menu, zakładki, okna dialogowe).
  * Opcjonalnie: funkcje pomocnicze do mapowania kolorów HEX na obiekty `QColor`.

* **Zrobiono:**

  Moduł pełni rolę centralnego magazynu konfiguracji wizualnej edytora. Przechowuje słownik `THEMES`, który całkowicie oddziela warstwę prezentacji i wyglądu od głównej logiki aplikacji (`mkHTML.py`). Dzięki takiej architekturze dodawanie nowych schematów kolorystycznych nie wymaga ingerencji w główny kod edytora.

  Każdy motyw zdefiniowany w słowniku `THEMES` (np. `"jasny"`, `"ciemny"`) zarządza trzema głównymi obszarami interfejsu:

  * **Globalny styl interfejsu (QSS):** Definiuje wygląd głównych komponentów okna (np. tło aplikacji, styl zakładek, przyciski) poprzez klucz `app_qss` obsługiwany przez framework PyQt6.
  * **Kolorystyka obszaru roboczego (QsciScintilla):** Określa bazowe właściwości edytora tekstu, w tym: tło (`bg`), kolor czcionki (`fg`), kursor i jego linia (`caret`, `caret_line`), wygląd zaznaczonego tekstu (`selection_bg`, `selection_fg`) oraz margines z numeracją linii (`margin_bg`, `margin_fg`).
  * **Podświetlanie składni (Lexery):** Zawiera dedykowane, zagnieżdżone słowniki mapujące kody szesnastkowe (HEX) na poszczególne elementy struktury kodu:
    * **`html`** – kolorowanie tagów, atrybutów, ciągów znaków (wartości), encji oraz komentarzy.
    * **`css`** – rozróżnianie i kolorowanie selektorów (tagi, klasy, ID), właściwości, wartości, pseudoklas oraz komentarzy.

#### Przykład struktury pojedynczego motywu:

```python
"nazwa_kodowa": {
    "name": "Wyświetlana nazwa w menu",
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
}
```
### 4. `file_utils.py` (Operacje wejścia/wyjścia)
"Robotnik" dyskowy, całkowicie uniezależniony od interfejsu graficznego.
* **Zadania:**
  * Funkcja `read_text_file(path)`: odczyt plików, wykrywanie kodowania, weryfikacja bajtów NUL (pliki binarne), normalizacja znaków końca linii (EOL).
  * Funkcja `_atomic_save(...)`: bezpieczny zapis do pliku z wykorzystaniem plików tymczasowych i `os.fsync`, chroniący przed utratą danych w razie awarii.

* **Zrobiono:**

  Moduł `file_utils.py` został w pełni wyodrębniony jako niezależny "robotnik dyskowy" (warstwa I/O)[cite: 6]. Został całkowicie odseparowany od interfejsu graficznego PyQt6, dzięki czemu nie posiada żadnych zależności od klas GUI i może być łatwo testowany osobno[cite: 6].

  * **Odczyt plików (`read_text_file`):**
    * Weryfikacja obecności bajtów NUL w pierwszych 8 KB pliku w celu natychmiastowego wykluczenia plików binarnych[cite: 5, 6].
    * Automatyczne czyszczenie nagłówka UTF-8 BOM (`utf-8-sig`) oraz obsługa zestawów znaków `utf-8` i `cp1250`[cite: 5, 6].
    * Wykrywanie oraz automatyczna normalizacja znaków końca linii (EOL: Windows CRLF / Unix LF)[cite: 5, 6].

  * **Bezpieczny zapis (`_atomic_save`):**
    * Zapis atomowy z wykorzystaniem plików tymczasowych (`tempfile.mkstemp`), chroniący plik przed uszkodzeniem lub wyczyszczeniem w razie awarii zasilania bądź błędu aplikacji podczas zapisu[cite: 5, 6].
    * Zapewnienie fizycznego zrzutu danych z pamięci podręcznej na dysk za pomocą `f.flush()` oraz `os.fsync()`[cite: 5, 6].
    * Zachowanie uprawnień i trybu dostępu oryginalnego pliku (`shutil.copymode`)[cite: 5, 6].
    * Pętla powtórzeń z opóźnieniem przy podmienianiu pliku (`os.replace`) chroniąca przed kolizjami blokad plików w systemie Windows (`PermissionError`)[cite: 5, 6].

### 5. `snippets.py` (Baza autouzupełniania)
Moduł z danymi statycznymi, wykorzystywanymi przez edytor do wspomagania pisania kodu.
* **Zadania:**
  * Słownik `snippets` zawierający szablony kodu (np. szkielet HTML, Lorem Ipsum).
  * Zbiór `void_tags` (tagi samozamykające, np. `<br>`, `<img>`).
  * (Przyszłość) Logika wczytywania własnych snippetów zdefiniowanych przez użytkownika.

### 6. `editor.py` (Logika edytora tekstu)
Serce aplikacji w kontekście edycji kodu.
* **Zadania:**
  * Klasa `MyCodeEditor` dziedzicząca po `QsciScintilla`.
  * Konfiguracja podstawowa Scintilli (zawijanie wierszy, marginesy).
  * Obsługa zdarzeń klawiatury (`keyPressEvent`): inteligentne zamykanie tagów, domykanie nawiasów `{`, cudzysłowów `"` i `'` oraz rozwijanie słów kluczowych klawiszem Tab.
  * Korzysta bezpośrednio z modułu `snippets.py`.

### 7. `ui_menu.py` (Budowa paska menu)
Moduł pomocniczy do odciążenia głównej klasy okna, odpowiedzialny wyłącznie za kreację UI.
* **Zadania:**
  * Funkcje lub klasa do budowania obiektu `QMenuBar`.
  * Podpinanie akcji (Nowy, Otwórz, Zapisz, Cofnij, Podgląd F5) oraz skrótów klawiaturowych pod odpowiednie metody głównego okna.
  * Dynamiczne budowanie menu "Motyw" na podstawie kluczy z modułu `themes.py`.

### 8. `main_window.py` (Główne okno aplikacji)
Moduł centralny, integrujący wszystkie pozostałe komponenty.
* **Zadania:**
  * Klasa `MkHTMLEditor` dziedzicząca po `QMainWindow`.
  * Zarządzanie zakładkami (`QTabWidget`), otwieranie, zamykanie i przełączanie aktywnych kart.
  * Przypisywanie odpowiednich lekserów (HTML/CSS) w zależności od rozszerzenia otwieranego pliku (metoda `update_lexer_for_editor`).
  * Okna dialogowe z ostrzeżeniami (np. niezapisane zmiany).
  * Współpraca z modułem `file_utils.py` przy operacjach wywoływanych przez użytkownika.

---

## Korzyści z wdrożenia

1. **Izolacja błędów:** Błąd w systemie zapisu plików (`file_utils.py`) nie wpłynie na rysowanie interfejsu (`main_window.py`).
2. **Łatwiejsze wprowadzanie funkcji:** Dodanie nowej funkcji edytora (np. komentowanie skrótem klawiszowym) wymaga edycji tylko jednego, zwięzłego pliku `editor.py`.
3. **Zwiększona czytelność:** Żaden pojedynczy plik nie powinien przekroczyć 300-400 linii kodu, co znacząco ułatwi jego analizę i pielęgnację.
