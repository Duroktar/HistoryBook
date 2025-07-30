#!/usr/bin/env python3

import os
import re
import json
import uuid
import sys
# --- MODIFICATION START ---
# Changed from dialog to whiptail
from whiptail import Whiptail
# --- MODIFICATION END ---

# --- Configuration ---
# This script now outputs JSON to stdout, so OUTPUT_FILENAME is not used here
# It's managed by history_book.py
# OUTPUT_FILENAME = "project_commands.json" 
COMMAND_LIMIT = 200
# --- End Configuration ---

def get_history_file_path():
    """Detects the most likely shell history file."""
    home = os.path.expanduser("~")
    history_files = {
        "zsh": os.path.join(home, ".zsh_history"),
        "bash": os.path.join(home, ".bash_history"),
        "fish": os.path.join(home, ".local/share/fish/fish_history")
    }
    for shell, path in history_files.items():
        if os.path.exists(path):
            # print(f"✅ Found {shell.capitalize()} history...") # Suppress for cleaner subprocess output
            return path, shell
    return None, None

def parse_history(file_path, shell_type):
    """Reads and cleans the history file."""
    commands = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
        seen_commands = set()
        for line in reversed(lines):
            line = line.strip()
            if not line: continue
            if shell_type == "zsh": line = re.sub(r'^: \d+:\d+;', '', line)
            if shell_type == "fish" and line.startswith('- cmd: '): line = line[7:]
            if line and line not in seen_commands:
                seen_commands.add(line)
                commands.append(line)
            if len(commands) >= COMMAND_LIMIT: break
        return commands
    except Exception as e:
        # print(f"❌ Error reading history file: {e}") # Suppress for cleaner subprocess output
        return []

# --- MODIFICATION START ---
# Removed load_existing_commands and save_commands, as history_book.py handles this
# This script only outputs new commands
# def load_existing_commands(filename): ...
# def save_commands(filename, new_entries, existing_data): ...

def main():
    """Main function to run the TUI and output selected commands as JSON."""
    w = Whiptail(title="History Book Scraper", backtitle="Select Commands")

    file_path, shell_type = get_history_file_path()
    if not file_path:
        w.msgbox("Could not find a supported history file (.zsh_history, .bash_history) in your home directory.")
        sys.exit(1) # Exit with error code if no history file

    commands = parse_history(file_path, shell_type)
    if not commands:
        w.msgbox("No commands found or unable to parse history file.")
        sys.exit(1) # Exit with error code if no commands

    # We no longer filter against existing commands here; history_book.py will do that.
    # This script just presents all recent commands from history.

    # Create a dictionary to map a unique tag (index) back to the full command string
    command_map = {str(i): cmd for i, cmd in enumerate(commands)}
    
    # Format for the checklist: (tag, item, status) for whiptail
    choices = [(str(i), cmd, 'OFF') for i, cmd in enumerate(commands)]

    selected_tags, exit_code = w.checklist(
        "Use SPACE to select commands you wish to save for this project. Press ENTER when done.",
        choices
    )

    if exit_code == 0 and selected_tags: # 0 indicates OK/Yes in whiptail
        new_entries = []
        for tag in selected_tags:
            command_text = command_map[tag]
            
            # --- Prompt for short name, description, tags, and quiet flag ---
            # Prompt for a short name
            name, code_name = w.inputbox(
                f"Enter a short name for:\n\n'{command_text}'\n\n(Optional, for 'run <name>')",
                default=""
            )
            if code_name != 0: name = "" # Handle cancel

            # Prompt for description
            description, code_desc = w.inputbox(
                f"Enter a description for:\n\n'{command_text}'",
                default=""
            )
            if code_desc != 0: description = "" # Handle cancel

            # Prompt for tags
            tags_str, code_tags = w.inputbox(
                f"Enter comma-separated tags for:\n\n'{command_text}'\n\n(e.g., build, test, docker)",
                default=""
            )
            tags = [tag.strip() for tag in tags_str.split(',')] if code_tags == 0 and tags_str else []

            # Prompt for quiet
            quiet_status_initial = "OFF" # New commands default to not quiet
            prompt_quiet_text = (
                f"Set command '{command_text}' to run quietly by default?\n\n"
                f"Current status: {quiet_status_initial}\n\n"
                "Select 'Yes' to suppress this script's output (e.g., 'Running:' messages) when this command is executed via 'history_book run'.\n"
                "Select 'No' to show all output."
            )
            quiet_selected = w.yesno(prompt_quiet_text) # True for Yes, False for No/Cancel

            entry = {
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "command": command_text,
                "description": description,
                "tags": tags,
                "last_run": None,
                "quiet": quiet_selected # Directly assign boolean from yesno
            }
            new_entries.append(entry)
        
        # Print the selected new entries as JSON to stdout
        # history_book.py will capture this
        print(json.dumps(new_entries, indent=2))
        sys.exit(0) # Indicate success
    else:
        # If no commands selected or cancelled, print empty JSON array
        print("[]")
        sys.exit(1) # Indicate cancellation/no selection
# --- MODIFICATION END ---

if __name__ == "__main__":
    main()

