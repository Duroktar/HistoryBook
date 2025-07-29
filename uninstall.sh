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
# Define the exact lines added by the installer
CONFIG_LINES_BASH='export PROMPT_COMMAND="history -a; ${PROMPT_COMMAND:-}"'
CONFIG_LINES_ZSH_1='setopt INC_APPEND_HISTORY'
CONFIG_LINES_ZSH_2='setopt SHARE_HISTORY'
CONFIG_COMMENT='# Added by History Book installer for instant history saving'

# Helper function to remove a specific line if it exists
remove_line_if_exists() {
    local file="$1"
    local pattern="$2"
    local description="$3"

    if [ -f "$file" ]; then
        if grep -qF -- "$pattern" "$file"; then
            # Get the line number of the first occurrence of the fixed string
            local line_num=$(grep -nF "$pattern" "$file" | head -n 1 | cut -d ':' -f 1)
            if [ -n "$line_num" ]; then
                sed -i "${line_num}d" "$file"
                success "Removed '${description}' from ${file}."
                return 0 # Success
            else
                warn "Could not determine line number for '${description}' in ${file}. Skipping."
            fi
        else
            info "'${description}' not found in ${file}. Skipping removal."
        fi
    else
        info "Configuration file '${file}' not found. Skipping removal of '${description}'."
    fi
    return 1 # Failure or not found
}

case "$CURRENT_SHELL" in
    "bash")
        SHELL_RC_FILE="${HOME}/.bashrc"
        if remove_line_if_exists "$SHELL_RC_FILE" "$CONFIG_LINES_BASH" "Bash history configuration"; then
            remove_line_if_exists "$SHELL_RC_FILE" "$CONFIG_COMMENT" "History Book comment"
        fi
        ;;
    "zsh")
        SHELL_RC_FILE="${HOME}/.zshrc"
        if remove_line_if_exists "$SHELL_RC_FILE" "$CONFIG_LINES_ZSH_1" "Zsh history config line 1"; then
            : # Successfully removed, continue
        fi
        if remove_line_if_exists "$SHELL_RC_FILE" "$CONFIG_LINES_ZSH_2" "Zsh history config line 2"; then
            : # Successfully removed, continue
        fi
        # Remove the comment only if both Zsh lines were removed or never existed (clean up)
        if ! grep -qF -- "$CONFIG_LINES_ZSH_1" "$SHELL_RC_FILE" && ! grep -qF -- "$CONFIG_LINES_ZSH_2" "$SHELL_RC_FILE"; then
            remove_line_if_exists "$SHELL_RC_FILE" "$CONFIG_COMMENT" "History Book comment"
        fi
        ;;
    *)
        warn "Unsupported shell: ${CURRENT_SHELL}. Automatic history configuration rollback is not available."
        SHELL_RC_FILE=""
        ;;
esac

if [ -n "$SHELL_RC_FILE" ] && [ -f "$SHELL_RC_FILE" ]; then
    warn "Please remember to restart your terminal or run 'source ${SHELL_RC_FILE}' for changes to take effect."
else
    info "Automatic shell configuration rollback skipped due to unsupported shell or missing file."
fi
success "Shell history configuration rollback complete."

# --- Final Instructions ---
echo -e "\n🎉 ${COLOR_GREEN}Uninstallation Complete!${COLOR_RESET}"
echo "Note: Your 'project_commands.json' file (if it exists) has NOT been removed, as it contains your project data."
echo "You may delete it manually if you no longer need it."
