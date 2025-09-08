#!/usr/bin/env bash
#
# Convenience wrapper for running RepoMapper in fully automatic mode.
#
# This script activates the virtual environment and executes the repomap tool
# with the --auto flag, which uses cached results and sensible defaults
# to generate a repository map without requiring manual configuration.

# Ensure the script runs from the project root
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment 'venv' not found."
    echo "Please run the setup script to create it."
    exit 1
fi

# Run the repomap tool in auto mode
python repomap.py --auto