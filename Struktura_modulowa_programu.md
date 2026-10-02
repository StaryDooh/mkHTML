# Dokumentacja struktury modułowej aplikacji mkHTML

Niniejszy dokument opisuje docelowy oraz zrealizowany podział monolitycznego kodu aplikacji **mkHTML** na odrębne, wyspecjalizowane moduły[cite: 2]. Architektura ta opiera się na wzorcu *Separation of Concerns* (rozdzielenie odpowiedzialności), co ułatwia testowanie, zwiększa czytelność kodu oraz umożliwia bezpieczną rozbudowę aplikacji o nowe funkcje[cite: 2].

## Struktura plików i odpowiedzialność modułów

### 1. `mkHTML.py` (Punkt wejścia aplikacji)
Główny skrypt uruchomieniowy. Jest to najkrótszy plik w projekcie, pozbawiony bezpośredniej logiki biznesowej i interfejsu[cite: 1, 2].
* **Zadania:**
  * Inicjalizacja obiektu `QApplication`[cite: 1, 2].
  * Konfiguracja globalnego przechwytywania wyjątków (`sys.excepthook`)[cite: 1, 2].
  * Utworzenie i wyświetlenie głównego okna programu (`MkHTMLEditor`)[cite: 1, 2].
  * Uruchomienie głównej pętli zdarzeń (`app.exec()`)[cite: 1, 2].

* **Zrobiono:**
  Główny moduł aplikacji `mkHTML.py` został całkowicie odchudzony i sprowadzony do pełnienia funkcji chudego punktu wejścia (*lean entry point*)[cite: 1].
  * **Inicjalizacja:** Tworzenie instancji `QApplication` i uruchomienie pętli zdarzeń[cite: 1, 2].
  * **Przechwytywanie błędów:** Rejestracja globalnego `sys.excepthook` rejestrującego awarie w pliku logów i wyświetlającego `QMessageBox`[cite: 1, 3].
  * **Odchudzenie:** Cała logika okna, edytora, menu oraz operacji dyskowych została przeniesiona do odpowiednich modułów[cite: 1, 3, 5, 6, 9].

### 2. `config.py` (Zarządzanie konfiguracją i logowaniem)
Moduł odpowiedzialny za środowisko, stałe aplikacji i zapis/odczyt ustawień użytkownika[cite: 2, 3].
* **Zadania:**
  * Definicja stałych ścieżek (plik konfiguracyjny `.mkhtml_config.json`, plik logów `.mkhtml.log`)[cite: 2, 3].
  * Przechowywanie stałej wersji aplikacji `APP_VERSION`[cite: 3].
  * Inicjalizacja systemu logowania[cite: 2, 3].
  * Funkcje `load_config()` i `save_config()` do odczytu i zapisu stanu okna, wybranego motywu oraz ostatniego katalogu roboczego[cite: 2, 3].

* **Zrobiono:**
  Moduł w pełni wyodrębniony jako centralne źródło prawdy dla konfiguracji[cite: 2, 3].
  * **Stałe aplikacji:** Zdefiniowano `APP_VERSION = "1.0.3.2"`, ścieżkę do pliku logów `LOG_FILE` oraz pliku konfiguracyjnego `CONFIG_FILE`[cite: 3].
  * **Obsługa ścieżek:** Funkcja `get_desktop_path()` do bezpiecznego pobierania domyślnego katalogu roboczego[cite: 3].
  * **Odczyt i zapis JSON:** Funkcje `load_config()` oraz `save_config()` do obsługi pozycji okna, wymiarów oraz wybranego motywu[cite: 3].

### 3. `themes.py` (Baza motywów wizualnych)
Moduł przechowujący definicje wyglądu edytora i całej aplikacji[cite: 2, 8].
* **Zadania:**
  * Przechowywanie słownika `THEMES` z paletami kolorów dla trybów (Jasny, Ciemny itp.)[cite: 2, 8].
  * Zawiera definicje stylów globalnych QSS dla komponentów[cite: 2, 8].
  * Mapowanie kolorów HTML/CSS dla lexerów Scintilla[cite: 2, 8].

* **Zrobiono:**
  Moduł pełni rolę centralnego magazynu konfiguracji wizualnej edytora. Przechowuje słownik `THEMES`, który całkowicie oddziela warstwę prezentacji od głównej logiki[cite: 2, 8].
  * **Globalny styl QSS:** Definicje wyglądów interfejsu PyQt6 (`app_qss`)[cite: 2, 8].
  * **Stylizacja obszaru edytora:** Ustawienia tła, tekstu, kursora, linii kursora oraz marginesów z numerami wierszy[cite: 2, 8].
  * **Kolorowanie składni (Lexery):** Słowniki barw dla elementów HTML (tagi, atrybuty, napisy, komentarze) oraz CSS (selektory, właściwości, wartości)[cite: 2, 8].

### 4. `file_utils.py` (Operacje wejścia/wyjścia)
"Robotnik dyskowy" (warstwa I/O), całkowicie uniezależniony od interfejsu graficznego[cite: 2, 5].
* **Zadania:**
  * Funkcja `read_text_file(path)`: odczyt plików, wykrywanie kodowania, weryfikacja bajtów NUL (pliki binarne), normalizacja znaków końca linii (EOL)[cite: 2, 5].
  * Funkcja `_atomic_save(...)`: bezpieczny zapis do pliku z wykorzystaniem plików tymczasowych i `os.fsync`, chroniący przed utratą danych[cite: 2, 5].

* **Zrobiono:**
  Moduł wyodrębniony jako niezależna warstwa I/O bez zależności od interfejsu użytkownika PyQt6[cite: 2, 5].
  * **Odczyt plików (`read_text_file`):** Wykrywanie plików binarnych (bajt NUL w pierwszych 8 KB), obsługa kodowania UTF-8 (z czyszczeniem BOM) oraz CP1250, detekcja i normalizacja znaków EOL (CRLF / LF)[cite: 2, 5].
  * **Bezpieczny zapis (`_atomic_save`):** Zapis atomowy przez pliki tymczasowe (`tempfile.mkstemp`), `os.fsync` wymuszający zrzut na dysk, zachowanie uprawnień (`shutil.copymode`) oraz pętla powtórzeń chroniąca przed blokadami plików w Windows (`PermissionError`)[cite: 2, 5].

### 5. `snippets.py` (Baza autouzupełniania)
Moduł z danymi statycznymi wspierającymi pisanie kodu[cite: 2, 7].
* **Zadania:**
  * Słownik `SNIPPETS` zawierający szablony kodu (np. szkielet HTML, Lorem Ipsum)[cite: 2, 7].
  * Zbiór `VOID_TAGS` (tagi samozamykające, np. `<br>`, `<img>`)[cite: 2, 7].
  * Zbiór `KNOWN_TAGS` do weryfikacji i autouzupełniania znaczników HTML[cite: 2, 7].

* **Zrobiono:**
  Moduł w pełni wyodrębniony jako pasywna baza danych dla edytora kodu[cite: 2, 7].
  * **Zbiory znaczników:** `VOID_TAGS` (tagi bez znaku zamykającego) oraz `KNOWN_TAGS` (lista dozwolonych znaczników HTML)[cite: 2, 7].
  * **Szablony kodu:** `SNIPPETS` oraz `LOREM_TEXT` przechowujące gotowe bloki tekstu wraz z offsetem pozycji kursora po wstawieniu (np. skróty `html`, `a`, `img`, `lorem`)[cite: 2, 7].

### 6. `editor.py` (Logika edytora tekstu)
Komponent wykonawczy dla obszaru edycji tekstu[cite: 2, 4].
* **Zadania:**
  * Klasa `MyCodeEditor` dziedzicząca po `QsciScintilla`[cite: 2, 4].
  * Konfiguracja zawijania wierszy i marginesów[cite: 2, 4].
  * Obsługa zdarzeń klawiatury (`keyPressEvent`): inteligentne zamykanie tagów, domykanie nawiasów `{`, cudzysłowów `"` i `'` oraz rozwijanie słów kluczowych klawiszem Tab[cite: 2, 4].

* **Zrobiono:**
  Wyodrębniono klasę edytora tekstu wraz ze słownikiem mapowania EOL[cite: 2, 4].
  * **Klasa `MyCodeEditor`:** Dziedziczenie po `QsciScintilla`, automatyczna konfiguracja końców linii zależna od systemu operacyjnego (Windows CRLF / Unix LF)[cite: 2, 4].
  * **Zaawansowana obsługa `keyPressEvent`:**
    * **Inteligentny Enter:** automatyczne rozbijanie i wcinanie tekstu między tagami (np. `<p>|</p>`)[cite: 2, 4].
    * **Rozwijanie skrótów klawiszem Tab:** pobieranie szablonów ze `snippets.py`, wstawianie z zachowaniem bieżącego wcięcia i pozycjonowaniem kursora[cite: 2, 4, 7].
    * **Auto-zamykanie tagów HTML:** tworzenie tagu zamykającego po wpisaniu `>` (z pominięciem `VOID_TAGS`)[cite: 2, 4, 7].
    * **Parowanie znaków:** automatyczne parowanie `{` w CSS, cudzysłowów `"` oraz apostrofów `'`[cite: 2, 4].

### 7. `ui_menu.py` (Budowa paska menu)
Moduł odpowiedzialny wyłącznie za kreację paska menu i akcji użytkownika[cite: 2, 9].
* **Zadania:**
  * Budowa struktury `QMenuBar` głównego okna[cite: 2, 9].
  * Tworzenie menu: Plik, Edycja, Motyw, Podgląd (F5) oraz Odwiedź[cite: 2, 9].
  * Podpinanie akcji pod odpowiednie metody klasy `MkHTMLEditor`[cite: 2, 9].

* **Zrobiono:**
  Pasek menu został wydzielony do osobnego pliku, co znacząco skróciło kod okna głównego[cite: 2, 9].
  * **Funkcja `create_menu(window)`:** Buduje kompletne menu aplikacji i podczepia akcje do przekazanej instancji okna[cite: 9].
  * **Dynamiczne menu motywów:** Iterowanie po słowniku `THEMES` z `themes.py` i tworzenie zaznaczalnych opcji wyboru motywu[cite: 8, 9].
  * **Pomocnicza funkcja `_add_action`:** Czytelna rejestracja akcji wraz ze skrótami klawiszowymi (Ctrl+N, Ctrl+O, Ctrl+S, F5 itp.)[cite: 9].

### 8. `main_window.py` (Główne okno aplikacji)
Moduł centralny, integrujący wszystkie komponenty i kontrolujący stan okna[cite: 2, 6].
* **Zadania:**
  * Klasa `MkHTMLEditor` dziedzicząca po `QMainWindow`[cite: 2, 6].
  * Zarządzanie zakładkami (`QTabWidget`), dodawanie, zamykanie i sprawdzanie stanu niezapisanych zmian[cite: 2, 6].
  * Przypisywanie i resetowanie lekserów (`QsciLexerHTML`, `QsciLexerCSS`) na podstawie rozszerzenia otwieranego pliku oraz wybranego motywu[cite: 2, 6].
  * Współpraca z modułem `file_utils.py` przy odczycie/zapisie plików i `config.py` przy zapisie stanu okna[cite: 2, 3, 5, 6].

* **Zrobiono:**
  Wyodrębniono klasę głównego okna aplikacji stanowiącą szkielet interfejsu użytkownika[cite: 2, 6].
  * **Zarządzanie zakładkami:** Dodawanie nowych kart (`add_new_tab`), monitorowanie modyfikacji tekstu (`*` w tytule), obsługa okna dialogowego zapisu przy zamykaniu zakładek (`maybe_save_tab`)[cite: 2, 6].
  * **Zarządzanie motywem i lexerami:** Metoda `update_lexer_for_editor()` nakładająca kolory z `themes.py` na lexery Scintilla HTML i CSS[cite: 2, 6, 8].
  * **Integracja I/O:** Wywoływanie funkcji `read_text_file` oraz `_atomic_save` z pliku `file_utils.py`[cite: 5, 6].
  * **Podgląd w przeglądarce:** Obsługa klawisza F5 i otwieranie aktywnego pliku HTML w domyślnej przeglądarce[cite: 6, 9].

---

## Korzyści z wdrożenia

1. **Czystszy kod i łatwa konserwacja:** Żaden plik nie przekracza kilkuset linii kodu, co ułatwia czytanie i nawigację[cite: 2].
2. **Izolacja odpowiedzialności:** Zmiany w wyglądzie menu (`ui_menu.py`) czy motywów (`themes.py`) nie naruszają logiki edytora (`editor.py`) ani operacji I/O (`file_utils.py`)[cite: 2, 4, 5, 8, 9].
3. **Brak kolizji importów:** Ściśle zdefiniowane zależności kierunkowe eliminują błędy importu cyklicznego (*circular import*).