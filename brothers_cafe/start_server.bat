@echo off
cd /d "%~dp0"
echo ============================================
echo   Brothers Cafe - Starting Server
echo ============================================
echo.
echo [1/3] Running migrations...
python manage.py migrate
echo.
echo [2/3] Starting server on 192.168.1.28:8000
echo       (Change IP below if needed)
echo.
echo Press CTRL+C to stop the server
echo.
python manage.py runserver 192.168.1.28:8000
pause
