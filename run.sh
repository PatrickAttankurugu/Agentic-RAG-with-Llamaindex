#!/bin/bash

# Agentic RAG - Run Script for Unix/Linux/macOS
# This script sets up and runs the Streamlit application

set -e  # Exit on error

echo "======================================"
echo "  Agentic RAG with LlamaIndex"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/installed.flag" ]; then
    echo ""
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed.flag
    echo "✅ Dependencies installed"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your Google API key!"
        echo "Get your API key from: https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Press Enter after you've added your API key to .env..."
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check if API key is set
if ! grep -q "GOOGLE_API_KEY=.*[^your_google_api_key_here]" .env; then
    echo ""
    echo "⚠️  WARNING: API key might not be configured in .env"
    echo "Please ensure GOOGLE_API_KEY is set correctly"
    echo ""
fi

# Run the application
echo ""
echo "Starting Streamlit application..."
echo "======================================"
echo ""

streamlit run app.py

# Deactivate virtual environment on exit
deactivate
