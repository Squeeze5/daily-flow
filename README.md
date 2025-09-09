# DailyFlow - Morning Routine Automation

A Windows desktop application that helps you automate your morning routine by launching a customized sequence of apps, websites, and system actions.

## Features

- **Custom Routine Builder**: Create, edit, and delete multiple routines with various action types
- **Action Types**:
  - Open desktop applications (e.g., Notepad, VS Code, Outlook)
  - Open websites in your default browser (e.g., Gmail, Calendar)
  - Show custom messages and notes
  - Play music via URLs or system commands
  - Add delays between actions
  - Enable Do Not Disturb mode (mute system volume)
- **Modern GUI**: Clean interface with routine list on the left and editor on the right
- **Routine Scheduler**: Schedule routines to run at specific times using Windows Task Scheduler
- **JSON Persistence**: All routines are saved locally and persist between app launches
- **Manual Execution**: "Start My Day" button to run routines on demand

## Installation

1. **Install Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Creating Your First Routine

1. Launch DailyFlow by running `python main.py`
2. Click "➕ New Routine" to create a new routine
3. Give your routine a name and description
4. Click "➕ Add Action" to add actions to your routine:
   - **Open Application**: Enter the path to an executable (e.g., `notepad.exe`, `C:\\Program Files\\...\\app.exe`)
   - **Open Website**: Enter a URL (e.g., `https://gmail.com` or just `gmail.com`)
   - **Show Message**: Create a custom message dialog
   - **Play Music**: Enter a music URL or system command
   - **Delay**: Add a pause between actions (in seconds)
   - **Do Not Disturb**: Mute system volume
5. Arrange actions in the desired order using "⬆️ Move Up" and "⬇️ Move Down"
6. Click "💾 Save Changes" to save your routine

### Running Routines

- **Manual**: Select a routine and click "🚀 Start My Day"
- **Scheduled**: Set a scheduled time in the routine editor, and it will run automatically via Windows Task Scheduler

### Command Line Usage

```bash
# Run a specific routine
python main.py --routine "Morning Startup"

# List all available routines
python main.py --list-routines
```

## Example Routine

The app comes with a sample "Morning Startup" routine that:
1. Shows a welcome message
2. Waits 2 seconds
3. Opens Gmail in your browser
4. Opens Notepad
5. Waits 1 second
6. Shows a completion message

## File Structure

- `main.py` - Main entry point with CLI support
- `main_window.py` - Main GUI window
- `models.py` - Data models for routines and actions
- `routine_editor.py` - Routine editing interface
- `action_executor.py` - Action execution engine
- `scheduler.py` - Windows Task Scheduler integration
- `requirements.txt` - Python package dependencies
- `dailyflow_config.json` - Your saved routines (created automatically)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure all requirements are installed with `pip install -r requirements.txt`

2. **Applications not opening**: 
   - For system apps, use just the executable name (e.g., `notepad.exe`)
   - For installed apps, use the full path (e.g., `C:\\Program Files\\...\\app.exe`)
   - Check if the application path is correct

3. **Scheduling not working**: 
   - Make sure you're running as administrator for Task Scheduler access
   - Check Windows Task Scheduler to see if tasks were created

4. **Do Not Disturb not working**: 
   - This feature requires the `pycaw` library to be properly installed
   - Some systems may require additional permissions

### Getting Help

- Check the execution log in the main window for error details
- Ensure all file paths and URLs are correct
- Test actions individually before adding them to routines

## System Requirements

- Windows 10/11
- Python 3.8 or higher
- Administrator privileges (recommended for scheduling features)

## License

This project is provided as-is for educational and personal use.