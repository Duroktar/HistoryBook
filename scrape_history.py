#!/usr/bin/env python3

import os
import re
import json
import uuid
from dialog import Dialog

# --- Configuration ---
# The name of the file where commands will be saved.
OUTPUT_FILENAME = "project_commands.json"
# Number of recent commands to display in the TUI.
COMMAND_LIMIT = 200
# --- End Configuration ---

def get_history_file_path():
    """Detects the most likely shell history file based on common shells."""
    home = os.path.expanduser("~")
    # A prioritized list of history files to check.
    history_files = {
        "zsh": os.path.join(home, ".zsh_history"),
        "bash": os.path.join(home, ".bash_history"),
        "fish": os.path.join(home, ".local/share/fish/fish_history")
    }
    
    for shell, path in history_files.items():
        if os.path.exists(path):
            print(f"✅ Found {shell.capitalize()} history...")
            return path, shell
    
    return None, None

def parse_history(file_path, shell_type):
    """
    Reads the history file and returns a clean list of the most recent,
    unique commands.
    """
    commands = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
        
        # Use a set for efficient duplicate checking of recent commands.
        seen_commands = set()
        
        # Read file in reverse to get the most recent commands first.
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            
            # Zsh history lines are often prefixed with a timestamp.
            # e.g., ": 1672531200:0;ls -la" -> "ls -la"
            if shell_type == "zsh":
                line = re.sub(r'^: \d+:\d+;', '', line)
            
            # Fish history has its own format.
            # e.g., "- cmd: ls -la"
            if shell_type == "fish" and line.startswith('- cmd: '):
                line = line[7:]

            # Avoid adding empty or duplicate commands.
            if line and line not in seen_commands:
                seen_commands.add(line)
                commands.append(line)
            
            if len(commands) >= COMMAND_LIMIT:
                break
        
        return commands

    except Exception as e:
        print(f"❌ Error reading history file: {e}")
        return []

def load_existing_commands(filename):
    """Loads commands from the JSON file if it exists."""
    if not os.path.exists(filename):
        return [], set()
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        # Create a set of command strings for quick lookups.
        existing_command_set = {item['command'] for item in data}
        print(f"✅ Loaded {len(data)} existing commands from {filename}")
        return data, existing_command_set
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Could not read or parse {filename}. Starting fresh. Error: {e}")
        return [], set()

def save_commands(filename, new_commands, existing_data):
    """Saves the combined list of new and existing commands to the JSON file."""
    for command in new_commands:
        # Structure the new command entry.
        entry = {
            "id": str(uuid.uuid4()),
            "command": command,
            "description": "",
            "tags": [],
            "last_run": None
        }
        existing_data.append(entry)
    
    try:
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"\n✅ Successfully saved {len(new_commands)} new command(s) to {filename}")
    except IOError as e:
        print(f"\n❌ Error saving to {filename}: {e}")


def main():
    """Main function to run the TUI and handle file operations."""
    d = Dialog(dialog="dialog", autowidgetsize=True)
    d.set_background_title("Project Command Collector")

    file_path, shell_type = get_history_file_path()

    if not file_path:
        d.msgbox("Could not find a supported history file (.zsh_history, .bash_history) in your home directory.")
        os.system('clear') # Clear screen after msgbox
        return

    commands = parse_history(file_path, shell_type)
    if not commands:
        d.msgbox("No commands found or unable to parse history file.")
        os.system('clear') # Clear screen after msgbox
        return

    # Load commands that have already been saved to avoid showing them.
    existing_data, existing_command_set = load_existing_commands(OUTPUT_FILENAME)

    # Filter out commands that are already in our JSON file.
    filtered_commands = [cmd for cmd in commands if cmd not in existing_command_set]

    if not filtered_commands:
        d.msgbox(f"No new commands found in your recent history. All recent commands are already in {OUTPUT_FILENAME}.")
        os.system('clear') # Clear screen after msgbox
        return

    # Reverse the filtered_commands list to display newest first in the TUI
    filtered_commands.reverse()

    # Format for the checklist: (tag, item, status)
    choices = [(cmd, "", "off") for cmd in filtered_commands]

    code, selected_commands = d.checklist(
        "Use SPACE to select commands you wish to save for this project. Press ENTER when done.",
        choices=choices,
        title="Select New Commands from History",
        height=30,
        width=100
    )

    os.system('clear') # Clear the screen immediately after the dialog box closes

    if code == d.OK:
        if selected_commands:
            save_commands(OUTPUT_FILENAME, selected_commands, existing_data)
        else:
            print("\nNo commands were selected. Operation cancelled.")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()