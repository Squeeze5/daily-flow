"""
Settings management for DailyFlow application.
"""
import json
import os
import winreg
from typing import Dict, Any
from enum import Enum


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    FOREST = "forest"
    OCEAN = "ocean"
    SUNSET = "sunset"


class SettingsManager:
    """Manages application settings and preferences."""
    
    def __init__(self, settings_file: str = "dailyflow_settings.json"):
        self.settings_file = settings_file
        self.settings = self._default_settings()
        self.load_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return {
            'run_on_startup': False,
            'auto_run_daily_routine': False,
            'default_routine_name': '',
            'theme': Theme.LIGHT.value,
            'window_size': {'width': 1200, 'height': 700},
            'window_position': {'x': 100, 'y': 100},
            'show_notifications': True,
            'minimize_to_tray': False,
            'execution_log_lines': 100,
            'auto_save_interval': 30,
            'confirm_routine_deletion': True,
            'show_welcome_message': True
        }
    
    def load_settings(self):
        """Load settings from JSON file."""
        if not os.path.exists(self.settings_file):
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                saved_settings = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            for key, value in saved_settings.items():
                if key in self.settings:
                    self.settings[key] = value
                    
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save_settings()
    
    def get_theme(self) -> Theme:
        """Get current theme."""
        try:
            return Theme(self.settings.get('theme', Theme.LIGHT.value))
        except ValueError:
            return Theme.LIGHT
    
    def set_theme(self, theme: Theme):
        """Set the application theme."""
        self.set('theme', theme.value)
    
    def set_startup_enabled(self, enabled: bool):
        """Enable/disable running on Windows startup."""
        self.set('run_on_startup', enabled)
        
        if enabled:
            self._add_to_startup()
        else:
            self._remove_from_startup()
    
    def _add_to_startup(self):
        """Add DailyFlow to Windows startup."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            
            app_path = os.path.abspath("main.py")
            python_path = os.path.join(os.path.dirname(app_path), "python.exe")
            startup_command = f'"{python_path}" "{app_path}"'
            
            winreg.SetValueEx(key, "DailyFlow", 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"Failed to add to startup: {e}")
    
    def _remove_from_startup(self):
        """Remove DailyFlow from Windows startup."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            
            winreg.DeleteValue(key, "DailyFlow")
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            pass  # Key doesn't exist, which is fine
        except Exception as e:
            print(f"Failed to remove from startup: {e}")
    
    def is_startup_enabled(self) -> bool:
        """Check if DailyFlow is set to run on startup."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_READ)
            
            winreg.QueryValueEx(key, "DailyFlow")
            winreg.CloseKey(key)
            return True
            
        except FileNotFoundError:
            return False
        except Exception:
            return False


def get_theme_styles(theme: Theme) -> Dict[str, str]:
    """Get CSS styles for different themes."""
    
    styles = {
        Theme.LIGHT: {
            'main_bg': '#ffffff',
            'panel_bg': '#f8f9fa',
            'text_color': '#212529',
            'button_primary': '#4CAF50',
            'button_primary_hover': '#45a049',
            'button_secondary': '#2196F3',
            'button_secondary_hover': '#1976D2',
            'button_danger': '#f44336',
            'button_danger_hover': '#d32f2f',
            'border_color': '#dee2e6',
            'log_bg': '#2b2b2b',
            'log_text': '#ffffff'
        },
        
        Theme.DARK: {
            'main_bg': '#2b2b2b',
            'panel_bg': '#3c3c3c',
            'text_color': '#ffffff',
            'button_primary': '#66BB6A',
            'button_primary_hover': '#4CAF50',
            'button_secondary': '#42A5F5',
            'button_secondary_hover': '#2196F3',
            'button_danger': '#EF5350',
            'button_danger_hover': '#f44336',
            'border_color': '#555555',
            'log_bg': '#1a1a1a',
            'log_text': '#ffffff'
        },
        
        Theme.FOREST: {
            'main_bg': '#f1f8e9',
            'panel_bg': '#e8f5e8',
            'text_color': '#2e7d32',
            'button_primary': '#388e3c',
            'button_primary_hover': '#2e7d32',
            'button_secondary': '#689f38',
            'button_secondary_hover': '#558b2f',
            'button_danger': '#d84315',
            'button_danger_hover': '#bf360c',
            'border_color': '#a5d6a7',
            'log_bg': '#1b5e20',
            'log_text': '#c8e6c9'
        },
        
        Theme.OCEAN: {
            'main_bg': '#e3f2fd',
            'panel_bg': '#e1f5fe',
            'text_color': '#01579b',
            'button_primary': '#0288d1',
            'button_primary_hover': '#0277bd',
            'button_secondary': '#29b6f6',
            'button_secondary_hover': '#0288d1',
            'button_danger': '#e91e63',
            'button_danger_hover': '#c2185b',
            'border_color': '#81d4fa',
            'log_bg': '#01579b',
            'log_text': '#b3e5fc'
        },
        
        Theme.SUNSET: {
            'main_bg': '#fff3e0',
            'panel_bg': '#ffe0b2',
            'text_color': '#e65100',
            'button_primary': '#ff9800',
            'button_primary_hover': '#f57c00',
            'button_secondary': '#ff5722',
            'button_secondary_hover': '#e64a19',
            'button_danger': '#d32f2f',
            'button_danger_hover': '#c62828',
            'border_color': '#ffcc02',
            'log_bg': '#bf360c',
            'log_text': '#ffccbc'
        }
    }
    
    return styles.get(theme, styles[Theme.LIGHT])