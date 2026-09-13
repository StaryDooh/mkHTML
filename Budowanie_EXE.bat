@echo off
echo ==========================================
echo Budowanie mkHTML (Tryb Katalogu)
echo ==========================================

:: 1. Czyszczenie starych kompilacji
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [1/2] Stare pliki usuniete.
echo [2/2] Rozpoczynam prace PyInstallera...

:: 2. Kompilacja do katalogu (--onedir)

python -m PyInstaller ^
	--noconsole ^
	--icon="ikona.ico" ^
	--version-file="wersja.txt" ^
	--add-data "ikona.ico;." ^
	mkHTML.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ==========================================
    echo SUKCES: Gotowe w dist\mkHTML
    echo ==========================================
) else (
    echo ##########################################
    echo BLAD: Cos poszlo nie tak przy budowaniu!
    echo ##########################################
)

pause