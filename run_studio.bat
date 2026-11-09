@echo off
title ClipPilot - Video Publishing on Autopilot
cd /d "%~dp0"
echo ========================================================
echo   CLIPPILOT - VIDEO PUBLISHING ON AUTOPILOT
echo   Made in India for Creators, Animators and Businesses
echo ========================================================
echo.
echo Starting ClipPilot local server and desktop UI...
set PYTHONIOENCODING=utf-8
python app.py
pause
