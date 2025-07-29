# History Book

History Book is a command-line tool designed to help you organize and manage your frequently used shell commands for specific projects. It allows you to scrape commands from your shell history, add descriptions and tags, and then easily view, edit, and re-run them from a simple text-based user interface (TUI).

The tool integrates with your `bash` or `zsh` history to provide a streamlined way to keep track of project-specific commands without cluttering your global history or relying on external notes.

## Features

* **Scrape Commands:** Pull recent commands directly from your shell history.
* **Organize:** Add descriptions and tags to your saved commands for better organization.
* **Edit:** Modify existing command entries, including their descriptions and tags.
* **Run:** Select and execute saved commands directly from the TUI.
* **History Synchronization:** Optional shell configuration to ensure your history file is always up-to-date.

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

### 1. Scrape New Commands (Default Action)

This is the primary way to add new commands to your project's collection. It will display a list of recent, unique commands from your shell history that are not yet saved.

```bash
history_book
# or explicitly
history_book scrape
```

A `whiptail` checklist will appear, allowing you to select commands to save.

### 2. View and Edit Saved Commands

Use this command to open a menu of your currently saved commands. You can then select a command to add or modify its description and tags.

```bash
history_book edit
```

A `whiptail` menu will appear to select a command, followed by input boxes for editing.

### 3. Select and Run Saved Commands

This command presents a list of all your saved commands (including their descriptions and tags). You can select one or more commands to execute them directly.

```bash
history_book run
```

A `whiptail` checklist will appear, allowing you to select commands to run. The selected commands will be executed in your current shell.
