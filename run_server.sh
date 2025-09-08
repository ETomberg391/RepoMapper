#!/bin/bash

# Define the virtual environment directory
VENV_DIR="venv"

# Function to print messages
log() {
    echo "--- $1 ---"
}

# Function to handle script interruption (Ctrl+C)
cleanup() {
    log "Script interrupted. The Python server should be shutting down."
    exit 0
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    log "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        log "Error: Failed to create virtual environment."
        exit 1
    fi

    log "Activating virtual environment..."
    source $VENV_DIR/bin/activate

    log "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        log "Error: Failed to install dependencies."
        exit 1
    fi
else
    log "Virtual environment found. Activating..."
    source $VENV_DIR/bin/activate

    log "Attempting to update dependencies..."
    pip install --upgrade -r requirements.txt
    if [ $? -ne 0 ]; then
        log "Warning: Failed to update dependencies. Continuing with existing packages."
    fi
fi

# Launch the RepoMap server in the foreground with debug flag
log "Launching RepoMap server... (Press Ctrl+C to shut down)"
python repomap_server.py --debug "$@"

log "Server process has finished."