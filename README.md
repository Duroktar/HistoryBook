# History Book

History Book is a command-line tool designed to help you organize and manage your frequently used shell commands for specific projects. It allows you to scrape commands from your shell history, add descriptions and tags, and then easily view, edit, and re-run them from a simple text-based user interface (TUI).

The tool integrates with your `bash` or `zsh` history to provide a streamlined way to keep track of project-specific commands without cluttering your global history or relying on external notes.

## Features

* **Scrape Commands:** Pull recent commands directly from your shell history.
* **Organize:** Add descriptions and tags to your saved commands for better organization.
* **Edit:** Modify existing command entries, including their descriptions and tags.
* **Run:** Select and execute saved commands directly from the TUI.
* **History Synchronization:** Optional shell configuration to ensure your history file is always up-to-date.
* **Version Tracking:** Easily check the current version of the tool.
* **Changelog Access:** View the project's development history directly from the CLI.

## Installation

To install History Book, simply run the `install.sh` script in the project directory:

```bash
./install.sh
```

The installer will:
1.  Check for necessary system dependencies (`python3`, `whiptail`).
2.  Set up a Python virtual environment.
3.  Install required Python packages (including `whiptail-dialogs`).
4.  Create a launcher script.
5.  Create a symbolic link (`history_book`) in `~/.local/bin` for easy access.
6.  *Optionally*, configure your shell (`.bashrc` or `.zshrc`) to save history instantly.

**Note:** If `~/.local/bin` is not in your `PATH`, the installer will provide instructions on how to add it. You may need to restart your terminal or `source` your shell profile file (`~/.bashrc` or `~/.zshrc`) for changes to take effect.

## Uninstallation

To remove History Book and revert its changes, run the `uninstall.sh` script:

```bash
./uninstall.sh
```

The uninstaller will:
1.  Prompt for confirmation before proceeding.
2.  Remove the symbolic link and launcher script.
3.  Delete the Python virtual environment.
4.  *Attempt to revert* the shell history configuration changes made by the installer (if applied).

**Important:** The `project_commands.json` file, which contains your saved commands, is **not** removed by the uninstaller. You will need to delete this file manually if you no longer need your command data.

## Usage

Once installed, you can use the `history_book` command from anywhere in your terminal.

### 1. `history_book add`

Interactively adds new commands from your shell history to your project's collection. For each selected command, you'll be prompted for a short name, description, tags, and whether it should run quietly by default.

```bash
history_book add
```

### 2. `history_book list`

Prints all saved commands to your terminal, formatted for readability. You can optionally filter the list by tags.

```bash
history_book list
# Example with tag filtering (case-insensitive, comma-separated)
history_book list --tags "build,docker"
```

### 3. `history_book run <name>`

Executes a saved command by its short name.

```bash
history_book run my_command_name
```

You can also suppress History Book's own output (e.g., "Running:" messages) for a specific execution using the `--quiet` flag:

```bash
history_book run my_command_name --quiet
```

Commands can also be configured to run quietly by default using the `edit` command.

### 4. `history_book edit`

Interactively edit properties (name, description, tags, quiet status) of an existing saved command.

```bash
history_book edit
```

### 5. `history_book version`

Displays the current version of the History Book tool.

```bash
history_book version
```

### 6. `history_book changelog`

Displays the project's changelog, showing development history and updates.

```bash
history_book changelog
	