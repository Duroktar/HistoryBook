#!/bin/bash

# A script to activate the development virtual environment and run pytest.

# --- Style Definitions (for consistent output) ---
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

# --- Helper Functions ---
info() {
    echo -e "${COLOR_BLUE}INFO: $1${COLOR_RESET}"
}

success() {
    echo -e "${COLOR_GREEN}SUCCESS: $1${COLOR_RESET}"
}

error() {
    echo -e "${COLOR_RED}ERROR: $1${COLOR_RESET}" >&2
    exit 1
}

# --- Configuration ---
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${PROJECT_DIR}/venv"

# --- Main Logic ---

info "Activating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    error "Virtual environment not found at ${VENV_DIR}. Please run ./dev-install.sh first."
fi

source "${VENV_DIR}/bin/activate" || error "Failed to activate virtual environment."
success "Virtual environment activated."

info "Running tests with pytest..."
pytest "$@" # Pass any arguments from run_tests.sh directly to pytest

# Deactivate the virtual environment when tests are done
deactivate
success "Tests finished. Virtual environment deactivated."
