@echo off
REM Script to activate the Validatus virtual environment on Windows

echo Activating Validatus Virtual Environment...
call validatus-env\Scripts\activate.bat
echo.
echo ✅ Virtual environment activated!
echo You can now run Python commands with all the Validatus packages installed.
echo.
echo To test the installation, try:
echo   python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
echo   python -c "import uvicorn; print('Uvicorn installed successfully')"
echo.
echo To run the application:
echo   cd backend
echo   python -m app.main
echo.
echo To deactivate the virtual environment later:
echo   deactivate
echo.
