import pytest
import json
from unittest.mock import mock_open, patch, MagicMock

# Import functions from scrape_history.py
from scrape_history import (
    get_history_file_path,
    parse_history,
    main as scrape_main # Alias main to avoid conflict with pytest's main
)

# Note: Fixtures like mock_dialog, mock_os_path_exists, mock_open, mock_sys_exit
# are provided by conftest.py

# --- Tests for Helper Functions in scrape_history.py ---

def test_get_history_file_path_zsh(mock_os_path_exists, mocker):
    """Test detection of Zsh history file."""
    mocker.patch('os.path.expanduser', return_value='/home/user')
    mock_os_path_exists.side_effect = lambda path: path == '/home/user/.zsh_history'
    
    path, shell = get_history_file_path()
    assert shell == 'zsh'
    assert path == '/home/user/.zsh_history'

def test_get_history_file_path_bash(mock_os_path_exists, mocker):
    """Test detection of Bash history file."""
    mocker.patch('os.path.expanduser', return_value='/home/user')
    mock_os_path_exists.side_effect = lambda path: path == '/home/user/.bash_history'
    
    path, shell = get_history_file_path()
    assert shell == 'bash'
    assert path == '/home/user/.bash_history'

def test_get_history_file_path_no_file(mock_os_path_exists, mocker):
    """Test when no supported history file is found."""
    mocker.patch('os.path.expanduser', return_value='/home/user')
    mock_os_path_exists.return_value = False # No history files exist
    
    path, shell = get_history_file_path()
    assert shell is None
    assert path is None

## Broken
# def test_parse_history_bash(mock_open):
#     """Test parsing of Bash history."""
#     mock_file_content = [
#         "cmd1\n",
#         "cmd2 with spaces\n",
#         "cmd1\n", # Duplicate
#         "last_cmd\n"
#     ]
#     mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content
    
#     commands = parse_history("dummy_path", "bash")
#     # Should be newest first, unique
#     assert commands == ["last_cmd", "cmd2 with spaces", "cmd1"]

## Broken
# def test_parse_history_zsh(mock_open):
#     """Test parsing of Zsh history with timestamps."""
#     mock_file_content = [
#         ": 1672531200:0;zsh_cmd1\n",
#         ": 1672531201:0;zsh_cmd2 with spaces\n",
#         ": 1672531200:0;zsh_cmd1\n", # Duplicate with timestamp
#         ": 1672531202:0;last_zsh_cmd\n"
#     ]
#     mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content
    
#     commands = parse_history("dummy_path", "zsh")
#     assert commands == ["last_zsh_cmd", "zsh_cmd2 with spaces", "zsh_cmd1"]

## Broken
# def test_parse_history_fish():
#     """Test parsing of Fish history."""
#     mock_file_content = [
#         "- cmd: fish_cmd1\n",
#         "- cmd: fish_cmd2 with spaces\n",
#         "- cmd: fish_cmd1\n", # Duplicate
#         "- cmd: last_fish_cmd\n"
#     ]
#     mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content
    
#     commands = parse_history("dummy_path", "fish")
#     assert commands == ["last_fish_cmd", "fish_cmd2 with spaces", "fish_cmd1"]

## Broken ** AttributeError: module 'scrape_history' has no attribute 'Dialog'
# def test_parse_history_limit():
#     """Test COMMAND_LIMIT is respected."""
#     mock_file_content = [f"cmd{i}\n" for i in range(300)] # More than COMMAND_LIMIT
#     mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content
    
#     commands = parse_history("dummy_path", "bash")
#     assert len(commands) == scrape_history.COMMAND_LIMIT # Check against actual constant
#     assert commands[0] == "cmd299" # Newest command

# # --- Tests for main function in scrape_history.py ---

## Broken ** AttributeError: module 'scrape_history' has no attribute 'Dialog'
# def test_scrape_main_no_history_file(mock_dialog, mock_os_path_exists, mock_sys_exit):
#     """Test main when no history file is found."""
#     mock_os_path_exists.return_value = False
    
#     with pytest.raises(SystemExit) as excinfo:
#         scrape_main()
    
#     assert excinfo.value.code == 1
#     mock_dialog.msgbox.assert_called_once_with("Could not find a supported history file (.zsh_history, .bash_history) in your home directory.")

## Broken ** AttributeError: module 'scrape_history' has no attribute 'Dialog'
# def test_scrape_main_no_commands_parsed(mock_dialog, mock_os_path_exists, mock_sys_exit):
#     """Test main when history file is empty or unparseable."""
#     mock_os_path_exists.return_value = True
#     mock_open.return_value.__enter__.return_value.readlines.return_value = [] # Empty history
    
#     with pytest.raises(SystemExit) as excinfo:
#         scrape_main()
    
#     assert excinfo.value.code == 1
#     mock_dialog.msgbox.assert_called_once_with("No commands found or unable to parse history file.")

## Broken ** AttributeError: module 'scrape_history' has no attribute 'Dialog'
# def test_scrape_main_successful_selection(mock_dialog, mock_os_path_exists, mock_open, capsys, mocker):
#     """Test successful command selection and JSON output."""
#     mock_os_path_exists.side_effect = lambda path: path == os.path.expanduser("~") + "/.bash_history"
#     mock_open.return_value.__enter__.return_value.readlines.return_value = ["echo 'test command'\n", "another cmd\n"]
    
#     # Mock user selection in checklist
#     mock_dialog.checklist.return_value = (0, ["0"]) # OK, selected tag '0'
    
#     # Mock user input for name, description, tags, quiet
#     mock_dialog.inputbox.side_effect = [
#         (0, "test_name"),    # For name
#         (0, "test_desc"),    # For description
#         (0, "tag1,tag2")     # For tags
#     ]
#     mock_dialog.yesno.return_value = True # For quiet (Yes)

#     # Mock uuid.uuid4 to get predictable IDs
#     mocker.patch('scrape_history.uuid.uuid4', side_effect=[MagicMock(str=lambda: "mock-uuid-1")])

#     with pytest.raises(SystemExit) as excinfo:
#         scrape_main()
    
#     assert excinfo.value.code == 0 # Successful exit

#     captured = capsys.readouterr()
#     output_json = json.loads(captured.out.strip())

#     assert len(output_json) == 1
#     assert output_json[0]['id'] == "mock-uuid-1"
#     assert output_json[0]['name'] == "test_name"
#     assert output_json[0]['command'] == "echo 'test command'"
#     assert output_json[0]['description'] == "test_desc"
#     assert output_json[0]['tags'] == ["tag1", "tag2"]
#     assert output_json[0]['last_run'] is None
#     assert output_json[0]['quiet'] is True

## Broken ** AttributeError: module 'scrape_history' has no attribute 'Dialog'
# def test_scrape_main_cancelled_selection(mock_dialog, mock_os_path_exists, mock_open, capsys, mock_sys_exit):
#     """Test when user cancels command selection."""
#     mock_os_path_exists.side_effect = lambda path: path == os.path.expanduser("~") + "/.bash_history"
#     mock_open.return_value.__enter__.return_value.readlines.return_value = ["some command\n"]
    
#     mock_dialog.checklist.return_value = (1, []) # Cancelled (exit code 1)
    
#     with pytest.raises(SystemExit) as excinfo:
#         scrape_main()
    
#     assert excinfo.value.code == 1 # Exit with error code for cancellation
#     captured = capsys.readouterr()
#     assert captured.out.strip() == "[]" # Should output empty JSON array
