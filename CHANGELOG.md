# Changelog

Wszystkie znaczące zmiany w projekcie **mkHTML** będą dokumentowane w tym pliku.

---

## [1.0.2.5 - 1.0.3.1-dev] - 2026-09-27

### 🏗️ Architektura i refaktoryzacja (Major Refactoring)
* **Rozbicie monolitu:** Zakończono proces podziału głównego, rozbudowanego pliku `mkHTML.py` na mniejsze, niezależne moduły o pojedynczej odpowiedzialności. Ułatwi to dalszy rozwój, testowanie oraz utrzymanie kodu.
* **Nowy moduł `file_utils.py` (Warstwa I/O):**
  * Całkowite odseparowanie operacji dyskowych od interfejsu graficznego (PyQt6).
  * Wdrożenie w pełni atomowego zapisu plików (`_atomic_save`) z wykorzystaniem plików tymczasowych, fizycznego zrzutu z pamięci podręcznej na dysk (`os.fsync`) oraz mechanizmu ponowień (ochrona przed zjawiskiem zablokowanych plików w systemie Windows).
  * Usprawniony system odczytu (`read_text_file`) z wczesną detekcją plików binarnych (bajt NUL), czyszczeniem nagłówka BOM i automatyczną normalizacją znaków końca linii (CRLF/LF).
* **Nowy moduł `config.py` (oraz oddzielenie motywów):**
  * Logika zarządzania plikiem konfiguracyjnym JSON, ładowanie struktury motywów kolorystycznych oraz wykrywanie ścieżek systemowych (np. Pulpit) zostały wyodrębnione z rdzenia edytora.
* **Odchudzenie `mkHTML.py`:** Główny plik pełni teraz wyłącznie rolę integratora systemu i głównego kontrolera GUI (okna, menu, zarządzanie zdarzeniami edytora Scintilla). 

### 🔧 Poprawki i optymalizacje
* Usunięto zbędne biblioteki i importy z pliku głównego (m.in. `codecs`, `shutil`, `tempfile`), przenosząc je do dedykowanych modułów.

---

## [1.0.1.16 - 1.0.2.4]

### Dodane
- **Zamykanie znaczników w locie:** Wpisanie znaku `>` po otwarciu tagu HTML automatycznie generuje znacznik zamykający (z pominięciem tzw. *void tags* jak `<br>`, `<img>`, `<input>`).
- **Rozwijanie tagów klawiszem TAB:** Wpisanie nazwy dowolnego standardowego znacznika HTML (np. `div`, `span`, `p`) i wciśnięcie klawisza `TAB` natychmiast rozwija go do pełnej formy (np. `<div></div>`) i precyzyjnie ustawia kursor.
- **Wbudowane snippety:** Dodano szybkie skróty rozwijane klawiszem `TAB`:
  - `html` – generuje pełny szkielet dokumentu HTML5 z podpiętym arkuszem stylów.
  - `a` – generuje tag linku (`<a href=""></a>`).
  - `img` – generuje tag obrazka (`<img src="" alt="">`).
  - `lorem` – wstawia klasyczny tekst "Lorem ipsum...".
- **Inteligentne łamanie linii (Enter):** Wciśnięcie klawisza `Enter` dokładnie pomiędzy otwierającym a zamykającym tagiem (np. `<div>|</div>`) automatycznie przenosi kursor do nowej linii z zachowaniem prawidłowych wcięć.
- **Otaczanie zaznaczenia:** Zaznaczenie tekstu i wciśnięcie cudzysłowu (`"`, `'`) lub klamry (`{` w plikach CSS) automatycznie otacza wybrany tekst tymi znakami, zamiast go nadpisywać.

### Zmienione
- **Kontekstowe cudzysłowy i apostrofy:** Usprawniono logikę wpisywania cudzysłowów. Edytor "wychodzi" za zamykający cudzysłów bez jego dublowania i ignoruje wstawianie parzystych apostrofów wewnątrz wyrazów (zapobiega błędom przy słowach typu `don't`).
- **Optymalizacja Lexerów:** Doprecyzowano działanie mechanizmów autouzupełniania w zależności od aktywnego lexera (HTML vs CSS), co zapobiega uruchamianiu specyficznych skrótów HTML wewnątrz arkuszy stylów.
- Zaktualizowano globalne listy wspieranych znaczników (w tym *void tags*).

### Naprawione
- Rozwiązano problemy z nieoczekiwanym nadpisywaniem tekstu przy wciśnięciu `>` podczas aktywnego zaznaczenia.
- Usunięto błędy związane z błędnym przesuwaniem kursora przy szybkim wprowadzaniu znaków specjalnych.

---

## [1.0.1.15]

### Zmieniono
- Ustabilizowano działanie edytora po ostatnich zmianach w cyklu życia kart.
- Wycofano eksperymentalne zmiany w układzie okien, przywracając sprawdzoną obsługę konfiguracji bazowej.

---

## [1.0.1.14]

### Dodano
- Funkcję automatycznego parowania nawiasów klamrowych `{}` przy pracy z plikami CSS.
### Naprawiono
- Błąd powodujący nieprawidłowe domykanie tagów typu "void" (np. `<img>`, `<br>`).

---

## [1.0.1.13]

### Zmieniono
- Zoptymalizowano system wcięć (indentacji) przenoszący odpowiedni poziom marginesu przy przejściu do nowej linii.
### Naprawiono
- Problem z obcinaniem numeracji linii dla plików powyżej 9999 wierszy poprzez zastosowanie dynamicznej szerokości marginesu.

---

## [1.0.1.12]

### Dodano
- Możliwość otwierania wielu plików jednocześnie w oknie dialogowym (wykorzystanie `getOpenFileNames`).
- Standardowe skróty klawiszowe w menu głównym (m.in. `Ctrl+W`, `Ctrl+A`).
### Zmieniono
- Dodano mnemoniki (znaki `&`) w nazwach zakładek menu, poprawiając dostępność aplikacji z poziomu klawiatury.
- Zgrupowano akcje zmiany motywów w wykluczającą się grupę `QActionGroup`.

---

## [1.0.1.11]

### Dodano
- Obejmowanie zaznaczonego tekstu cudzysłowami (po wciśnięciu `"` na zaznaczonym fragmencie).
### Naprawiono
- Konflikt nazw zmiennych, w którym `self.font` nadpisywało natywną metodę `QWidget.font()`.

---

## [1.0.1.10]

### Dodano
- Sprawdzanie duplikatów w akcji "Zapisz jako", chroniące przed otwarciem tego samego pliku w dwóch osobnych kartach.
### Zmieniono
- Uporządkowano zarządzanie wersją aplikacji, przenosząc ją do jednej globalnej stałej `APP_VERSION`.

---

## [1.0.1.9]

### Dodano
- Zabezpieczenie przed uszkodzonym plikiem konfiguracyjnym JSON poprzez wymuszenie minimalnych rozmiarów okna (400x300).
- Rozszerzono automatyczne podpinanie leksera HTML dla dodatkowych formatów: `.svg`, `.xml` oraz `.php`.

---

## [1.0.1.8]

### Zmieniono
- Zachowanie klawiszy `Enter` i `Esc` w oknach dialogowych (przypisanie `setDefaultButton` oraz `setEscapeButton`), co czyni nawigację bardziej przewidywalną.
### Naprawiono
- Logikę wczytywania współrzędnych w układach wielomonitorowych, zapobiegając uciekaniu okna na ekran główny.
- Atomowy zapis plików konfiguracyjnych, zapobiegający ich wyzerowaniu w przypadku nagłego zamknięcia programu lub błędu systemu.
- Weryfikację typów w odczycie konfiguracji (zabezpieczenie przed rzutowaniem wartości `bool` na `int`).

---

## [1.0.1.7] - 2026-09-19

### Poprawki
- **Uszczelnienie wykrywania duplikatów:** Zmodyfikowano mechanizm identyfikacji już otwartych plików, wprowadzając weryfikację opartą na `os.path.samefile()`. Gwarantuje to pełną odporność na różnice w wielkości liter w ścieżkach (istotne w systemie Windows) oraz poprawne rozwiązywanie dowiązań symbolicznych.
- **Zabezpieczenie awaryjne (Fallback):** Dodano zapasową weryfikację przez `os.path.normcase(os.path.abspath())` na wypadek usunięcia otwartego pliku w tle.

## [1.0.1.6] - 2026-09-19

### Dodane
- **Zarządzanie zakładkami (Ochrona przed utratą danych):** Dodano mechanizm wykrywania plików już otwartych w edytorze (wykonywany jeszcze przed odczytem pliku z dysku). Przy próbie ponownego otwarcia tego samego pliku, aplikacja automatycznie przełącza widok na istniejącą zakładkę, zapobiegając utworzeniu duplikatu i potencjalnemu nadpisaniu niezapisanej pracy użytkownika.

## [1.0.1.5] - 2026-09-18

### Refaktoryzacja i czyszczenie kodu
- **Skróty klawiszowe (Tab):** Usunięto martwy, redundantny warunek filtrujący w logice rozwijania tagów.
- **Interfejs użytkownika:** Usunięto nieużywaną referencję do zmiennej `btn_discard` w oknie dialogowym pytającym o zapis zmian.
- **Menu główne:** Wprowadzono metodę pomocniczą `_add_action` do budowania menu w `create_menu()`, co zredukowało powtarzalny kod.

## [1.0.1.4] - 2026-09-18

### Poprawki
- **Zapis plików (`_atomic_save`):** Usunięto ryzykowny fallback otwierający plik docelowy bezpośrednio w trybie `'w'`. W przypadku błędu `OSError` aplikacja wykonuje ponowną próbę podmiany pliku `os.replace` po krótkim opóźnieniu (`time.sleep(0.1)`), eliminując ryzyko utraty danych przy chwilowej blokadzie przez program antywirusowy.

## [1.0.1.3] - 2026-09-17

### Poprawki
- **Edytor HTML:** Naprawiono problem polegający na ignorowaniu składni samozamykającej przez mechanizm automatycznego zamykania tagów[cite: 3]. Tagi kończące się jawnie znakiem `/>` (np. `<path d="M0 0" />` lub `<Component/>`) nie otrzymują już niepotrzebnego tagu zamykającego[cite: 3].

## [1.0.1.2] - 2026-09-17

### Poprawki
- **Zapis plików:** Wyeliminowano błąd podwójnego zamknięcia deskryptora pliku w funkcji bezpiecznego zapisu `_atomic_save`[cite: 3]. Rozdzielono moment otwarcia deskryptora od zapisu, co zapobiega wywoływaniu błędu `OSError: Bad file descriptor` w bloku obsługi wyjątków i maskowaniu właściwej przyczyny problemu z zapisem[cite: 3].

## [1.0.1.1] - 2026-09-17

### Poprawki
- **Skróty klawiszowe:** Rozwiązano krytyczny błąd rozwijania tagów za pomocą klawisza Tab, który wcześniej nie rozpoznawał kontekstu składniowego[cite: 3]. Dzięki sprawdzeniu stylu leksera w pozycji kursora wyeliminowano problem duplikowania zamykających tagów, zamieniania dowolnych tekstów/liczb na tagi wewnątrz atrybutów oraz niepoprawnego aktywowania mechanizmu w plikach niebędących kodem HTML[cite: 3].

## [1.0.1.0] - 2026-09-17

### Naprawiono
- **Błąd zapisu atomowego przy ścieżkach względnych (`EXDEV`):** Wymuszono konwersję ścieżki pliku na ścieżkę bezwzględną (`os.path.abspath`), co zapobiega błędom operacji `os.replace` przy zapisie plików otwartych z poziomu konsoli lub ścieżek względnych.
- **Wycieki pamięci obiektów Lexera:** Dodano jawne zwalnianie pamięci poprawnie odłączanych lexerów (`deleteLater()`) przy zmianie rozszerzenia pliku lub operacji *Zapisz jako*.
- **Cichą zmianę kodowania plików:** Wdrożono zapamiętywanie kodowania źródłowego (np. `cp1250`) podczas otwierania pliku i ponowne jego wykorzystanie przy zapisie na dysk.
- **Wycieki deskryptorów plików (File Descriptors):** Zabezpieczono tworzenie plików tymczasowych w `_atomic_save` blokiem `try...finally`, co gwarantuje zamknięcie i usunięcie deskryptora w przypadku awarii I/O.

### Zoptymalizowano
- **Płynność pisania w dużych plikach (UI Latency):** Zoptymalizowano metodę `keyPressEvent` — pełny tekst wiersza jest pobierany i analizowany tylko wtedy, gdy wciśnięty klawisz wyzwala regułę skrótu lub autouzupełniania.
- **Skanowanie tekstu kursorem:** Wyszukiwanie domknięć tagów HTML i reguł snippetów oparto na wąskim buforze tekstu (do 200 znaków wstecz od kursora) zamiast pełnej linii tekstu.
- **Redukcję operacji I/O:** Usunięto synchroniczny zapis pliku konfiguracyjnego `save_app_config()` przy otwieraniu i zapisywaniu plików. Konfiguracja jest teraz zapisywana wyłącznie raz, podczas zamykania aplikacji.
- **Kompilację Regex:** Przeniesiono kompilację wszystkich wyrażeń regularnych (`re.compile`) do konstruktora klasy `MyCodeEditor`.

### Udoskonalenia
- **Bezpieczeństwo pozycji okna:** Dodano mechanizm sprawdzania części wspólnej geometrii okna z dostępnymi ekranami (`intersected`). Okno automatycznie wyśrodkowuje się na głównym ekranie, jeśli poprzednie współrzędne znajdowały się na odłączonym monitorze.
- **Zarządzanie pamięcią RAM zakładek:** Wywołanie `deleteLater()` na zamkniętych zakładkach usuwa nieużywane instancje `QsciScintilla`.

## [1.0.0.1] - 2026-09-16

### Added
- Menu `Odwiedź...` na pasku menu zawierające odnośniki:
  - `Pobierz najnowszą wersję` -> `https://github.com/StaryDooh/mkHTML/releases`
  - `Zgłoś błąd` -> `https://github.com/StaryDooh/mkHTML/issues`
  - `Zrelaksuj się` -> `https://www.youtube.com/@StaryDooh`

### Changed
- Pozycja menu `Odwiedź...` została dodana na końcu paska nawigacji.

## [1.0.0.0] - 2026-09-15

### Added
- Pierwsza oficjalna wersja edytora **mkHTML**.
- System zakładek (tabów) umożliwiający pracę na wielu plikach jednocześnie.
- Kolorowanie składni dla plików HTML oraz CSS z wykorzystaniem biblioteki `QScintilla`.
- Automatyczne zamykanie tagów HTML, klamer CSS oraz cudzysłowów.
- Inteligentne auto-wcięcia oraz rozwijanie podstawowych szablonów kodu klawiszem `Tab`.
- Funkcja podglądu pliku w domyślnej przeglądarce internetowej pod klawiszem `F5`.
- Zapisywanie konfiguracji aplikacji (geometria okna, ostatnia ścieżka robocza) w pliku JSON profilu użytkownika.

## [0.0.2.2] - 2026-09-15

### Zmieniono
- Zastąpiono rozwijane menu `Uruchom -> Uruchom w przeglądarce` pojedynczym, wygodniejszym przyciskiem **Podgląd** umieszczonym bezpośrednio na głównym pasku menu.

### Naprawiono
- Naprawiono błąd polegający na znikaniu ikony programu na pasku tytułowym okna (ikona ładuje się teraz poprawnie z bezwzględnej ścieżki, niezależnie od otwieranego pliku czy pracy z plikiem z użyciem PyInstallera).

## [0.0.2.1] - 2026-09-14

### Dodano
- **Zapamiętywanie geometrii okna**: Położenie ($X, Y$) oraz rozmiar okna (szerokość i wysokość) są automatycznie zapisywane w pliku konfiguracyjnym `.mkhtml_config.json` przy zamykaniu aplikacji.
- **Przywracanie stanu okna**: Przy uruchomieniu program otwiera się w dokładnie tym samym miejscu i rozmiarze, w którym został zamknięty.

### Zmieniono
- Rozbudowano strukturę pliku konfiguracyjnego `~/.mkhtml_config.json` o parametry pozycji i wymiarów okna.

## [0.0.2.0] - 2026-09-14

### Dodano
- **Obsługa zakładek (`QTabWidget`)**: Wprowadzono interfejs wielozakładkowy umożliwiający jednoczesną pracę nad wieloma plikami (np. `index.html` i `style.css`) w jednym oknie.
- **Wskaźnik niezapisanych zmian (`*`)**: Dodano wizualny wskaźnik edycji w tytule aktywnej zakładki oraz na pasku tytułu głównego okna.
- **Zarządzanie zamknięciem zakładek**: Możliwość zamykania poszczególnych zakładek przyciskiem `X` wraz z kontrolą niezapisanych zmian dla każdego pliku osobno.
- **Inteligentne otwieranie plików**: Jeśli aktualna zakładka jest czysta i pusta, otwarcie pliku wczytuje zawartość w bieżącą zakładkę zamiast tworzyć nową.

### Zmieniono
- Akcja menu **Plik -> Nowy** tworzy teraz nową zakładkę edytora.
- Zamknięcie programu sprawdza status modyfikacji we wszystkich otwartych zakładkach i kolejno pyta o zapis niezapisanych plików.

## [0.0.1.2] - 2026-09-10

### Dodano
- **Dynamiczne rozwijanie tagów (TAB)**: Wpisanie nazwy znacznikowej i naciśnięcie klawisza `TAB` generuje pełny tag (np. `section` -> `<section></section>`).
- **Obsługa tagów pojedynczych (void tags)**: Dedykowana obsługa znaczników samozamykających się (`<br>`, `<hr>`, `<img>`, `<input>`, `<meta>`, `<link>` itp.).
- **Szablony snippets**: Generowanie pełnej struktury nagłówkowej HTML5 po wpisaniu `html` + `TAB`.

### Zmieniono
- Ujednolicono wcięcia kodu na 4 spacje (z automatyczną konwersją podwójnych spacji).

## [0.0.1.0] - 2026-09-01

### Dodano
- Pierwsza wersja edytora oparta na **PyQt6** i **QScintilla**.
- Kolorowanie składni dla składni HTML (`QsciLexerHTML`) i CSS (`QsciLexerCSS`).
- Podstawowa obsługa plików (Nowy, Otwórz, Zapisz, Zapisz jako...).
- Szybkie uruchamianie podglądu strony w domyślnej przeglądarce pod klawiszem `F5`.
- Zapisywanie ostatnio używanego katalogu roboczego w pliku `.mkhtml_config.json`.
- Wykrywanie polskiej ścieżki Pulpitu w systemie Windows.