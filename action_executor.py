"""
Action execution engine for DailyFlow.
Handles running different types of actions.
"""
import subprocess
import webbrowser
import time
import os
import sys
from typing import Dict, Any
from models import Action, ActionType
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QThread, Signal
import pycaw.pycaw as pycaw
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class ActionExecutor(QThread):
    """Executes actions in a separate thread to avoid blocking the UI."""
    
    action_started = Signal(str)
    action_completed = Signal(str)
    action_failed = Signal(str, str)
    routine_completed = Signal()
    
    def __init__(self):
        super().__init__()
        self.actions = []
        self.should_stop = False
        
    def set_actions(self, actions):
        """Set the actions to execute."""
        self.actions = actions
        self.should_stop = False
    
    def stop_execution(self):
        """Stop the current execution."""
        self.should_stop = True
    
    def run(self):
        """Execute all actions in sequence."""
        for i, action in enumerate(self.actions):
            if self.should_stop:
                break
                
            if not action.enabled:
                continue
                
            try:
                action_desc = self._get_action_description(action)
                self.action_started.emit(action_desc)
                
                success = self._execute_single_action(action)
                
                if success:
                    self.action_completed.emit(action_desc)
                else:
                    self.action_failed.emit(action_desc, "Execution failed")
                    
            except Exception as e:
                action_desc = self._get_action_description(action)
                self.action_failed.emit(action_desc, str(e))
        
        if not self.should_stop:
            self.routine_completed.emit()
    
    def _get_action_description(self, action: Action) -> str:
        """Get a human-readable description of the action."""
        if action.action_type == ActionType.OPEN_APP:
            app_path = action.parameters.get('app_path', '')
            return f"Opening {os.path.basename(app_path)}"
        elif action.action_type == ActionType.OPEN_WEBSITE:
            url = action.parameters.get('url', '')
            return f"Opening {url}"
        elif action.action_type == ActionType.SHOW_MESSAGE:
            return "Showing message"
        elif action.action_type == ActionType.PLAY_MUSIC:
            return "Playing music"
        elif action.action_type == ActionType.DELAY:
            seconds = action.parameters.get('seconds', 0)
            return f"Waiting {seconds} seconds"
        elif action.action_type == ActionType.DO_NOT_DISTURB:
            return "Enabling Do Not Disturb"
        return "Unknown action"
    
    def _execute_single_action(self, action: Action) -> bool:
        """Execute a single action."""
        try:
            if action.action_type == ActionType.OPEN_APP:
                return self._open_app(action.parameters)
            elif action.action_type == ActionType.OPEN_WEBSITE:
                return self._open_website(action.parameters)
            elif action.action_type == ActionType.SHOW_MESSAGE:
                return self._show_message(action.parameters)
            elif action.action_type == ActionType.PLAY_MUSIC:
                return self._play_music(action.parameters)
            elif action.action_type == ActionType.DELAY:
                return self._delay(action.parameters)
            elif action.action_type == ActionType.DO_NOT_DISTURB:
                return self._do_not_disturb(action.parameters)
            return False
        except Exception as e:
            print(f"Error executing action: {e}")
            return False
    
    def _open_app(self, params: Dict[str, Any]) -> bool:
        """Open a desktop application."""
        app_path = params.get('app_path', '')
        if not app_path:
            return False
        
        try:
            # Handle different ways to specify applications
            if app_path.endswith('.exe') and not os.path.exists(app_path):
                # Try to find the app in PATH
                subprocess.Popen([app_path])
            elif os.path.exists(app_path):
                subprocess.Popen([app_path])
            else:
                # Try as a system command
                os.startfile(app_path)
            return True
        except Exception as e:
            print(f"Failed to open app {app_path}: {e}")
            return False
    
    def _open_website(self, params: Dict[str, Any]) -> bool:
        """Open a website in the default browser."""
        url = params.get('url', '')
        if not url:
            return False
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Failed to open website {url}: {e}")
            return False
    
    def _show_message(self, params: Dict[str, Any]) -> bool:
        """Show a message dialog."""
        message = params.get('message', '')
        title = params.get('title', 'DailyFlow')
        
        try:
            # We'll emit a signal to show the message in the main thread
            # since QMessageBox needs to be created in the main thread
            self.show_message_signal.emit(title, message)
            return True
        except Exception as e:
            print(f"Failed to show message: {e}")
            return False
    
    # Add signal for showing messages
    show_message_signal = Signal(str, str)
    
    def _play_music(self, params: Dict[str, Any]) -> bool:
        """Play music via URL or system command."""
        music_url = params.get('url', '')
        command = params.get('command', '')
        
        try:
            if music_url:
                # Try to open music URL in default media player
                webbrowser.open(music_url)
                return True
            elif command:
                # Execute system command
                subprocess.Popen(command, shell=True)
                return True
            return False
        except Exception as e:
            print(f"Failed to play music: {e}")
            return False
    
    def _delay(self, params: Dict[str, Any]) -> bool:
        """Wait for specified number of seconds."""
        seconds = params.get('seconds', 1)
        try:
            time.sleep(float(seconds))
            return True
        except Exception as e:
            print(f"Failed to delay: {e}")
            return False
    
    def _do_not_disturb(self, params: Dict[str, Any]) -> bool:
        """Enable Do Not Disturb mode (mute system volume)."""
        try:
            # Get the default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            # Mute the system
            volume.SetMute(1, None)
            return True
        except Exception as e:
            print(f"Failed to enable Do Not Disturb: {e}")
            # Fallback: try to mute using nircmd if available
            try:
                subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], check=True)
                return True
            except:
                return False


class StaticActionExecutor:
    """Static methods for executing actions without threading (for testing)."""
    
    @staticmethod
    def show_message_dialog(title: str, message: str, parent=None):
        """Show a message dialog in the main thread."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()