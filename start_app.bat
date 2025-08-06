@echo off
echo 🚀 Starte AI Diagnostic Assistant...
echo.

REM Virtuelles Environment aktivieren
call venv\Scripts\activate.bat

REM Streamlit starten
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats=false

pause 