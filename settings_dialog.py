"""
Settings dialog for DailyFlow application.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QWidget, QLabel, QCheckBox, QComboBox, QPushButton,
                               QSpinBox, QGroupBox, QFormLayout, QMessageBox,
                               QSlider, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from settings import SettingsManager, Theme, get_theme_styles
from typing import List


class SettingsDialog(QDialog):
    """Settings dialog with multiple tabs."""
    
    theme_changed = Signal(Theme)
    settings_changed = Signal()
    
    def __init__(self, settings_manager: SettingsManager, routine_names: List[str], parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.routine_names = routine_names
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the settings dialog UI."""
        self.setWindowTitle("DailyFlow Settings")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_appearance_tab()
        self.create_advanced_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Startup group
        startup_group = QGroupBox("Startup Options")
        startup_layout = QFormLayout(startup_group)
        
        self.run_on_startup_cb = QCheckBox()
        startup_layout.addRow("Run DailyFlow on Windows startup:", self.run_on_startup_cb)
        
        self.auto_run_routine_cb = QCheckBox()
        startup_layout.addRow("Auto-run daily routine when app starts:", self.auto_run_routine_cb)
        
        self.default_routine_combo = QComboBox()
        self.default_routine_combo.addItems([""] + self.routine_names)
        startup_layout.addRow("Default routine to run:", self.default_routine_combo)
        
        layout.addWidget(startup_group)
        
        # Notifications group
        notifications_group = QGroupBox("Notifications & Behavior")
        notifications_layout = QFormLayout(notifications_group)
        
        self.show_notifications_cb = QCheckBox()
        notifications_layout.addRow("Show notifications during execution:", self.show_notifications_cb)
        
        self.minimize_to_tray_cb = QCheckBox()
        notifications_layout.addRow("Minimize to system tray:", self.minimize_to_tray_cb)
        
        self.show_welcome_cb = QCheckBox()
        notifications_layout.addRow("Show welcome message on first run:", self.show_welcome_cb)
        
        self.confirm_deletion_cb = QCheckBox()
        notifications_layout.addRow("Confirm routine deletion:", self.confirm_deletion_cb)
        
        layout.addWidget(notifications_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def create_appearance_tab(self):
        """Create the appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme group
        theme_group = QGroupBox("Color Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        theme_items = [
            ("Light Theme", Theme.LIGHT),
            ("Dark Theme", Theme.DARK),
            ("Forest Theme", Theme.FOREST),
            ("Ocean Theme", Theme.OCEAN),
            ("Sunset Theme", Theme.SUNSET)
        ]
        
        for name, theme in theme_items:
            self.theme_combo.addItem(name, theme)
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addRow("Application theme:", self.theme_combo)
        
        # Theme preview
        self.theme_preview = QLabel("Theme preview will appear here")
        self.theme_preview.setMinimumHeight(100)
        self.theme_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f0f0f0;
            }
        """)
        theme_layout.addRow("Preview:", self.theme_preview)
        
        layout.addWidget(theme_group)
        
        # Font group (bonus feature)
        font_group = QGroupBox("Display Options")
        font_layout = QFormLayout(font_group)
        
        self.log_lines_spin = QSpinBox()
        self.log_lines_spin.setRange(50, 500)
        self.log_lines_spin.setValue(100)
        self.log_lines_spin.setSuffix(" lines")
        font_layout.addRow("Execution log max lines:", self.log_lines_spin)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Appearance")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance group
        performance_group = QGroupBox("Performance & Storage")
        performance_layout = QFormLayout(performance_group)
        
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(10, 300)
        self.auto_save_spin.setValue(30)
        self.auto_save_spin.setSuffix(" seconds")
        performance_layout.addRow("Auto-save interval:", self.auto_save_spin)
        
        layout.addWidget(performance_group)
        
        # Developer options (bonus creative feature)
        dev_group = QGroupBox("Developer Options 🛠️")
        dev_layout = QFormLayout(dev_group)
        
        self.debug_mode_cb = QCheckBox()
        dev_layout.addRow("Enable debug logging:", self.debug_mode_cb)
        
        self.action_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.action_delay_slider.setRange(0, 5000)  # 0-5 seconds
        self.action_delay_slider.setValue(500)  # 0.5 seconds default
        self.delay_label = QLabel("0.5s")
        self.action_delay_slider.valueChanged.connect(
            lambda v: self.delay_label.setText(f"{v/1000:.1f}s")
        )
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(self.action_delay_slider)
        delay_layout.addWidget(self.delay_label)
        
        dev_layout.addRow("Extra delay between actions:", delay_layout)
        
        # Easter egg feature
        self.party_mode_cb = QCheckBox()
        self.party_mode_cb.setToolTip("🎉 Makes execution more fun with emojis and colors!")
        dev_layout.addRow("Party mode (fun execution messages):", self.party_mode_cb)
        
        layout.addWidget(dev_group)
        
        # Reset section
        reset_group = QGroupBox("Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_button = QPushButton("🔄 Reset All Settings to Default")
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        reset_layout.addWidget(reset_button)
        
        layout.addWidget(reset_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_current_settings(self):
        """Load current settings into the dialog."""
        # General tab
        self.run_on_startup_cb.setChecked(self.settings_manager.get('run_on_startup', False))
        self.auto_run_routine_cb.setChecked(self.settings_manager.get('auto_run_daily_routine', False))
        
        default_routine = self.settings_manager.get('default_routine_name', '')
        if default_routine in self.routine_names:
            self.default_routine_combo.setCurrentText(default_routine)
        
        self.show_notifications_cb.setChecked(self.settings_manager.get('show_notifications', True))
        self.minimize_to_tray_cb.setChecked(self.settings_manager.get('minimize_to_tray', False))
        self.show_welcome_cb.setChecked(self.settings_manager.get('show_welcome_message', True))
        self.confirm_deletion_cb.setChecked(self.settings_manager.get('confirm_routine_deletion', True))
        
        # Appearance tab
        current_theme = self.settings_manager.get_theme()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
        
        self.log_lines_spin.setValue(self.settings_manager.get('execution_log_lines', 100))
        
        # Advanced tab
        self.auto_save_spin.setValue(self.settings_manager.get('auto_save_interval', 30))
        self.debug_mode_cb.setChecked(self.settings_manager.get('debug_mode', False))
        self.action_delay_slider.setValue(self.settings_manager.get('action_extra_delay', 500))
        self.party_mode_cb.setChecked(self.settings_manager.get('party_mode', False))
        
        # Update theme preview
        self.update_theme_preview()
    
    def on_theme_changed(self):
        """Handle theme change."""
        self.update_theme_preview()
    
    def update_theme_preview(self):
        """Update the theme preview."""
        current_theme = self.theme_combo.currentData()
        if current_theme:
            styles = get_theme_styles(current_theme)
            preview_text = f"Theme: {current_theme.value.title()}"
            
            self.theme_preview.setText(f"✨ {preview_text} ✨\\n🎨 Main Background\\n📝 Text Color\\n🔘 Buttons")
            self.theme_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: {styles['main_bg']};
                    color: {styles['text_color']};
                    border: 2px solid {styles['button_primary']};
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                }}
            """)
    
    def apply_settings(self):
        """Apply settings without closing dialog."""
        self.save_settings()
        QMessageBox.information(self, "Settings Applied", "Settings have been saved successfully!")
    
    def accept_settings(self):
        """Apply settings and close dialog."""
        self.save_settings()
        self.accept()
    
    def save_settings(self):
        """Save all settings."""
        # General settings
        self.settings_manager.set('auto_run_daily_routine', self.auto_run_routine_cb.isChecked())
        self.settings_manager.set('default_routine_name', self.default_routine_combo.currentText())
        self.settings_manager.set('show_notifications', self.show_notifications_cb.isChecked())
        self.settings_manager.set('minimize_to_tray', self.minimize_to_tray_cb.isChecked())
        self.settings_manager.set('show_welcome_message', self.show_welcome_cb.isChecked())
        self.settings_manager.set('confirm_routine_deletion', self.confirm_deletion_cb.isChecked())
        
        # Appearance settings
        new_theme = self.theme_combo.currentData()
        old_theme = self.settings_manager.get_theme()
        if new_theme != old_theme:
            self.settings_manager.set_theme(new_theme)
            self.theme_changed.emit(new_theme)
        
        self.settings_manager.set('execution_log_lines', self.log_lines_spin.value())
        
        # Advanced settings
        self.settings_manager.set('auto_save_interval', self.auto_save_spin.value())
        self.settings_manager.set('debug_mode', self.debug_mode_cb.isChecked())
        self.settings_manager.set('action_extra_delay', self.action_delay_slider.value())
        self.settings_manager.set('party_mode', self.party_mode_cb.isChecked())
        
        # Handle startup setting (requires special handling)
        if self.run_on_startup_cb.isChecked() != self.settings_manager.get('run_on_startup', False):
            self.settings_manager.set_startup_enabled(self.run_on_startup_cb.isChecked())
        
        self.settings_changed.emit()
    
    def reset_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?\\n\\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.settings_manager.settings = self.settings_manager._default_settings()
            self.settings_manager.save_settings()
            
            # Reload the dialog
            self.load_current_settings()
            
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to default values.")