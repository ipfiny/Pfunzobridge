@echo off
cd /d "%~dp0"
title PfunzoBridge - Mobile Agentic App
echo ========================================================
echo   PfunzoBridge - Access to Higher Education Platform
echo   FNB AOTY Hackathon 2026 | Developer: Nyamande Ipfi
echo ========================================================
echo.
py manage.py check
echo.
echo Starting PfunzoBridge Mobile Web Application on http://127.0.0.1:8000
echo Access from your phone on the same Wi-Fi via your PC's IP address.
echo.
echo KEEP THIS WINDOW OPEN while using the app!
echo.
py manage.py runserver 0.0.0.0:8000
pause
