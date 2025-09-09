# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DailyFlow** is a Windows desktop application for morning routine automation built with Python and PyQt6. Users can create custom sequences of actions (opening apps, websites, system commands) to streamline their daily startup process.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run with CLI options
python main.py --list-routines
python main.py --routine "Morning Startup"
```

### No Build Process
This is a Python application that runs directly - no build step required.

## Architecture

### Tech Stack
- **Python 3.8+** with PyQt6 for modern GUI
- **pycaw** for Windows audio control
- **comtypes** for Windows COM interfaces
- **Windows Task Scheduler** for routine scheduling

### Core Components
1. **models.py**: Data models (Routine, Action, RoutineManager) with JSON persistence
2. **main_window.py**: Main GUI with left/right panels and execution controls
3. **routine_editor.py**: Routine and action editing interfaces with dialogs
4. **action_executor.py**: Threaded action execution engine
5. **scheduler.py**: Windows Task Scheduler integration
6. **main.py**: Entry point with CLI support

### Action Types Implemented
- **OPEN_APP**: Launch desktop applications by path
- **OPEN_WEBSITE**: Open URLs in default browser
- **SHOW_MESSAGE**: Display custom message dialogs
- **PLAY_MUSIC**: Play music via URLs or system commands
- **DELAY**: Wait specified seconds between actions
- **DO_NOT_DISTURB**: Mute system volume

## Key Files

- `main.py` - Entry point with GUI and CLI modes
- `dailyflow_config.json` - Auto-generated user configuration
- `requirements.txt` - Python dependencies
- `README.md` - User documentation

## Important Implementation Details

- All actions execute in separate thread to avoid blocking UI
- JSON configuration automatically saves on changes
- Sample routine created on first launch
- Windows Task Scheduler integration for automatic execution
- CLI mode for scheduled routine execution
- Local-only application with no external dependencies