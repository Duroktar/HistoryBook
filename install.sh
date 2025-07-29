#!/bin/bash

# A script to install the "History Book" project.
# It checks for dependencies, sets up a Python virtual environment,
# and creates a symlink in the user's local bin directory.

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
MAIN_SCRIPT_NAME="scrape_history.py"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"
SYMLINK_DIR="${HOME}/.local/bin"
SYMLINK_NAME="history_book"
LAUNCHER_SCRIPT_PATH="${PROJECT_DIR}/${SYMLINK_NAME}_launcher.sh"

# --- Main Installation Logic ---

# 1. Check for System Dependencies
info "Step 1: Checking for required system dependencies..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install it to continue."
fi

if ! command -v dialog &> /dev/null; then
    error "'dialog' is not installed. Please install it using your system's package manager (e.g., 'sudo apt install dialog' or 'brew install dialog')."
fi
success "All system dependencies are present."

# 2. Set up Python Virtual Environment
info "Step 2: Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment."
else
    info "Virtual environment already exists."
fi
success "Virtual environment is ready."

# 3. Install Python Requirements
info "Step 3: Installing Python requirements..."
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    error "requirements.txt not found in project directory. Please create it."
fi
# Activate venv and install
source "${VENV_DIR}/bin/activate"
pip install -r "$REQUIREMENTS_FILE" || error "Failed to install Python packages from requirements.txt."
deactivate
success "Python requirements installed."

# 4. Create the Launcher Script
info "Step 4: Creating the launcher script..."
# This script ensures the command always runs within its virtual environment.
cat > "$LAUNCHER_SCRIPT_PATH" << EOF
#!/bin/bash
# This is an auto-generated launcher script for History Book.

# Activate the virtual environment
source "${VENV_DIR}/bin/activate"

# Execute the main Python script
python3 "${PROJECT_DIR}/${MAIN_SCRIPT_NAME}" "\$@"

# Deactivate on exit (optional, as the script terminates)
deactivate
EOF
chmod +x "$LAUNCHER_SCRIPT_PATH" || error "Failed to make launcher script executable."
success "Launcher script created at ${LAUNCHER_SCRIPT_PATH}"

# 5. Create the Symbolic Link
info "Step 5: Creating symbolic link for 'history_book' command..."
mkdir -p "$SYMLINK_DIR" # Create the directory if it doesn't exist
ln -sf "$LAUNCHER_SCRIPT_PATH" "${SYMLINK_DIR}/${SYMLINK_NAME}" || error "Failed to create symbolic link."
success "Symbolic link created at ${SYMLINK_DIR}/${SYMLINK_NAME}"

# --- Final Instructions ---
echo -e "\n🎉 ${COLOR_GREEN}Installation Complete!${COLOR_RESET}"
echo -e "You can now run the command '${COLOR_YELLOW}${SYMLINK_NAME}${COLOR_RESET}' from anywhere in your terminal."
warn "If the command is not found, you may need to add '${SYMLINK_DIR}' to your shell's PATH."
warn "You can do this by adding the following line to your ~/.bashrc, ~/.zshrc, or equivalent shell profile file:"
echo -e "\n    ${COLOR_YELLOW}export PATH=\"\$HOME/.local/bin:\$PATH\"${COLOR_RESET}\n"
echo "Then, restart your shell or run 'source ~/.bashrc' (or equivalent)."


