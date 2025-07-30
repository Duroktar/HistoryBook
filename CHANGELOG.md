# Changelog

## [0.2.0] - 2025-07-30

### Added

* **Project Website:** Initial public webpage for the History Book application, hosted on GitHub Pages.
  * Includes a compelling product hook, detailed features, installation guide, and usage examples.
  * Incorporates support blurb with Ko-fi and GitHub repository links.
* **Application Logo:** Finalized "The Indexed Scroll" SVG logo.
  * Features an aged paper background.
  * Utilizes a split title design with a prominent 'H' on the scroll and "istory Book" beside it, using a classic serif font and a muted green color.

### Fixed

* **Testing Infrastructure:** Addressed persistent "Fixture 'mock_open' called directly" errors.
  * Refined `mock_open` fixture in `conftest.py` to correctly patch `builtins.open` using `pytest-mock`'s `mocker`.
  * Removed `autouse=True` from `mock_open` to prevent conflicts with other fixtures.
  * Cleaned up extraneous non-Python content that was causing parsing issues in `conftest.py`.
  * Updated relevant test function signatures to explicitly request the `mock_open` fixture.
* **Scraper Script (`scrape_history.py`):**
  * Corrected `whiptail.checklist` positional arguments (`height`, `width`) to resolve TUI display issues.
  * Integrated `argparse` for `--output-file` to ensure proper data transfer from the subprocess.
* **Website Content:**
  * Replaced all raw Markdown formatting characters (e.g., `**`, `` ` ``) with proper HTML tags (`<strong>`, `<code>`) for correct rendering.
  * Updated footer copyright information and removed version display.

## [0.1.0] - 2025-07-29

### Added

* Initial core functionality for History Book.
* `history_book add`: Interactively scrapes and saves commands from shell history.
* `history_book list`: Lists saved commands with descriptions, tags, and coloring.
* `history_book run`: Executes saved commands by name.
* `history_book edit`: Interactively edits saved command properties.
* Support for `whiptail` TUI library.
* Per-command and global `--quiet` options for `run` command.
* Basic `install.sh` and `uninstall.sh` scripts.

### Fixed

* Resolved `whiptail` issue where commands with spaces were split during selection/execution.
* Corrected `whiptail.inputbox` parameter from `default_item` to `default`.
* Refined `edit_commands` `yesno` dialog logic and prompt text.
* Adjusted `list` and `run` command output formatting for better readability.


## [0.1.0] - 2025-07-29

### Added

* Initial core functionality for History Book.

* `history_book add`: Interactively scrapes and saves commands from shell history.

* `history_book list`: Lists saved commands with descriptions, tags, and coloring.

* `history_book run`: Executes saved commands by name.

* `history_book edit`: Interactively edits saved command properties.

* Support for `whiptail` TUI library.

* Per-command and global `--quiet` options for `run` command.

* Basic `install.sh` and `uninstall.sh` scripts.

### Fixed

* Resolved `whiptail` issue where commands with spaces were split during selection/execution.

* Corrected `whiptail.inputbox` parameter from `default_item` to `default`.

* Refined `edit_commands` `yesno` dialog logic and prompt text.

* Adjusted `list` and `run` command output formatting for better readability.

# Recent Updates to History Book

---

## Core Architecture & CLI

* **Centralized CLI (`history_book.py`):** The primary script was refactored to use `argparse`, becoming the central command-line interface for all History Book operations (`add`, `list`, `run`, `edit`).
* **Dedicated Scraper (`scrape_history.py`):** The original scraping logic was moved to a separate script, which now solely focuses on interactively selecting commands from history and outputting them as a JSON array to standard output. This output is then consumed by `history_book.py`.
* **Robust Data Handling:**
    * Introduced `id` fields for unique command identification.
    * Improved `load_commands_data` to ensure all necessary fields (`id`, `name`, `description`, `tags`, `last_run`, `quiet`) are present with default values when loading existing data, ensuring backward compatibility.
    * Updated `update_last_run` to use the command's unique `id` for more reliable timestamp updates.

---

## TUI & User Experience

* **Transition to `whiptail`:** The interactive text-based user interface (TUI) was fully migrated from `dialog` to `whiptail` for a cleaner, more modern look and feel.
    * Updated `install.sh` and `uninstall.sh` to check for `whiptail` and install `whiptail-dialogs`.
    * All TUI calls in both `history_book.py` and `scrape_history.py` were adapted to the `whiptail-dialogs` Python library's API, including adjusting parameter names and return value handling.
    * Removed explicit screen clearing (`os.system('clear')`) as `whiptail` handles this natively.
* **Improved Command Selection:** For `scrape_commands` and `run_commands`, the `whiptail` checklist now uses numerical indices as internal tags. This prevents `whiptail` from incorrectly splitting command strings that contain spaces when they are selected.

---

## New Commands & Functionality

* **`history_book add`:**
    * Launches the `scrape_history.py` interface.
    * For each selected command, it now interactively prompts the user for a **short name**, a **description**, **comma-separated tags**, and whether the command should run **quietly by default**.
* **`history_book list`:**
    * A new command to print all saved commands directly to standard output.
    * **Concise and Formatted Output:** Each command is displayed on its own line, prefixed with `$` for clarity.
    * **Rich Metadata Display:** Shows the command's `name`, `tags`, `command` string, `description`, and indicates if it's set to run `(Quiet)` by default.
    * **ANSI Color Coding:** Utilizes ANSI escape codes for enhanced readability, applying colors to names, tags, commands, and descriptions.
    * **Tag Filtering:** Supports the `--tags` flag to filter the displayed list by one or more comma-separated tags (case-insensitive).
* **`history_book run <name>`:**
    * Executes a saved command by its short name.
    * **Global Quiet Flag:** Added a `--quiet` flag to suppress History Book's own output (e.g., "🚀 Running:" messages) for a specific execution.
    * **Per-Command Quiet Option:** Commands can now be marked as `quiet: true` in `project_commands.json` via the `edit` command, causing them to suppress History Book's output by default when run. Error messages are always shown, regardless of quiet mode.
* **`history_book edit`:**
    * A new interactive command to modify properties of existing saved commands.
    * Allows editing a command's `name`, `description`, `tags`, and its `quiet` status using `whiptail` input boxes and a `yesno` dialog.
    * The `yesno` dialog for the `quiet` option now includes a more detailed explanation of its effect.