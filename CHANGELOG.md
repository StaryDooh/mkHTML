# Changelog

Wszystkie znaczące zmiany w projekcie **mkHTML** będą dokumentowane w tym pliku.

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

---

## [0.0.2.0] - 2026-09-14

### Dodano
- **Obsługa zakładek (`QTabWidget`)**: Wprowadzono interfejs wielozakładkowy umożliwiający jednoczesną pracę nad wieloma plikami (np. `index.html` i `style.css`) w jednym oknie.
- **Wskaźnik niezapisanych zmian (`*`)**: Dodano wizualny wskaźnik edycji w tytule aktywnej zakładki oraz na pasku tytułu głównego okna.
- **Zarządzanie zamknięciem zakładek**: Możliwość zamykania poszczególnych zakładek przyciskiem `X` wraz z kontrolą niezapisanych zmian dla każdego pliku osobno.
- **Inteligentne otwieranie plików**: Jeśli aktualna zakładka jest czysta i pusta, otwarcie pliku wczytuje zawartość w bieżącą zakładkę zamiast tworzyć nową.

### Zmieniono
- Akcja menu **Plik -> Nowy** tworzy teraz nową zakładkę edytora.
- Zamknięcie programu sprawdza status modyfikacji we wszystkich otwartych zakładkach i kolejno pyta o zapis niezapisanych plików.

---

## [0.0.1.2] - 2026-09-10

### Dodano
- **Dynamiczne rozwijanie tagów (TAB)**: Wpisanie nazwy znacznikowej i naciśnięcie klawisza `TAB` generuje pełny tag (np. `section` -> `<section></section>`).
- **Obsługa tagów pojedynczych (void tags)**: Dedykowana obsługa znaczników samozamykających się (`<br>`, `<hr>`, `<img>`, `<input>`, `<meta>`, `<link>` itp.).
- **Szablony snippets**: Generowanie pełnej struktury nagłówkowej HTML5 po wpisaniu `html` + `TAB`.

### Zmieniono
- Ujednolicono wcięcia kodu na 4 spacje (z automatyczną konwersją podwójnych spacji).

---

## [0.0.1.0] - 2026-09-01

### Dodano
- Pierwsza wersja edytora oparta na **PyQt6** i **QScintilla**.
- Kolorowanie składni dla składni HTML (`QsciLexerHTML`) i CSS (`QsciLexerCSS`).
- Podstawowa obsługa plików (Nowy, Otwórz, Zapisz, Zapisz jako...).
- Szybkie uruchamianie podglądu strony w domyślnej przeglądarce pod klawiszem `F5`.
- Zapisywanie ostatnio używanego katalogu roboczego w pliku `.mkhtml_config.json`.
- Wykrywanie polskiej ścieżki Pulpitu w systemie Windows.