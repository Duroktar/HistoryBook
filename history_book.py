#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# --- MODIFICATION START ---
# Import Whiptail for TUI interactions in history_book.py itself
from whiptail import Whiptail
# --- MODIFICATION END ---

# --- Configuration ---
COMMANDS_FILE = "project_commands.json"
# The script for adding new commands (the one we built previously)
# This script will now output selected commands as JSON to stdout
ADD_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'scrape_history.py')

# --- Helper Functions ---

def load_commands_data():
    """Loads and returns the commands from the JSON file.
    Ensures default fields for older entries."""
    if not os.path.exists(COMMANDS_FILE):
        return []
    try:
        with open(COMMANDS_FILE, 'r') as f:
            data = json.load(f)
        # Ensure all expected fields exist with defaults for backward compatibility
        for item in data:
            if 'id' not in item:
                item['id'] = str(uuid.uuid4()) # Add ID if missing
            if 'name' not in item:
                item['name'] = "" # Commands added before 'name' existed
            if 'description' not in item:
                item['description'] = ""
            if 'tags' not in item:
                item['tags'] = []
            if 'last_run' not in item:
                item['last_run'] = None
            if 'quiet' not in item:
                item['quiet'] = False
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read or parse '{COMMANDS_FILE}': {e}")
        sys.exit(1)

def save_commands_data(data):
    """Saves the list of commands to the JSON file."""
    try:
        with open(COMMANDS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Successfully saved/updated commands to {COMMANDS_FILE}")
    except IOError as e:
        print(f"❌ Error saving to {COMMANDS_FILE}: {e}")

def update_last_run(command_id): # Changed to use command ID for robustness
    """Updates the 'last_run' timestamp for a command by its ID."""
    all_commands = load_commands_data()
    command_found = False
    for cmd in all_commands:
        if cmd.get('id') == command_id: # Match by ID
            cmd['last_run'] = datetime.utcnow().isoformat() + "Z"
            command_found = True
            break
            
    if command_found:
        save_commands_data(all_commands) # Use the new save function
    else:
        print(f"Warning: Could not find command with ID '{command_id}' to update last_run timestamp.")


# --- Command Functions ---

def list_commands(args):
    """Handles the 'list' command, including tag filtering."""
    commands = load_commands_data() # Use new load function
    
    # Prepare tags for case-insensitive comparison
    filter_tags = set(tag.lower() for tag in args.tags.split(',')) if args.tags else None

    print("\n--- Project Commands ---\n")
    
    commands_to_display = []
    for cmd in commands:
        if filter_tags:
            # Case-insensitive check for tag intersection
            command_tags = set(t.lower() for t in cmd.get('tags', []))
            if not filter_tags.intersection(command_tags):
                continue # Skip if no tags match
            
        commands_to_display.append(cmd)

    if not commands_to_display:
        print("No commands found matching the specified criteria.")
        return

    for cmd in commands_to_display:
        name_part = f"  \033[1;33m{cmd.get('name', 'N/A')}\033[0m" # Yellow and Bold
        tags_part = f"\033[0;34m{cmd.get('tags', [])}\033[0m" # Blue
        
        # --- MODIFICATION START ---
        # Ensure 'command' is always present, even if empty string
        command_text = cmd.get('command', '') 
        description_text = cmd.get('description', '')
        quiet_status = " (Quiet)" if cmd.get('quiet', False) else ""

        print(f"{name_part.ljust(30)} {tags_part}")
        print(f"  └─ \033[0;32m{command_text}\033[0m") # Green
        if description_text:
            print(f"     \033[2;37m{description_text}{quiet_status}\033[0m") # Dim White, include quiet status here
        elif quiet_status: # If no description but quiet status exists
             print(f"     \033[2;37m{quiet_status.strip()}\033[0m")
        print("-" * 20)
        # --- MODIFICATION END ---

def run_command(args):
    """Handles the 'run' command."""
    commands = load_commands_data() # Use new load function
    command_to_run_entry = None
    
    for cmd_entry in commands: # Iterate through full entries
        if cmd_entry.get('name') == args.name:
            command_to_run_entry = cmd_entry
            break
            
    if command_to_run_entry:
        # --- MODIFICATION START ---
        # Determine effective quiet mode for this command
        effective_quiet = args.quiet or command_to_run_entry.get('quiet', False)
        
        if not effective_quiet:
            print(f"Running '{args.name}': \033[1;32m{command_to_run_entry['command']}\033[0m\n")
        try:
            # Using subprocess.run is safer and more modern
            subprocess.run(command_to_run_entry['command'], shell=True, check=True)
            if not effective_quiet:
                print(f"\n✅ Command '{args.name}' completed successfully.")
            update_last_run(command_to_run_entry['id']) # Update timestamp on successful run by ID
        except subprocess.CalledProcessError as e:
            # Always print error messages, even in quiet mode
            print(f"\n❌ Error: Command '{args.name}' failed with exit code {e.returncode}.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        # --- MODIFICATION END ---
    else:
        print(f"Error: No command with the name '{args.name}' found.")

def add_commands(args):
    """Handles the 'add' command by calling the scraper script."""
    print("Launching the command selection interface...")
    try:
        # --- MODIFICATION START ---
        # Capture stdout from scrape_history.py
        result = subprocess.run([sys.executable, ADD_SCRIPT_PATH], capture_output=True, text=True, check=True)
        # scrape_history.py will print the JSON of new commands to stdout
        new_commands_json = result.stdout.strip()

        if new_commands_json:
            new_entries = json.loads(new_commands_json)
            if new_entries:
                current_commands = load_commands_data()
                current_commands.extend(new_entries)
                save_commands_data(current_commands)
                print(f"✅ Added {len(new_entries)} new command(s).")
            else:
                print("No new commands selected to add.")
        else:
            print("No commands returned from the selection interface.")
        # --- MODIFICATION END ---

    except FileNotFoundError:
        print(f"Error: The scraper script '{ADD_SCRIPT_PATH}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON output from scraper script. Output:\n{new_commands_json}")
    except subprocess.CalledProcessError as e:
        print(f"The 'add' process was cancelled or failed. Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")


# --- NEW: Edit Commands Function ---
def edit_commands(args):
    """Handles the 'edit' command, allowing modification of saved commands."""
    w = Whiptail(title="History Book", backtitle="Edit Commands")
    commands_data = load_commands_data()

    if not commands_data:
        w.msgbox(f"No commands found in {COMMANDS_FILE} to edit.")
        return

    # Create a menu of commands: (tag, item) for whiptail
    # We use the index as the tag, and the command name as the item.
    menu_choices = [(str(i), item.get('name', item['command'])) for i, item in enumerate(commands_data)]

    tag_str, exit_code = w.menu(
        "Select a command to edit:",
        menu_choices
    )

    if exit_code == 0: # 0 indicates OK/Yes in whiptail
        try:
            selected_index = int(tag_str)
            selected_command_entry = commands_data[selected_index]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return

        # Edit Name
        new_name, code_name = w.inputbox(
            f"Edit short name for: {selected_command_entry['command']}",
            default=selected_command_entry.get('name', '')
        )
        if code_name == 0: # OK
            selected_command_entry['name'] = new_name.strip()

        # Edit Description
        new_description, code_desc = w.inputbox(
            f"Edit description for: {selected_command_entry['command']}",
            default=selected_command_entry.get('description', '')
        )
        if code_desc == 0: # OK
            selected_command_entry['description'] = new_description

        # Edit Tags (as comma-separated string)
        current_tags_str = ", ".join(selected_command_entry.get('tags', []))
        new_tags_str, code_tags = w.inputbox(
            f"Edit tags for: {selected_command_entry['command']} (comma-separated)",
            default=current_tags_str
        )
        if code_tags == 0: # OK
            selected_command_entry['tags'] = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
            
        # Option to toggle quiet mode
        quiet_status = "ON" if selected_command_entry.get('quiet', False) else "OFF"
        prompt_text = (
            f"Set command '{selected_command_entry.get('name', selected_command_entry['command'])}' to run quietly?\n\n"
            f"Current status: {quiet_status}\n\n"
            "Select 'Yes' to suppress output\n  (e.g., 'Running:' messages)'.\n\n"
            "Select 'No' to show all output."
        )
        code_quiet = w.yesno(prompt_text) 
        
        if code_quiet: # True means Yes was selected
            selected_command_entry['quiet'] = True
        else: # False means No was selected (or ESC/Cancel, which defaults to False)
            selected_command_entry['quiet'] = False

        save_commands_data(commands_data)
    else:
        print("\nCommand selection cancelled.")


# --- Main Argument Parser ---

def main():
    parser = argparse.ArgumentParser(
        description="History Book: A tool to manage and run project-specific shell commands."
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Sub-parser for the 'add' command
    parser_add = subparsers.add_parser('add', help='Interactively add new commands from your shell history.')
    parser_add.set_defaults(func=add_commands)

    # Sub-parser for the 'list' command
    parser_list = subparsers.add_parser('list', help='List all saved commands, with optional tag filtering.')
    parser_list.add_argument(
        '--tags', 
        type=str, 
        help='A comma-separated list of tags to filter by (e.g., "build,docker").'
    )
    parser_list.set_defaults(func=list_commands)

    # Sub-parser for the 'run' command
    parser_run = subparsers.add_parser('run', help='Run a saved command by its short name.')
    parser_run.add_argument('name', type=str, help='The short name of the command to execute.')
    # --- MODIFICATION START ---
    # Add --quiet flag to the run command
    parser_run.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress History Book\'s own output (e.g., "Running:" messages) for this execution.'
    )
    # --- MODIFICATION END ---
    parser_run.set_defaults(func=run_command)

    # --- NEW: Sub-parser for the 'edit' command ---
    parser_edit = subparsers.add_parser('edit', help='Interactively edit properties of a saved command.')
    parser_edit.set_defaults(func=edit_commands)
    # --- END NEW ---

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
