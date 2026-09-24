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

# Instrukcja obsługi skrótów i automatyzacji w edytorze mkHTML

Edytor **mkHTML** został wyposażony w mechanizmy automatyzacji i skróty klawiszowe przyspieszające tworzenie kodu HTML oraz CSS. Poniżej znajduje się zestawienie wszystkich dostępnych skrótów oraz funkcji edytora.

---

## 1. Ogólne skróty klawiszowe

| Skrót | Działanie | Opis |
| :--- | :--- | :--- |
| `Ctrl + N` | Nowy plik | Otwiera nową zakładkę z pustym dokumentem. |
| `Ctrl + O` | Otwórz plik | Wywołuje okno wyboru pliku z dysku (z wykrywaniem duplikatów). |
| `Ctrl + S` | Zapisz | Zapisuje bieżący plik (z bezpiecznym zapisem atomowym). |
| `Ctrl + Q` | Zakończ | Zamyka aplikację (pyta o zapisanie niezapisanych zmian). |
| `Ctrl + Z` | Cofnij | Cofa ostatnią operację w edytorze. |
| `Ctrl + Y` | Ponów | Ponawia cofniętą operację. |
| `Ctrl + X` | Wytnij | Wycina zaznaczony fragment tekstu do schowka. |
| `Ctrl + C` | Kopiuj | Kopiuje zaznaczony tekst do schowka. |
| `Ctrl + V` | Wklej | Wkleja tekst ze schowka. |
| `F5` | Podgląd | Otwiera bieżący dokument HTML w domyślnej przeglądarce internetowej. |

---

## 2. Dynamiczne rozwijanie tagów i snippetów (`Tab`)

Wpisz skrót lub nazwę tagu na początku linii (lub po spacji) i naciśnij klawisz **`Tab`**, aby go rozwinąć:

### Tagi HTML
- **Dowolny tag standardowy** (np. `div`, `p`, `section`, `h1`, `article`):
  - Wpisanie `div` + `Tab` → `<div></div>` *(kursor ustawia się wewnątrz tagu)*.
- **Tagi puste / samozamykające (`void_tags`)** (np. `br`, `hr`, `img`, `input`, `meta`, `link`):
  - Wpisanie `br` + `Tab` → `<br>` *(bez tagu zamykającego)*.

### Wbudowane Snippety
- **`html` + `Tab`** – Wstawia pełny nagłówek i szkielet dokumentu HTML5:
  ```html
  <!DOCTYPE html>
  <html lang="pl">
  <head>
      <meta charset="UTF-8">
      <title>Tytuł strony</title>
      <link rel="stylesheet" href="style.css">
  </head>
  <body>
      
  </body>
  </html>
  ```
- **`a` + `Tab`** – Wstawia hiperłącze: `<a href=""></a>`
- **`img` + `Tab`** – Wstawia obrazek: `<img src="" alt="">`
- **`lorem` + `Tab`** – Wstawia akapit przykładowego tekstu (Lorem Ipsum).

> **Uwaga:** Rozwijanie klawiszem `Tab` działa inteligentnie – jest aktywne tylko w trybie HTML oraz gdy kursor znajduje się w bezpiecznym miejscu (nie rozwija tagów wewnątrz komentarzy ani cudzysłowów atrybutów).

---

## 3. Automatyzacja pisania i składni

### Automatyczne domykanie tagów HTML (`>`)
Gdy piszesz tag ręcznie i naciśniesz **`>`**, edytor automatycznie wstawi tag zamykający i ustawi kursor pomiędzy nimi:
- Wpisujesz `<span>` → Edytor tworzy `<span></span>` z kursorem w środku.
- *Wyjątki:* Tagi puste (np. `<img ...>`) oraz tagi jawnie samozamknięte (np. `<path d="..." />`) są ignorowane i nie generują dodatkowych zamknięć.

### Inteligentny Enter między tagami
Jeśli kursor znajduje się dokładnie między tagem otwierającym a zamykającym (np. `<p></p>`) i naciśniesz **`Enter`**, edytor automatycznie rozbije wiersz i sformatuje wcięcia:
```html
<p>
    
</p>
```

### Automatyczne klamry w CSS (`{`)
W plikach `.css` naciśnięcie otwierającej klamry **`{`** tworzy blok reguły z automatycznym wcięciem:
```css
body {
    
}
```

### Obsługa cudzysłowów (`"` oraz `'`)
- Naciśnięcie cudzysłowu powoduje wstawienie pary `""` z kursorem w środku.
- Jeśli kursor stoi bezpośrednio przed cudzysłowem zamknięcia, ponowne naciśnięcie znaku cudzysłowu przeskakuje nad nim zamiast go dublować.
