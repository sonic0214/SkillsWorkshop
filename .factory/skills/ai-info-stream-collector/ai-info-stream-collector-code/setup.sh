#!/bin/bash

echo "Creating project structure..."
mkdir -p src/scrapers data logs

echo "Installing dependencies..."
python3 -m pip install --quiet requests beautifulsoup4 feedparser pyyaml apscheduler deep-translator lxml python-dateutil

echo "Creating Python files..."

# Create __init__ files
touch src/__init__.py
touch src/scrapers/__init__.py

echo "Setup complete!"
echo "Next steps:"
echo "1. Run once: python3 main.py --once"
echo "2. Run with scheduler: python3 main.py"
