@echo off
REM Agentic RAG - Run Script for Windows
REM This script sets up and runs the Streamlit application

echo ======================================
echo   Agentic RAG with LlamaIndex
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo WARNING: Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\installed.flag" (
    echo.
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    type nul > venv\installed.flag
    echo Dependencies installed
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo.
        echo IMPORTANT: Please edit .env and add your Google API key!
        echo Get your API key from: https://makersuite.google.com/app/apikey
        echo.
        pause
    ) else (
        echo ERROR: .env.example not found. Please create a .env file manually.
        pause
        exit /b 1
    )
)

REM Run the application
echo.
echo Starting Streamlit application...
echo ======================================
echo.

streamlit run app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
