#!/bin/bash

# A script to set up the development environment for the "History Book" project.
# It creates a Python virtual environment and installs all necessary dependencies,
# including those for testing.

# --- Style Definitions ---
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

warn() {
    echo -e "${COLOR_YELLOW}WARNING: $1${COLOR_RESET}"
}

error() {
    echo -e "${COLOR_RED}ERROR: $1${COLOR_RESET}" >&2
    exit 1
}

# --- Configuration ---
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${PROJECT_DIR}/venv"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"
TEST_REQUIREMENTS_FILE="${PROJECT_DIR}/test_requirements.txt"

# --- Main Development Installation Logic ---

info "Starting setup of History Book development environment..."

# 1. Check for Python 3
info "Step 1: Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install it to continue."
fi
success "Python 3 is present."

# 2. Set up Python Virtual Environment
info "Step 2: Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment."
else
    info "Virtual environment already exists."
fi
success "Virtual environment is ready."

# 3. Install Application Requirements
info "Step 3: Installing application requirements from ${REQUIREMENTS_FILE}..."
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    error "Application requirements file '${REQUIREMENTS_FILE}' not found. Please ensure it exists."
fi
source "${VENV_DIR}/bin/activate" || error "Failed to activate virtual environment."
pip install -r "$REQUIREMENTS_FILE" || error "Failed to install application packages."
success "Application requirements installed."

# 4. Install Test Requirements
info "Step 4: Installing test requirements from ${TEST_REQUIREMENTS_FILE}..."
if [ ! -f "$TEST_REQUIREMENTS_FILE" ]; then
    warn "Test requirements file '${TEST_REQUIREMENTS_FILE}' not found. Skipping test dependency installation."
else
    pip install -r "$TEST_REQUIREMENTS_FILE" || error "Failed to install test packages."
    success "Test requirements installed."
fi

deactivate # Deactivate the virtual environment after installation
success "Development environment setup complete."

# --- Final Instructions ---
echo -e "\n🎉 ${COLOR_GREEN}Development Environment Ready!${COLOR_RESET}"
# Corrected: Added -e to interpret color codes
echo -e "To activate your environment, run: ${COLOR_YELLOW}source ${VENV_DIR}/bin/activate${COLOR_RESET}"
echo -e "To run tests, activate the environment and then run: ${COLOR_YELLOW}pytest${COLOR_RESET}"
echo -e "For more development details, see: ${COLOR_YELLOW}DEVELOPMENT.md${COLOR_RESET}"
