#!/usr/bin/env python3

import os
import re
import json
import uuid
import sys
import argparse # NEW: Import argparse
from whiptail import Whiptail

# --- Configuration ---
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

def main():
    # Add argument parsing for output file
    parser = argparse.ArgumentParser(description="History Book Scraper CLI")
    parser.add_argument('--output-file', type=str, required=True,
                        help='Path to the file where selected commands will be written as JSON.')
    args = parser.parse_args()

    w = Whiptail(title="History Book Scraper", backtitle="Select Commands")

    file_path, shell_type = get_history_file_path()
    if not file_path:
        w.msgbox("Could not find a supported history file (.zsh_history, .bash_history) in your home directory.")
        sys.exit(1)

    commands = parse_history(file_path, shell_type)
    if not commands:
        w.msgbox("No commands found or unable to parse history file.")
        sys.exit(1)

    command_map = {str(i): cmd for i, cmd in enumerate(commands)}
    
    choices = [(str(i), cmd, 'OFF') for i, cmd in enumerate(commands)]

    selected_tags, exit_code = w.checklist(
        "Use SPACE to select commands you wish to save for this project. Press ENTER when done.",
        choices
    )

    new_entries = []
    if exit_code == 0 and selected_tags: # 0 indicates OK/Yes in whiptail
        for tag in selected_tags:
            command_text = command_map[tag]
            
            name, code_name = w.inputbox(
                f"Enter a short name for:\n\n'{command_text}'\n\n(Optional, for 'run <name>')",
                default=""
            )
            if code_name != 0: name = ""

            description, code_desc = w.inputbox(
                f"Enter a description for:\n\n'{command_text}'",
                default=""
            )
            if code_desc != 0: description = ""

            tags_str, code_tags = w.inputbox(
                f"Enter comma-separated tags for:\n\n'{command_text}'\n\n(e.g., build, test, docker)",
                default=""
            )
            tags = [tag.strip() for tag in tags_str.split(',')] if code_tags == 0 and tags_str else []

            quiet_status_initial = "OFF"
            prompt_quiet_text = (
                f"Set command '{command_text}' to run quietly by default?\n\n"
                f"Current status: {quiet_status_initial}\n\n"
                "Select 'Yes' to suppress this script's output (e.g., 'Running:' messages) when this command is executed via 'history_book run'.\n"
                "Select 'No' to show all output."
            )
            quiet_selected = w.yesno(prompt_quiet_text)

            entry = {
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "command": command_text,
                "description": description,
                "tags": tags,
                "last_run": None,
                "quiet": quiet_selected
            }
            new_entries.append(entry)
    
    # Write the JSON output to the specified file
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(new_entries, f, indent=2)
        sys.exit(0) # Indicate success
    except IOError as e:
        # Print error to stderr, as stdout is for JSON
        print(f"❌ Error writing output to file '{args.output_file}': {e}", file=sys.stderr)
        sys.exit(1) # Indicate failure

if __name__ == "__main__":
    main()
