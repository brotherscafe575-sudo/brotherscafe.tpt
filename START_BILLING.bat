@echo off
REM ════════════════════════════════════════════════════════════════
REM  BROTHERS CAFE - BILLING MODE LAUNCHER
REM  Opens the browser in SILENT PRINT mode (no print dialog).
REM  Bills print directly on the default printer (set POS80 as default!)
REM
REM  HOW TO USE: just double-click this file.
REM  If your server runs on another PC, edit the URL below.
REM ════════════════════════════════════════════════════════════════

set URL=http://127.0.0.1:8000/staff/

REM ── Close running browsers so the silent-print flag takes effect ──
taskkill /IM brave.exe /F >nul 2>&1
taskkill /IM chrome.exe /F >nul 2>&1
taskkill /IM msedge.exe /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM ── Try Brave first, then Chrome, then Edge ──
set BRAVE1="C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
set BRAVE2="%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"
set CHROME1="C:\Program Files\Google\Chrome\Application\chrome.exe"
set CHROME2="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set EDGE1="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if exist %BRAVE1% ( start "" %BRAVE1% --kiosk-printing %URL% & goto done )
if exist %BRAVE2% ( start "" %BRAVE2% --kiosk-printing %URL% & goto done )
if exist %CHROME1% ( start "" %CHROME1% --kiosk-printing %URL% & goto done )
if exist %CHROME2% ( start "" %CHROME2% --kiosk-printing %URL% & goto done )
if exist %EDGE1% ( start "" %EDGE1% --kiosk-printing %URL% & goto done )

echo Could not find Brave, Chrome or Edge. Install one of them.
pause
exit /b 1

:done
echo.
echo  ✔ Billing mode started - bills will print SILENTLY (no dialog).
echo  ✔ Make sure POS80 is the DEFAULT printer in Windows settings.
echo.
timeout /t 4 >nul
