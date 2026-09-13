#define MyAppVersion "0.0.1.1"


[Setup]
; --- BARDZO WAŻNE: To jest nowy AppId dla mkHTML! ---
; W Inno Setup kliknij u góry: Tools -> Generate GUID (lub Shift+Ctrl+G)
; i podmień poniższy ciąg znaków, jeśli chcesz wygenerować własny.
AppId={{66C114CB-D177-488A-9F95-F09427482748}

AppName=mkHTML
AppVersion={#MyAppVersion}
AppPublisher=Krzysztof Markowski

; Domyślny folder instalacji (Program Files)
DefaultDirName={autopf}\mkHTML
DefaultGroupName=mkHTML
PrivilegesRequired=admin

; Plik licencji, który przygotowaliśmy
LicenseFile=Licencja.txt

; Ikony instalatora i deinstalatora
SetupIconFile=ikona.ico
UninstallDisplayIcon={app}\ikona.ico

; Gdzie ma się zapisać gotowy instalator i jak ma się nazywać
OutputDir=.\GitHub
OutputBaseFilename=Setup_mkHTML_v{#MyAppVersion}

; Najlepsza kompresja, żeby plik ważył jak najmniej
Compression=lzma
SolidCompression=yes

; Ułatwia aktualizację (próbuje zamknąć mkHTML, jeśli jest włączony)
CloseApplications=yes

; Informuje system Windows, że instalator zmienia skojarzenia plików
ChangesAssociations=yes

[Languages]
Name: "pl"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
; Główny plik wykonywalny pobierany z podkatalogu dist/mkHTML
Source: "dist\mkHTML\mkHTML.exe"; DestDir: "{app}"; Flags: ignoreversion

; Kopiuje całą resztę z folderu dist/mkHTML (w tym folder _internal ze wszystkimi plikami)
Source: "dist\mkHTML\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dodatkowe pliki leżące obok skryptu .iss
Source: "Licencja.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "ikona.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Tworzenie skrótów w Menu Start i na Pulpicie
Name: "{autoprograms}\mkHTML"; Filename: "{app}\mkHTML.exe"; IconFilename: "{app}\ikona.ico"
Name: "{autodesktop}\mkHTML"; Filename: "{app}\mkHTML.exe"; IconFilename: "{app}\ikona.ico"; Tasks: desktopicon
