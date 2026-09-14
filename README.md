# mkHTML 📝

**mkHTML** to lekki, szybki i przyjazny dla uczniów edytor kodu HTML oraz CSS. Został stworzony specjalnie z myślą o zajęciach w szkole i nauce podstaw tworzenia stron WWW. Posiada interfejs w 100% w języku polskim oraz przydatne ułatwienia, które przyspieszają pisanie kodu.

---

## ✨ Główne funkcje

* 🇵🇱 **Polski interfejs** – komunikaty, przyciski i menu w całości po polsku.
* 📑 **Wielozakładkowość (Tabs)** – wygodna praca nad kilkoma plikami naraz (np. jednoczesna edycja `index.html` i `style.css`).
* 🎨 **Kolorowanie składni** – przejrzysty i czytelny kod HTML oraz CSS ułatwiający wyłapywanie błędów.
* ⚡ **Autouzupełnij tagów** – po wpisaniu zamykającego nawiasu `>` w tagu (np. `<body>`), edytor automatycznie dopisze tag zamykający (`</body>`).
* 🚀 **Rozwijanie tagów klawiszem TAB** – wpisanie nazwy znacznika (np. `p`, `h1`, `div`, `section`, `br`) i wciśnięcie klawisza `TAB` generuje gotowy tag.
* 📋 **Szablony kodu (Snippets)** – wpisanie słowa `html` + `TAB` generuje pełny szkielet strony HTML5 z dołączonym plikiem stylów `style.css`.
* 🧠 **Inteligentne wcięcia i klamry** – automatyczne domykanie klamer `{}` w CSS oraz cudzysłowów `""`.
* 🌍 **Szybki podgląd** – jedno kliknięcie (lub klawisz `F5`) uruchamia aktualny plik HTML w domyślnej przeglądarce internetowej.
* 💾 **Zapisywanie ustawień** – program pamięta ostatnio otwierany folder oraz położenie i rozmiar okna na ekranie.

---

## 📥 Pobieranie

Najnowszą wersję instalatora dla systemu Windows można pobrać bezpośrednio z oficjalnego repozytorium GitHub:

👉 **[Pobierz najnowszą wersję z GitHub Releases](https://github.com/StaryDooh/mkHTML/releases)**

---

## ⚙️ Instalacja

### 👨‍🎓 Standardowa instalacja
1. Pobierz plik instalacyjny `Setup_mkHTML_vX.X.X.X.exe` z działu *Releases*.
2. Uruchom plik i przejdź przez standardowy proces instalacji.
3. Po zakończeniu uruchom program za pomocą skrótu na Pulpicie lub w Menu Start.

### 🏫 Instalacja nienadzorowana (Cicha instalacja dla pracowni szkolnych)
Instalator został przygotowany w programie **Inno Setup**, co umożliwia bezobsługową instalację na wielu komputerach jednocześnie (np. za pomocą skryptów `.bat` lub narzędzi zarządzania siecią szkolną).

Aby zainstalować program w trybie cichym, uruchom wiersz poleceń (CMD) jako administrator i wpisz:

```cmd
Setup_mkHTML_v0.0.2.1.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

**Przełączniki instalatora:**
* `/VERYSILENT` – ukrywa interfejs graficzny instalatora (instalacja odbywa się w tle bez udziału użytkownika).
* `/SUPPRESSMSGBOXES` – blokuje wyświetlanie jakichkolwiek okien dialogowych i komunikatów o błędach/pytaniach.
* `/NORESTART` – zapobiega automatycznemu ponownemu uruchomieniu komputera po zakończeniu instalacji.
* `/DIR="C:\TwojaSciezka"` *(opcjonalnie)* – pozwala wymusić niestandardowy folder instalacji.

---

## ⌨️ Przydatne skróty klawiszowe

| Skrót | Działanie |
|---|---|
| `TAB` | Rozwinięcie znacznika / szablonu (np. wpisz `html` lub `div` i wciśnij TAB) |
| `F5` | Uruchom stronę w domyślnej przeglądarce internetowej |
| `Ctrl + N` | Nowa zakładka / nowy plik |
| `Ctrl + O` | Otwórz plik w nowej zakładce |
| `Ctrl + S` | Zapisz aktywny plik |
| `Ctrl + Shift + S` | Zapisz aktywny plik jako... |
| `Ctrl + Z` | Cofnij zmianę |
| `Ctrl + Y` | Ponów zmianę |
| `Ctrl + X` | Wytnij zaznaczony tekst |
| `Ctrl + C` | Kopiuj zaznaczony tekst |
| `Ctrl + V` | Wklej tekst ze schowka |
| `Ctrl + Q` | Zamknij aplikację |

---

## 👨‍🏫 Uruchomienie ze źródeł (Dla dociekliwych i nauczycieli)

Jeśli chcesz zobaczyć kod źródłowy lub samodzielnie go zmodyfikować:

1. Upewnij się, że masz zainstalowane środowisko Python (wersja 3.8 lub nowsza).
2. Sklonuj repozytorium:
   ```bash
   git clone [https://github.com/StaryDooh/mkHTML.git](https://github.com/StaryDooh/mkHTML.git)
   cd mkHTML
   ```
3. Zainstaluj wymagane biblioteki:
   ```bash
   pip install PyQt6 PyQt6-QScintilla
   ```
4. Uruchom program:
   ```bash
   python main.py
   ```