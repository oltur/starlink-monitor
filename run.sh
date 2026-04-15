#!/bin/bash

# Activate virtual environment and run the Starlink dashboard

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting Starlink Metrics Dashboard..."
python app.py
