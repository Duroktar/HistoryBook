#!/usr/bin/env python3

import os
import re
import json
import uuid
import sys
import datetime
import subprocess

from whiptail import Whiptail

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
    commands = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
        
        seen_commands = set()
        
        for line in reversed(lines):
            original_stripped_line = line.strip()
            processed_line = original_stripped_line
            if not processed_line:
                continue
            
            # Zsh specific processing
            if shell_type == "zsh":
                processed_line = re.sub(r'^: \d+:\d+;', '', processed_line)
            
            # Fish specific processing
            if shell_type == "fish" and processed_line.startswith('- cmd: '):
                processed_line = processed_line[7:]

            # Avoid adding empty or duplicate commands.
            if processed_line and processed_line not in seen_commands:
                seen_commands.add(processed_line)
                commands.append(processed_line)
            
            if len(commands) >= COMMAND_LIMIT:
                break
        
        return commands

    except Exception as e:
        print(f"❌ Error reading history file: {e}")
        return []

def load_commands_data(filename):
    """Loads commands from the JSON file if it exists."""
    if not os.path.exists(filename):
        return [], set()
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        # Ensure 'tags' and 'last_run' exist for older entries
        for item in data:
            if 'tags' not in item:
                item['tags'] = []
            if 'description' not in item:
                item['description'] = ""
            if 'last_run' not in item:
                item['last_run'] = None
        # Create a set of command strings for quick lookups.
        existing_command_set = {item['command'] for item in data}
        print(f"✅ Loaded {len(data)} existing commands from {filename}")
        return data, existing_command_set
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Could not read or parse {filename}. Starting fresh. Error: {e}")
        return [], set()

def save_commands_data(filename, data):
    """Saves the combined list of new and existing commands to the JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Successfully saved/updated commands to {filename}")
    except IOError as e:
        print(f"\n❌ Error saving to {filename}: {e}")

# --- SCRAPE COMMANDS ---
def scrape_commands(w: Whiptail):
    """Function to scrape new commands from shell history."""
    file_path, shell_type = get_history_file_path()

    if not file_path:
        w.msgbox("Could not find a supported history file (.zsh_history, .bash_history) in your home directory.")
        return

    commands = parse_history(file_path, shell_type)
    if not commands:
        w.msgbox("No commands found or unable to parse history file.")
        return

    # Load commands that have already been saved to avoid showing them.
    existing_data, existing_command_set = load_commands_data(OUTPUT_FILENAME)

    # Filter out commands that are already in our JSON file.
    filtered_commands = [cmd for cmd in commands if cmd not in existing_command_set]

    if not filtered_commands:
        w.msgbox(f"No new commands found in your recent history. All recent commands are already in {OUTPUT_FILENAME}.")
        return

    # Create a dictionary to map a unique tag (index) back to the full command string
    # This prevents whiptail-dialogs from splitting tags containing spaces.
    command_map = {str(i): cmd for i, cmd in enumerate(filtered_commands)}
    
    # Format for the checklist: (tag, item, status) for whiptail
    # Tag is now the string representation of the index, item is the full command string for display
    choices = [(str(i), cmd, 'OFF') for i, cmd in enumerate(filtered_commands)]

    selected_tags, exit_code = w.checklist( # selected_tags will now be a list of string indices (e.g., ['0', '1'])
        "Use SPACE to select commands you wish to save for this project. Press ENTER when done.",
        choices # Pass choices directly as a list
    )
    
    if exit_code == 0: # 0 indicates OK/Yes in whiptail
        if selected_tags: # selected_tags now contains indices like ['0']
            new_entries = []
            for tag in selected_tags: # Iterate over the selected tags (indices)
                # Retrieve the full, correct command string using the map
                command_text = command_map[tag] 
                entry = {
                    "id": str(uuid.uuid4()),
                    "command": command_text, # This will now be the correctly retrieved full command
                    "description": "",
                    "tags": [],
                    "last_run": None
                }
                new_entries.append(entry)
            
            existing_data.extend(new_entries)
            save_commands_data(OUTPUT_FILENAME, existing_data)
        else:
            print("\nNo commands were selected. Operation cancelled.")
    else:
        print("\nOperation cancelled.")

# --- EDIT COMMANDS ---
def edit_commands(w: Whiptail):
    """Function to view and edit existing commands."""
    commands_data, _ = load_commands_data(OUTPUT_FILENAME)

    if not commands_data:
        w.msgbox(f"No commands found in {OUTPUT_FILENAME} to edit.")
        return

    # Create a menu of commands: (tag, item) for whiptail
    # We use the index as the tag, and the command as the item.
    menu_choices = [(str(i), item['command']) for i, item in enumerate(commands_data)]

    tag_str, exit_code = w.menu(
        "Select a command to edit its description and tags:",
        menu_choices # Pass choices directly as a list
    )

    if exit_code == 0: # 0 indicates OK/Yes in whiptail
        try:
            selected_index = int(tag_str)
            selected_command_entry = commands_data[selected_index]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return

        # Edit Description
        new_description, code_desc = w.inputbox(
            f"Edit description for: {selected_command_entry['command']}",
            default=selected_command_entry.get('description', '') # Corrected to default
        )

        if code_desc == 0: # 0 indicates OK/Yes in whiptail
            selected_command_entry['description'] = new_description

            # Edit Tags (as comma-separated string)
            current_tags_str = ", ".join(selected_command_entry.get('tags', []))
            new_tags_str, code_tags = w.inputbox(
                f"Edit tags for: {selected_command_entry['command']} (comma-separated)",
                default=current_tags_str # Corrected to default
            )

            if code_tags == 0: # 0 indicates OK/Yes in whiptail
                selected_command_entry['tags'] = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
                save_commands_data(OUTPUT_FILENAME, commands_data)
            else:
                print("\nTag editing cancelled. Description saved (if changed).")
        else:
            print("\nDescription editing cancelled. No changes saved.")
    else:
        print("\nCommand selection cancelled.")

# --- RUN COMMANDS ---
def run_commands(w: Whiptail):
    """Function to select and run commands from the project_commands.json."""
    commands_data, _ = load_commands_data(OUTPUT_FILENAME)

    if not commands_data:
        w.msgbox(f"No commands found in {OUTPUT_FILENAME} to run.")
        return

    # --- MODIFICATION START ---
    # Create a dictionary to map a unique tag (index) back to the full command string
    # This is crucial to prevent whiptail from splitting tags that contain spaces.
    command_map = {str(i): item['command'] for i, item in enumerate(commands_data)}

    # Prepare choices for checklist: (tag, item, status) for whiptail
    # Tag is now the string representation of the index, item is the full command string for display.
    choices = []
    for i, item in enumerate(commands_data):
        display_text = item['command']
        if item.get('description'):
            display_text += f" ({item['description']})"
        if item.get('tags'):
            display_text += f" [{', '.join(item['tags'])}]"
        # Use the numerical index as the tag
        choices.append((str(i), display_text, 'OFF')) 

    selected_tags, exit_code = w.checklist( # selected_tags will now be a list of string indices (e.g., ['0', '1'])
        "Use SPACE to select commands to run. Press ENTER to execute.",
        choices
    )

    if exit_code == 0 and selected_tags: # 0 indicates OK/Yes in whiptail
        print("\nExecuting selected commands:")
        for tag in selected_tags: # Iterate over the selected tags (indices)
            # Retrieve the full, correct command string using the map
            original_command = command_map[tag] 
            
            print(f"\n🚀 Running: {original_command}")
            try:
                # Execute the command in the shell
                subprocess.run(original_command, shell=True, check=True)
                # Update last_run timestamp
                for item in commands_data:
                    if item['command'] == original_command:
                        item['last_run'] = datetime.datetime.now().isoformat()
                        break
                print(f"✅ Command completed: {original_command}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Command failed with exit code {e.returncode}: {original_command}")
            except Exception as e:
                print(f"❌ An error occurred while running '{original_command}': {e}")
        
        save_commands_data(OUTPUT_FILENAME, commands_data)
        print("\nExecution complete.")
    else:
        print("\nNo commands selected for execution or operation cancelled.")
    # --- MODIFICATION END ---


# --- Main Dispatcher ---
def main():
    w = Whiptail(title="History Book", backtitle="Project Command Collector")

    # If no arguments, or 'scrape' (default action)
    if len(sys.argv) == 1 or sys.argv[1] == "scrape":
        scrape_commands(w)
    elif sys.argv[1] == "edit":
        edit_commands(w)
    elif sys.argv[1] == "run":
        run_commands(w)
    else:
        w.msgbox(f"Unknown command: '{sys.argv[1]}'\n\nUsage:\n  history_book [scrape] - Scrape new commands\n  history_book edit   - View and edit saved commands\n  history_book run    - Select and run saved commands")

if __name__ == "__main__":
    main()
