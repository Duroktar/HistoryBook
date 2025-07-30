import pytest
import os
import json
import sys
from unittest.mock import Mock, patch, mock_open

# Add the project root to sys.path so pytest can find history_book and scrape_history
# This assumes conftest.py is in 'tests/' and the main scripts are in the parent directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, PROJECT_ROOT)

# Now import the modules after modifying sys.path
import history_book
import scrape_history

@pytest.fixture
def temp_commands_file(tmp_path):
    """
    Fixture to create a temporary project_commands.json file for tests.
    It also patches the COMMANDS_FILE path in history_book.py
    to point to this temporary file.
    """
    original_commands_file_path = history_book.COMMANDS_FILE
    temp_file = tmp_path / original_commands_file_path
    
    # Ensure the parent directory for the temp file exists if COMMANDS_FILE
    # was originally in a subdirectory.
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    # Patch the module-level variable in history_book.py
    history_book.COMMANDS_FILE = str(temp_file)

    # Clean up any existing content in the temp file
    if temp_file.exists():
        temp_file.unlink()

    yield temp_file # Provide the path to the temporary file to the test

    # Teardown: Restore the original COMMANDS_FILE path
    history_book.COMMANDS_FILE = original_commands_file_path
    # Clean up the temporary file after the test
    if temp_file.exists():
        temp_file.unlink()

@pytest.fixture
def mock_whiptail():
    """Fixture to provide a mocked Whiptail instance."""
    mock_w = Mock(spec=history_book.Whiptail)
    # Default return values for common methods
    mock_w.msgbox.return_value = None
    mock_w.inputbox.return_value = ("", 0) # default_item, exit_code (OK)
    mock_w.menu.return_value = ("", 0) # tag, exit_code (OK)
    mock_w.checklist.return_value = ([], 0) # selected_tags, exit_code (OK)
    mock_w.yesno.return_value = False # Default to 'No' for yesno
    return mock_w

@pytest.fixture
def mock_dialog():
    """Fixture to provide a mocked Dialog instance for scrape_history.py."""
    mock_d = Mock(spec=scrape_history.Dialog)
    # Default return values for common methods
    mock_d.msgbox.return_value = None
    mock_d.inputbox.return_value = (0, "") # code (OK), text
    mock_d.checklist.return_value = (0, []) # code (OK), selected_items
    # Dialog's OK constant
    mock_d.OK = 0
    return mock_d

@pytest.fixture(autouse=True)
def mock_subprocess_run():
    """
    Fixture to mock subprocess.run globally.
    Tests can configure its behavior using mock_subprocess_run.return_value
    or mock_subprocess_run.side_effect.
    """
    with patch('subprocess.run') as mock_run:
        yield mock_run

@pytest.fixture(autouse=True)
def mock_os_path_exists():
    """
    Fixture to mock os.path.exists globally.
    Tests can configure its behavior using mock_os_path_exists.return_value
    or mock_os_path_exists.side_effect.
    """
    with patch('os.path.exists') as mock_exists:
        yield mock_exists

@pytest.fixture # Removed autouse=True here
def mock_open(mocker): # Add mocker fixture as a dependency
    """
    Fixture to mock the built-in open function globally.
    This allows simulating file reads/writes without actual disk I/O.
    """
    # Patch builtins.open directly using mocker.patch with new_callable=mock_open.
    # mocker.patch returns the mock object that replaces 'open'.
    mock_file_open_func = mocker.patch('builtins.open', new_callable=mock_open)
    
    # Configure the mock file handle that mock_file_open_func will return when called.
    # This is the object that represents the file itself within the 'with open(...) as f:' block.
    mock_file_open_func.return_value.readlines.return_value = [] # Default readlines to empty list
    mock_file_open_func.return_value.read.return_value = "" # Default read to empty string

    yield mock_file_open_func # Yield the mock for the 'open' function itself

@pytest.fixture(autouse=True)
def mock_sys_exit():
    """
    Fixture to mock sys.exit to prevent tests from actually exiting.
    Instead, it raises SystemExit.
    """
    with patch('sys.exit') as mock_exit:
        yield mock_exit

@pytest.fixture(autouse=True)
def mock_sys_stdout_stderr():
    """
    Fixture to capture sys.stdout and sys.stderr.
    Use capsys fixture from pytest for capturing output.
    This fixture ensures sys.stdout and sys.stderr are not mocked by default
    by other fixtures, allowing capsys to work.
    """
    pass # No need to do anything here, just ensures it's auto-used
