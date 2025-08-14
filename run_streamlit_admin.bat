@echo off
echo ========================================
echo  Aerospace Calculators - Admin Launcher
echo ========================================
echo.
echo This script will run Streamlit with administrator privileges
echo to bypass Windows socket permission errors.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo Activating conda environment...
call conda activate textappv2
if errorlevel 1 (
    echo ERROR: Failed to activate textappv2 environment
    echo Make sure Conda is installed and textappv2 environment exists
    pause
    exit /b 1
)

echo.
echo Starting Streamlit...
echo The app will open automatically in your browser.
echo To stop the server, press Ctrl+C in this window.
echo.

streamlit run streamlit_app.py --server.port 8501
if errorlevel 1 (
    echo.
    echo ERROR: Streamlit failed to start
    echo This might be due to:
    echo - Missing dependencies
    echo - Port already in use
    echo - Network permissions
    echo.
    echo Try running this batch file as Administrator.
    pause
    exit /b 1
)

echo.
echo Server stopped.
pause
