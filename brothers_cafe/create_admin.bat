@echo off
cd /d "%~dp0"
echo ============================================
echo   Brothers Cafe - Create Admin User
echo ============================================
echo.
echo Enter details for the staff login account:
echo.
python manage.py createsuperuser
pause
