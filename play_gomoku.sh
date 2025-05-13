#!/bin/bash
# Launcher script for Five in a Row (Gomoku) game

echo "Starting Five in a Row (Gomoku)..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Set up Python path environment variable
export PYTHONPATH="$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please make sure Python 3 is installed."
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Run the launcher script
python3 play_gomoku.py

# If the game exited with an error, wait for user input
if [ $? -ne 0 ]; then
    echo ""
    echo "The game exited with an error. Check the output above for details."
    echo "Press Enter to exit..."
    read
fi
