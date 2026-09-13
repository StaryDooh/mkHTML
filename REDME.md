# mkHTML 📝

**mkHTML** to lekki, szybki i przyjazny dla uczniów edytor kodu HTML oraz CSS. Został stworzony specjalnie z myślą o zajęciach w szkole i nauce podstaw tworzenia stron WWW. Posiada interfejs w 100% w języku polskim oraz przydatne ułatwienia, które przyspieszają pisanie kodu.

## ✨ Główne funkcje

* 🇵🇱 **Polski interfejs** – komunikaty, przyciski i menu w całości po polsku (Zapisz, Nie zapisuj, Anuluj).
* 🎨 **Kolorowanie składni** – przejrzysty i czytelny kod HTML oraz CSS ułatwiający wyłapywanie błędów.
* ⚡ **Autouzupełnianie tagów** – po wpisaniu zamykającego nawiasu `>` w tagu (np. `<body>`), edytor automatycznie dopisze tag zamykający (`</body>`).
* 🚀 **Snippety (szablony kodu)** – po wpisaniu słowa `html` i wciśnięciu klawisza `TAB`, edytor automatycznie wygeneruje pełny szkielet strony HTML5 z dołączonym plikiem stylów `style.css`. Działa również dla tagu `a`.
* 🧠 **Inteligentne wcięcia i klamry** – automatyczne domykanie klamer `{}` w CSS i cudzysłowów `""`.
* 🌍 **Szybki podgląd** – jedno kliknięcie (lub klawisz `F5`) uruchamia aktualny plik w Twojej domyślnej przeglądarce internetowej.
* 💾 **Zapisywanie ścieżki** – program pamięta ostatnio otwierany folder (domyślnie Pulpit).

## ⌨️ Przydatne skróty klawiszowe

| Skrót | Działanie |
|---|---|
| `TAB` | Rozwinięcie skrótu (np. wpisz `html` i wciśnij TAB) |
| `F5` | Uruchom stronę w przeglądarce internetowej |
| `Ctrl + S` | Zapisz plik |
| `Ctrl + N` | Nowy plik |
| `Ctrl + O` | Otwórz plik |
| `Ctrl + Z` | Cofnij zmianę |

---

## 🚀 Jak uruchomić?

### 👨‍🎓 Opcja 1: Gotowy program (Dla uczniów - najprościej)
Nie musisz instalować żadnych dodatkowych programów. 
1. Pobierz projekt na swój komputer.
2. Zainstaluj aplikację.
3. Uruchom program klikając na ikonkę mkHTML.

### 👨‍🏫 Opcja 2: Uruchomienie ze źródeł (Dla dociekliwych i nauczycieli)
Jeśli chcesz zobaczyć kod źródłowy lub samodzielnie go zmodyfikować:
1. Upewnij się, że masz zainstalowanego Pythona (wersja 3.8+).
2. Zainstaluj wymagane biblioteki w terminalu:
   ```bash
   pip install PyQt6 PyQt6-QScintilla