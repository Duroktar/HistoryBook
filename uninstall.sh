#!/bin/bash

# A script to uninstall the "History Book" project.
# It removes the symlink, launcher script, Python virtual environment,
# and optionally reverts changes made to the user's shell configuration.

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
    # For uninstall, we don't always exit on error for non-critical removals.
    # We'll just report and continue where possible.
}

# --- Configuration (Must match install.sh) ---
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${PROJECT_DIR}/venv"
MAIN_SCRIPT_NAME="scrape_history.py" # Not directly used for uninstall, but good to keep consistent
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt" # Not directly used for uninstall
SYMLINK_DIR="${HOME}/.local/bin"
SYMLINK_NAME="history_book"
LAUNCHER_SCRIPT_PATH="${PROJECT_DIR}/${SYMLINK_NAME}_launcher.sh"

# --- Main Uninstallation Logic ---

info "Starting uninstallation of History Book project..."

# 1. Confirmation
read -p "$(warn "Are you sure you want to uninstall History Book? (y/N): ")" -n 1 -r
echo # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    info "Uninstallation cancelled."
    exit 0
fi

# 2. Remove Symbolic Link
info "Step 1: Removing symbolic link..."
SYMLINK_FULL_PATH="${SYMLINK_DIR}/${SYMLINK_NAME}"
if [ -L "$SYMLINK_FULL_PATH" ] && [ "$(readlink "$SYMLINK_FULL_PATH")" == "$LAUNCHER_SCRIPT_PATH" ]; then
    rm "$SYMLINK_FULL_PATH"
    success "Removed symbolic link: ${SYMLINK_FULL_PATH}"
elif [ -e "$SYMLINK_FULL_PATH" ]; then
    warn "Symbolic link '${SYMLINK_FULL_PATH}' exists but does not point to the expected launcher script or is not a symlink. Skipping removal."
else
    info "Symbolic link '${SYMLINK_FULL_PATH}' does not exist. Skipping."
fi

# 3. Remove the Launcher Script
info "Step 2: Removing launcher script..."
if [ -f "$LAUNCHER_SCRIPT_PATH" ]; then
    rm "$LAUNCHER_SCRIPT_PATH"
    success "Removed launcher script: ${LAUNCHER_SCRIPT_PATH}"
else
    info "Launcher script '${LAUNCHER_SCRIPT_PATH}' does not exist. Skipping."
fi

# 4. Remove Python Virtual Environment
info "Step 3: Removing Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    success "Removed virtual environment: ${VENV_DIR}"
else
    info "Virtual environment '${VENV_DIR}' does not exist. Skipping."
fi

# 5. Revert Shell History Configuration
info "Step 4: Reverting shell history configuration (optional)..."

CURRENT_SHELL=$(basename "$SHELL")
SHELL_RC_FILE=""
CONFIG_LINES_BASH='export PROMPT_COMMAND="history -a; ${PROMPT_COMMAND:-}"'
CONFIG_LINES_ZSH_1='setopt INC_APPEND_HISTORY'
CONFIG_LINES_ZSH_2='setopt SHARE_HISTORY'
CONFIG_COMMENT='# Added by History Book installer for instant history saving'

case "$CURRENT_SHELL" in
    "bash")
        SHELL_RC_FILE="${HOME}/.bashrc"
        ;;
    "zsh")
        SHELL_RC_FILE="${HOME}/.zshrc"
        ;;
    *)
        warn "Unsupported shell: ${CURRENT_SHELL}. Automatic history configuration rollback is not available."
        SHELL_RC_FILE=""
        ;;
esac

if [ -n "$SHELL_RC_FILE" ] && [ -f "$SHELL_RC_FILE" ]; then
    info "Checking ${SHELL_RC_FILE} for History Book configuration..."
    
    # Remove Bash specific lines
    if [[ "$CURRENT_SHELL" == "bash" ]] && grep -qF -- "$CONFIG_LINES_BASH" "$SHELL_RC_FILE"; then
        sed -i "\_$(echo "$CONFIG_LINES_BASH" | sed 's/[\/&]/\\&/g')_d" "$SHELL_RC_FILE"
        success "Removed Bash history configuration from ${SHELL_RC_FILE}."
    fi

    # Remove Zsh specific lines
    if [[ "$CURRENT_SHELL" == "zsh" ]]; then
        if grep -qF -- "$CONFIG_LINES_ZSH_1" "$SHELL_RC_FILE"; then
            sed -i "\_$(echo "$CONFIG_LINES_ZSH_1" | sed 's/[\/&]/\\&/g')_d" "$SHELL_RC_FILE"
            success "Removed Zsh history config line 1 from ${SHELL_RC_FILE}."
        fi
        if grep -qF -- "$CONFIG_LINES_ZSH_2" "$SHELL_RC_FILE"; then
            sed -i "\_$(echo "$CONFIG_LINES_ZSH_2" | sed 's/[\/&]/\\&/g')_d" "$SHELL_RC_FILE"
            success "Removed Zsh history config line 2 from ${SHELL_RC_FILE}."
        fi
    fi

    # Remove the installer comment line
    if grep -qF -- "$CONFIG_COMMENT" "$SHELL_RC_FILE"; then
        sed -i "\_$(echo "$CONFIG_COMMENT" | sed 's/[\/&]/\\&/g')_d" "$SHELL_RC_FILE"
        success "Removed History Book comment from ${SHELL_RC_FILE}."
    fi

    if [[ "$?" -eq 0 ]]; then # Check status of last sed command
        warn "Please remember to restart your terminal or run 'source ${SHELL_RC_FILE}' for changes to take effect."
    else
        error "Failed to modify ${SHELL_RC_FILE}. Please check permissions or remove lines manually."
    fi
else
    info "Shell configuration file '${SHELL_RC_FILE}' not found or not applicable. Skipping."
fi
success "Shell history configuration rollback complete."

# --- Final Instructions ---
echo -e "\n🎉 ${COLOR_GREEN}Uninstallation Complete!${COLOR_RESET}"
echo "Note: Your 'project_commands.json' file (if it exists) has NOT been removed, as it contains your project data."
echo "You may delete it manually if you no longer need it."
