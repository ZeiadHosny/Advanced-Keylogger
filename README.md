# Advanced Keylogger with Command Line Detection

A Python-based keylogger system with a GUI interface and command line activity detection/flagging capabilities.

## Features

- Keyboard input monitoring
- Window title and process tracking
- Command line detection
- Suspicious command flagging
- Simple and intuitive GUI
- Log saving and clearing
- Flagged command management

## Installation

### Prerequisites

- Python 3.6 or higher
- Windows operating system

### Setup

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python main.py
```

## Usage

1. Start the application by running `main.py`
2. Click "Start Monitoring" to begin logging keyboard input
3. Use the tabs to switch between the monitor view and flagged commands
4. Save logs or flagged commands using the respective buttons

### Monitor Tab

The Monitor tab displays all keyboard input and window changes. You can:
- Start/stop monitoring
- Save logs to a file
- Clear the current log

### Command Flags Tab

The Command Flags tab displays any detected suspicious command line activity. You can:
- View flagged commands with timestamps
- Save the list of flagged commands
- Clear the flagged commands list

## Customization

You can customize the list of flagged commands by modifying the `flagged_commands` list in the `CommandDetector` class in `keylogger/command_detector.py`.

## Project Structure

```
advanced_keylogger/
├── main.py                # Entry point file
├── keylogger/
│   ├── __init__.py        # Package initialization
│   ├── input_monitor.py   # Keyboard and window monitoring
│   ├── command_detector.py# Command line detection and flagging
│   └── data_manager.py    # Saving and loading data
└── gui/
    ├── __init__.py        # Package initialization
    ├── app.py             # Main application window
    ├── monitor_tab.py     # Keylogging display tab
    └── flags_tab.py       # Command flags display tab
```

## Educational Purpose Notice

This software is created for educational purposes only. It should be used responsibly and ethically. The user assumes all responsibility for how this software is used. Monitoring someone's computer activity without their knowledge and consent may be illegal in your jurisdiction.

## License

This project is licensed under the MIT License - see the LICENSE file for details.