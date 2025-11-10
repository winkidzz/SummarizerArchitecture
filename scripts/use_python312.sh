#!/bin/bash
# Activate Python 3.12 virtual environment for this project

cd "$(dirname "$0")/.."

if [ ! -d "venv312" ]; then
    echo "Creating Python 3.12 virtual environment..."
    /opt/homebrew/bin/python3.12 -m venv venv312
    source venv312/bin/activate
    pip install --upgrade pip setuptools wheel
    echo "Installing project dependencies..."
    pip install -r requirements.txt
else
    source venv312/bin/activate
fi

echo "✅ Python 3.12 virtual environment activated"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

