@echo off
REM File: Setup.bat
REM Path: OllamaModelEditor/scripts/Setup.bat
REM Standard: AIDEV-PascalCase-1.2
REM Created: 2025-03-11
REM Last Modified: 2025-03-11
REM Description: Windows setup script for OllamaModelEditor project

echo === Setting Up Python Virtual Environment ===
python -m venv .venv
call .venv\Scripts\activate.bat

echo === Installing Dependencies ===
pip install -r requirements.txt

echo === Setup Complete ===
echo.
echo Virtual environment created and dependencies installed.
echo To activate the virtual environment in the future, run:
echo   .venv\Scripts\activate.bat
echo.
pause
