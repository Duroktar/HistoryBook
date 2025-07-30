# History Book Development Guide

This guide provides instructions for setting up your development environment and contributing to the History Book project.

---

## 1. Setting Up Your Development Environment

To get started with developing History Book, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/history-book.git # Replace with actual repo URL
    cd history-book
    ```

2.  **Run the Development Installer:**
    This script will create a Python virtual environment and install all necessary dependencies, including those required for testing.
    ```bash
    ./dev-install.sh
    ```

3.  **Activate the Virtual Environment:**
    You'll need to activate the virtual environment in each new terminal session where you plan to work on the project.
    ```bash
    source venv/bin/activate
    ```
    (To deactivate, simply run `deactivate`)

---

## 2. Running the Application

Once your environment is set up and activated, you can run the `history_book` commands directly from the project root:

```bash
python history_book.py add
python history_book.py list
python history_book.py run <command_name>
python history_book.py edit
```

---

## 3. Running Tests

History Book uses `pytest` for testing.

1.  **Run all tests:**
    You can now run all tests directly using the `run_tests.sh` script.
    ```bash
    ./run_tests.sh
    ```

2.  **Run specific tests:**
    You can also pass arguments to `run_tests.sh` which will be forwarded to `pytest`.
    ```bash
    ./run_tests.sh tests/test_history_book.py
    ./run_tests.sh tests/test_scrape_history.py::test_parse_history_bash
    ```

---

## 4. Contributing Guidelines

We welcome contributions to History Book! Please follow these guidelines:

* **Feature Branches:** Create a new branch for each feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
* **Code Style:** Adhere to existing code style. We follow PEP 8 for Python code.
* **Testing:** Write unit tests for new features and bug fixes. Ensure all existing tests pass before submitting.
* **Commit Messages:** Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for clear and consistent commit history. Examples:
    * `feat: Add new 'delete' command`
    * `fix: Resolve command splitting in run_commands`
    * `docs: Update README with new usage examples`
    * `refactor: Centralize data loading logic`
* **Changelog:**
    * When adding new features or fixing bugs, update the `CHANGELOG.md` file.
    * Add your changes under an "Unreleased" section or a new version heading if you are preparing a release.
    * Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
* **Versioning:**
    * The project version is stored in the `VERSION` file.
    * Update this file following [Semantic Versioning](https://semver.org/spec/v2.0.0.html) principles for new releases.
    * Typically, this is done as part of a release process, not for every small change.

---

## 5. Project Structure

* `history_book.py`: Main CLI application.
* `scrape_history.py`: Helper script for interactive history scraping.
* `project_commands.json`: Stores your saved commands (user data).
* `install.sh`: End-user installation script.
* `uninstall.sh`: End-user uninstallation script.
* `dev-install.sh`: Development environment setup script.
* `run_tests.sh`: Script to run project tests.
* `requirements.txt`: Application dependencies.
* `test_requirements.txt`: Development and testing dependencies.
* `VERSION`: Current project version number.
* `CHANGELOG.md`: Project change history.
* `DEVELOPMENT.md`: This guide.
* `tests/`: Directory containing all unit and integration tests.
    * `tests/conftest.py`: Pytest fixtures for test setup.
    * `tests/test_history_book.py`: Tests for `history_book.py`.
    * `tests/test_scrape_history.py`: Tests for `scrape_history.py`.