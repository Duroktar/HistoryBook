#!/bin/bash
# This is an auto-generated launcher script for History Book.

# Activate the virtual environment
source "/home/duroktar/source/HistoryBook/venv/bin/activate"

# Execute the main Python script
python3 "/home/duroktar/source/HistoryBook/scrape_history.py" "$@"

# Deactivate on exit (optional, as the script terminates)
deactivate
