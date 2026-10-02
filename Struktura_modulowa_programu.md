# Dokumentacja struktury modułowej aplikacji mkHTML

Niniejszy dokument opisuje podział aplikacji **mkHTML** na odrębne, wyspecjalizowane moduły. Architektura opiera się na wzorcu *Separation of Concerns* (rozdzielenie odpowiedzialności), co ułatwia testowanie, zwiększa czytelność kodu oraz umożliwia bezpieczną rozbudowę aplikacji o nowe funkcje.

## Mapa zależności modułów

Strzałka oznacza „importuje”. Zależności mają jeden kierunek, więc nie występuje import cykliczny.

```
mkHTML.py ──► config.py ──► themes.py
    │
    └──────► main_window.py ──► config.py
                   │      ├──► file_utils.py
                   │      ├──► editor.py ──► snippets.py
                   │      ├──► ui_menu.py ──► themes.py
                   │      └──► themes.py
```

## Struktura plików i odpowiedzialność modułów

### 1. `mkHTML.py` (Punkt wejścia aplikacji)
Główny skrypt uruchomieniowy. Jest to najkrótszy plik w projekcie, pozbawiony logiki biznesowej i interfejsu.
* **Zadania:**
  * Inicjalizacja obiektu `QApplication`.
  * Rejestracja globalnego przechwytywania wyjątków (`sys.excepthook`).
  * Utworzenie i wyświetlenie głównego okna programu (`MkHTMLEditor`).
  * Uruchomienie głównej pętli zdarzeń (`app.exec()`).

* **Zrobiono:**
  Moduł sprowadzono do roli chudego punktu wejścia (*lean entry point*).
  * **Inicjalizacja:** Tworzenie instancji `QApplication` i uruchomienie pętli zdarzeń.
  * **Przechwytywanie błędów:** Funkcja `_excepthook` jest jedynym miejscem obsługi nieobsłużonych wyjątków: zapisuje błąd w pliku logów i wyświetla `QMessageBox`.
  * **Logowanie:** Plik nie konfiguruje logowania samodzielnie. Konfiguracja następuje przy imporcie `config.py`, skąd pobierana jest także ścieżka `LOG_FILE`.
  * **Odchudzenie:** Cała logika okna, edytora, menu oraz operacji dyskowych znajduje się w pozostałych modułach.

### 2. `config.py` (Zarządzanie konfiguracją i logowaniem)
Moduł odpowiedzialny za środowisko, stałe aplikacji i zapis/odczyt ustawień użytkownika.
* **Zadania:**
  * Definicja stałych ścieżek (plik konfiguracyjny `.mkhtml_config.json`, plik logów `.mkhtml.log`).
  * Przechowywanie numeru wersji aplikacji (`APP_VERSION`) oraz minimalnych wymiarów okna.
  * Jednorazowa inicjalizacja systemu logowania.
  * Funkcje `load_config()` i `save_config()` do odczytu i zapisu stanu okna, wybranego motywu oraz ostatniego katalogu roboczego.

* **Zrobiono:**
  Moduł jest centralnym źródłem prawdy dla konfiguracji.
  * **Stałe aplikacji:** `APP_VERSION`, `MIN_WINDOW_WIDTH` (400), `MIN_WINDOW_HEIGHT` (300), `LOG_FILE` oraz `CONFIG_FILE`. Numer wersji jest zdefiniowany wyłącznie w tym miejscu.
  * **Logowanie:** Konfiguracja `logging.basicConfig` (plik w katalogu domowym, poziom `ERROR`, z awaryjnym przejściem na logowanie bez pliku).
  * **Obsługa ścieżek:** `get_desktop_path()` zwraca bezpieczny, domyślny katalog roboczy.
  * **Odczyt i zapis JSON:** `load_config()` oraz `save_config()` obsługują położenie okna, jego wymiary, stan *zmaksymalizowane* (`maximized`), motyw oraz katalog roboczy.
  * **Walidacja konfiguracji:** Pola `x`, `y`, `width`, `height` muszą być liczbami całkowitymi (wartości logiczne są odrzucane). Położenie może być ujemne, co umożliwia zapamiętanie okna na monitorze położonym na lewo lub powyżej monitora głównego. Szerokość i wysokość mniejsze od minimum wracają do wartości domyślnych. Pole `maximized` musi być wartością logiczną, w przeciwnym razie przyjmowane jest `False`. Nieznany motyw zamieniany jest na `jasny`. Widoczność okna na dostępnych ekranach sprawdza `main_window.py`.
  * **Zgodność wsteczna:** Stare pliki konfiguracji bez pola `maximized` są wczytywane bez błędu.

### 3. `themes.py` (Baza motywów wizualnych)
Moduł przechowujący komplet definicji wyglądu edytora i całej aplikacji. Wszystkie kolory wpisywane są w jednym miejscu, osobno dla każdego motywu.
* **Zadania:**
  * Przechowywanie słownika `THEMES` z paletami kolorów (Jasny, Ciemny, Polarny).
  * Opis kolorów interfejsu okna w słowniku `"ui"` każdego motywu.
  * Generowanie arkusza stylów QSS okna na podstawie tego słownika.
  * Mapowanie kolorów HTML/CSS dla lexerów Scintilla.

* **Zrobiono:**
  Moduł jest centralnym magazynem konfiguracji wizualnej i całkowicie oddziela warstwę prezentacji od logiki aplikacji.
  * **Motywy:** `jasny` (domyślny przy pierwszym uruchomieniu), `ciemny` oraz `polarny` (chłodna, przygaszona paleta wzorowana na Nord). Dodanie kolejnego motywu wymaga tylko nowego bloku w słowniku `THEMES`. Pozycja w menu „Motyw” pojawia się automatycznie.
  * **Kolory edytora:** Tło, tekst, kursor, linia kursora, zaznaczenie oraz marginesy z numerami wierszy (klucze `bg`, `fg`, `caret`, `caret_line`, `selection_*`, `margin_*`).
  * **Kolorowanie składni (lexery):** Słowniki `html` (tagi, atrybuty, napisy, encje, komentarze) oraz `css` (selektory, właściwości, wartości, napisy, pseudoklasy, komentarze).
  * **Kolory interfejsu okna (`"ui"`):** Tło i tekst okna, paska menu i menu rozwijanego (w tym zaznaczenie, pozycje wyłączone, separator i znacznik wybranego motywu), zakładek (zwykłych i zaznaczonej) oraz przycisku zamykania zakładki (karta aktywna, nieaktywna, najechanie myszą).
  * **Generowanie QSS:** Funkcja `build_app_qss(ui)` buduje arkusz stylów ze słownika `"ui"`. Wynik zapisywany jest w kluczu `app_qss` każdego motywu, który odczytuje `main_window.py`. Dzięki temu wszystkie motywy mają identyczny zestaw reguł, a wygląd okna (łącznie z motywem jasnym) nie zależy od ustawień systemu, np. trybu ciemnego.
  * **Kontrola kompletności:** Krotka `UI_KEYS` określa wymagane kolory interfejsu. Brak któregokolwiek w nowym motywie zgłaszany jest od razu przy starcie programu.
  * **Powiązanie z oknem:** Przycisk zamykania zakładki stylowany jest regułami dla `QToolButton#tabClose`. Nazwa obiektu `tabClose` występuje także w `main_window.py` i musi być zmieniana w obu miejscach jednocześnie.

### 4. `file_utils.py` (Operacje wejścia/wyjścia)
„Robotnik dyskowy” (warstwa I/O), niezawierający logiki interfejsu graficznego.
* **Zadania:**
  * Funkcja `read_text_file(path)`: odczyt plików, wykrywanie kodowania, weryfikacja bajtów NUL (pliki binarne), normalizacja znaków końca linii (EOL).
  * Funkcja `_atomic_save(...)`: bezpieczny zapis do pliku z wykorzystaniem plików tymczasowych i `os.fsync`, chroniący przed utratą danych.

* **Zrobiono:**
  Moduł wyodrębniony jako warstwa I/O, niewykorzystująca widgetów ani okien PyQt6. Jedyną zależnością od biblioteki QScintilla jest import `QsciScintilla`, potrzebny do zwrócenia trybu EOL (`EolMode`) oraz zdefiniowania słownika mapowania EOL.
  * **Odczyt plików (`read_text_file`):** Wykrywanie plików binarnych (bajt NUL w pierwszych 8 KB), obsługa kodowania UTF-8 (z obsługą BOM) oraz CP1250, detekcja i normalizacja znaków EOL (CRLF / LF).
  * **Bezpieczny zapis (`_atomic_save`):** Zapis atomowy przez pliki tymczasowe (`tempfile.mkstemp`), `os.fsync` wymuszający zrzut na dysk, zachowanie uprawnień istniejącego pliku (`shutil.copymode`) oraz pętla powtórzeń chroniąca przed blokadami plików w Windows (`PermissionError`).

### 5. `snippets.py` (Baza autouzupełniania)
Moduł z danymi statycznymi wspierającymi pisanie kodu.
* **Zadania:**
  * Słownik `SNIPPETS` zawierający szablony kodu (np. szkielet HTML, Lorem Ipsum).
  * Zbiór `VOID_TAGS` (tagi samozamykające, np. `<br>`, `<img>`).
  * Zbiór `KNOWN_TAGS` do weryfikacji i autouzupełniania znaczników HTML.

* **Zrobiono:**
  Moduł jest pasywną bazą danych dla edytora kodu.
  * **Zbiory znaczników:** `VOID_TAGS` (tagi bez znacznika zamykającego) oraz `KNOWN_TAGS` (lista rozpoznawanych znaczników HTML).
  * **Szablony kodu:** `SNIPPETS` oraz `LOREM_TEXT` przechowują gotowe bloki tekstu wraz z offsetem pozycji kursora po wstawieniu (skróty `html`, `a`, `img`, `lorem`).

### 6. `editor.py` (Logika edytora tekstu)
Komponent wykonawczy dla obszaru edycji tekstu.
* **Zadania:**
  * Klasa `MyCodeEditor` dziedzicząca po `QsciScintilla`.
  * Konfiguracja zawijania wierszy.
  * Obsługa zdarzeń klawiatury (`keyPressEvent`): inteligentne zamykanie tagów, domykanie nawiasów `{`, cudzysłowów `"` i `'` oraz rozwijanie skrótów klawiszem Tab.

* **Zrobiono:**
  Wyodrębniono klasę edytora tekstu wraz ze słownikiem mapowania EOL.
  * **Klasa `MyCodeEditor`:** Dziedziczenie po `QsciScintilla`, automatyczna konfiguracja końców linii zależna od systemu operacyjnego (Windows CRLF / Unix LF), zawijanie wierszy ze wskaźnikami i wcięciem.
  * **Obsługa `keyPressEvent`:**
    * **Inteligentny Enter:** automatyczne rozbijanie i wcinanie tekstu między tagami (np. `<p>|</p>`).
    * **Rozwijanie skrótów klawiszem Tab:** pobieranie szablonów ze `snippets.py`, wstawianie z zachowaniem bieżącego wcięcia i pozycjonowaniem kursora.
    * **Auto-zamykanie tagów HTML:** tworzenie znacznika zamykającego po wpisaniu `>` (z pominięciem `VOID_TAGS`).
    * **Parowanie znaków:** automatyczne parowanie `{` w CSS, cudzysłowów `"` oraz apostrofów `'`.

### 7. `ui_menu.py` (Budowa paska menu)
Moduł odpowiedzialny wyłącznie za kreację paska menu i akcji użytkownika. Nie zawiera żadnych kolorów, wygląd menu zależy od aktywnego motywu.
* **Zadania:**
  * Budowa struktury `QMenuBar` głównego okna.
  * Tworzenie menu: Plik, Edycja, Motyw, Podgląd (F5) oraz Odwiedź.
  * Podpinanie akcji pod odpowiednie metody klasy `MkHTMLEditor`.

* **Zrobiono:**
  Pasek menu został wydzielony do osobnego pliku, co skróciło kod okna głównego.
  * **Funkcja `create_menu(window)`:** Buduje kompletne menu aplikacji i podczepia akcje do przekazanej instancji okna.
  * **Dynamiczne menu motywów:** Iterowanie po słowniku `THEMES` z `themes.py` i tworzenie zaznaczalnych opcji wyboru motywu. Nowy motyw pojawia się w menu bez zmian w tym pliku.
  * **Pomocnicza funkcja `_add_action`:** Czytelna rejestracja akcji wraz ze skrótami klawiszowymi (Ctrl+N, Ctrl+O, Ctrl+S, F5 itp.).

### 8. `main_window.py` (Główne okno aplikacji)
Moduł centralny, integrujący wszystkie komponenty i kontrolujący stan okna.
* **Zadania:**
  * Klasa `MkHTMLEditor` dziedzicząca po `QMainWindow`.
  * Zarządzanie zakładkami (`QTabWidget`), dodawanie, zamykanie i sprawdzanie stanu niezapisanych zmian.
  * Przypisywanie i resetowanie lekserów (`QsciLexerHTML`, `QsciLexerCSS`) na podstawie rozszerzenia otwieranego pliku oraz wybranego motywu.
  * Stosowanie arkusza stylów okna (`app_qss`) wybranego motywu.
  * Zapamiętywanie i przywracanie położenia, rozmiaru i stanu okna.
  * Współpraca z modułem `file_utils.py` przy odczycie/zapisie plików i `config.py` przy zapisie stanu okna.

* **Zrobiono:**
  Wyodrębniono klasę głównego okna aplikacji stanowiącą szkielet interfejsu użytkownika.
  * **Zarządzanie zakładkami:** Dodawanie nowych kart (`add_new_tab`), monitorowanie modyfikacji tekstu (`*` w tytule), obsługa okna dialogowego zapisu przy zamykaniu zakładek (`maybe_save_tab`).
  * **Przyciski zamykania kart:** Zakładki nie używają wbudowanego przycisku Qt. Każda karta ma własny przycisk `QToolButton` (`_install_close_button`) o nazwie obiektu `tabClose`. Metoda `refresh_close_buttons()` oznacza przycisk karty aktywnej właściwością `active=true`, dzięki czemu motyw może nadać „×” inny kolor na karcie aktywnej niż na nieaktywnych. Przycisk wywołuje to samo `close_tab`, więc pytanie o zapis działa jak dotychczas.
  * **Zarządzanie motywem i lexerami:** Metoda `update_lexer_for_editor()` nakładająca kolory z `themes.py` na lexery Scintilla HTML i CSS. Zmiana motywu (`set_theme`) podstawia nowy arkusz `app_qss` całemu oknu, odświeża lexery wszystkich kart i zapisuje konfigurację.
  * **Czcionka edytora:** Przechowywana w atrybucie `editor_font` (nazwa nie koliduje z metodą `QWidget.font()`).
  * **Stan okna:** Zapis używa `normalGeometry()`, czyli rozmiaru okna w stanie normalnym, także gdy okno jest zmaksymalizowane lub zminimalizowane, oraz flagi `isMaximized()`. Przy starcie przywracana jest zapamiętana geometria (z kontrolą widoczności na dostępnych ekranach), a następnie, jeśli trzeba, stan zmaksymalizowany. Po wyjściu z maksymalizacji okno wraca do zapamiętanego rozmiaru.
  * **Integracja I/O:** Wywoływanie funkcji `read_text_file` oraz `_atomic_save` z pliku `file_utils.py`.
  * **Podgląd w przeglądarce:** Obsługa klawisza F5 i otwieranie aktywnego pliku HTML w domyślnej przeglądarce.

---

## Korzyści z wdrożenia

1. **Czystszy kod i łatwa konserwacja:** Żaden plik nie przekracza kilkuset linii kodu, co ułatwia czytanie i nawigację.
2. **Izolacja odpowiedzialności:** Zmiany w wyglądzie aplikacji (kolory, menu, zakładki) wykonuje się wyłącznie w `themes.py`. Nie naruszają one logiki edytora (`editor.py`) ani operacji I/O (`file_utils.py`).
3. **Jedno źródło prawdy:** Numer wersji i ustawienia użytkownika znajdują się w `config.py`, a kolory w `themes.py`. Logowanie konfigurowane jest w jednym miejscu, a obsługa nieobsłużonych wyjątków w `mkHTML.py`.
4. **Brak kolizji importów:** Ściśle zdefiniowane zależności kierunkowe (patrz mapa zależności) eliminują błędy importu cyklicznego (*circular import*).