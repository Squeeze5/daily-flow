"""
Main window for DailyFlow application.
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
                             QLabel, QSplitter, QMessageBox, QProgressBar, QTextEdit,
                             QScrollArea, QFrame, QMenuBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QAction
from models import RoutineManager, Routine, create_sample_routine
from routine_editor import RoutineEditor
from action_executor import ActionExecutor, StaticActionExecutor
from scheduler import SchedulerManager
from settings import SettingsManager, Theme, get_theme_styles
from settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window with routine list and editor."""
    
    def __init__(self):
        super().__init__()
        self.routine_manager = RoutineManager()
        self.scheduler_manager = SchedulerManager()
        self.action_executor = ActionExecutor()
        self.settings_manager = SettingsManager()
        self.current_routine = None
        
        self.init_ui()
        self.setup_connections()
        self.apply_theme(self.settings_manager.get_theme())
        self.load_routines()
        
        # Create sample routine if no routines exist
        if not self.routine_manager.get_all_routines():
            sample = create_sample_routine()
            self.routine_manager.add_routine(sample)
            self.load_routines()
        
        # Auto-run daily routine if enabled
        if self.settings_manager.get('auto_run_daily_routine', False):
            self.auto_run_daily_routine()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DailyFlow - Morning Routine Automation")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Routine list
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Routine editor
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 2)  # Right panel takes more space
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set up progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with routine list and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("My Routines")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Routine list
        self.routine_list = QListWidget()
        self.routine_list.setMinimumWidth(250)
        layout.addWidget(self.routine_list)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.start_button = QPushButton("🚀 Start My Day")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.new_routine_button = QPushButton("➕ New Routine")
        self.new_routine_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.new_routine_button)
        
        self.delete_routine_button = QPushButton("🗑️ Delete Routine")
        self.delete_routine_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        button_layout.addWidget(self.delete_routine_button)
        
        self.stop_button = QPushButton("⏹️ Stop Routine")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Execution log
        log_label = QLabel("Execution Log:")
        log_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)
        
        self.execution_log = QTextEdit()
        self.execution_log.setMaximumHeight(150)
        self.execution_log.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.execution_log)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with routine editor."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        self.editor_title = QLabel("Select a routine to edit")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.editor_title.setFont(title_font)
        layout.addWidget(self.editor_title)
        
        # Routine editor
        self.routine_editor = RoutineEditor()
        self.routine_editor.setEnabled(False)
        layout.addWidget(self.routine_editor)
        
        return panel
    
    def setup_connections(self):
        """Set up signal connections."""
        # Button connections
        self.start_button.clicked.connect(self.start_routine)
        self.new_routine_button.clicked.connect(self.new_routine)
        self.delete_routine_button.clicked.connect(self.delete_routine)
        self.stop_button.clicked.connect(self.stop_routine)
        
        # List selection
        self.routine_list.currentItemChanged.connect(self.on_routine_selected)
        
        # Editor connections
        self.routine_editor.routine_changed.connect(self.on_routine_changed)
        
        # Action executor connections
        self.action_executor.action_started.connect(self.on_action_started)
        self.action_executor.action_completed.connect(self.on_action_completed)
        self.action_executor.action_failed.connect(self.on_action_failed)
        self.action_executor.routine_completed.connect(self.on_routine_completed)
        self.action_executor.show_message_signal.connect(StaticActionExecutor.show_message_dialog)
    
    def load_routines(self):
        """Load routines into the list widget."""
        self.routine_list.clear()
        routines = self.routine_manager.get_all_routines()
        
        for routine in routines:
            item = QListWidgetItem(routine.name)
            item.setData(Qt.ItemDataRole.UserRole, routine.name)
            
            # Add description as tooltip
            if routine.description:
                item.setToolTip(f"{routine.name}: {routine.description}")
            
            # Mark scheduled routines
            if routine.scheduled_time:
                item.setText(f"{routine.name} ⏰ {routine.scheduled_time}")
            
            self.routine_list.addItem(item)
        
        # Select first routine if available
        if self.routine_list.count() > 0:
            self.routine_list.setCurrentRow(0)
    
    def on_routine_selected(self, current_item, previous_item):
        """Handle routine selection change."""
        if current_item is None:
            self.routine_editor.setEnabled(False)
            self.editor_title.setText("Select a routine to edit")
            self.current_routine = None
            return
        
        routine_name = current_item.data(Qt.ItemDataRole.UserRole)
        routine = self.routine_manager.get_routine(routine_name)
        
        if routine:
            self.current_routine = routine
            self.routine_editor.setEnabled(True)
            self.editor_title.setText(f"Editing: {routine.name}")
            self.routine_editor.load_routine(routine)
    
    def on_routine_changed(self, routine: Routine):
        """Handle routine changes from editor."""
        if self.current_routine:
            old_name = self.current_routine.name
            if self.routine_manager.update_routine(old_name, routine):
                self.current_routine = routine
                self.load_routines()
                
                # Reselect the updated routine
                for i in range(self.routine_list.count()):
                    item = self.routine_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == routine.name:
                        self.routine_list.setCurrentRow(i)
                        break
    
    def new_routine(self):
        """Create a new routine."""
        routine = Routine(name="New Routine", description="A new routine")
        
        # Find unique name
        counter = 1
        original_name = routine.name
        while any(r.name == routine.name for r in self.routine_manager.get_all_routines()):
            routine.name = f"{original_name} {counter}"
            counter += 1
        
        if self.routine_manager.add_routine(routine):
            self.load_routines()
            # Select the new routine
            for i in range(self.routine_list.count()):
                item = self.routine_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == routine.name:
                    self.routine_list.setCurrentRow(i)
                    break
    
    def delete_routine(self):
        """Delete the selected routine."""
        current_item = self.routine_list.currentItem()
        if current_item is None:
            return
        
        routine_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "Delete Routine",
            f"Are you sure you want to delete '{routine_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.routine_manager.delete_routine(routine_name):
                self.load_routines()
                self.current_routine = None
                self.routine_editor.setEnabled(False)
                self.editor_title.setText("Select a routine to edit")
    
    def start_routine(self):
        """Start executing the selected routine."""
        current_item = self.routine_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "No Routine", "Please select a routine to start.")
            return
        
        routine_name = current_item.data(Qt.ItemDataRole.UserRole)
        routine = self.routine_manager.get_routine(routine_name)
        
        if not routine or not routine.actions:
            QMessageBox.information(self, "Empty Routine", "The selected routine has no actions.")
            return
        
        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Clear log and show progress
        self.execution_log.clear()
        self.execution_log.append(f"Starting routine: {routine.name}")
        
        # Start execution
        self.action_executor.set_actions(routine.actions)
        self.action_executor.start()
    
    def stop_routine(self):
        """Stop the currently executing routine."""
        self.action_executor.stop_execution()
        self.on_routine_completed()
        self.execution_log.append("Routine stopped by user.")
    
    def on_action_started(self, description: str):
        """Handle action started event."""
        self.execution_log.append(f"▶️ {description}")
        self.statusBar().showMessage(f"Executing: {description}")
    
    def on_action_completed(self, description: str):
        """Handle action completed event."""
        self.execution_log.append(f"✅ {description} - Completed")
    
    def on_action_failed(self, description: str, error: str):
        """Handle action failed event."""
        self.execution_log.append(f"❌ {description} - Failed: {error}")
    
    def on_routine_completed(self):
        """Handle routine completion."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("Routine completed")
        self.execution_log.append("🎉 Routine completed!")
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About DailyFlow", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_settings(self):
        """Open the settings dialog."""
        routine_names = [routine.name for routine in self.routine_manager.get_all_routines()]
        dialog = SettingsDialog(self.settings_manager, routine_names, self)
        
        # Connect signals
        dialog.theme_changed.connect(self.apply_theme)
        dialog.settings_changed.connect(self.on_settings_changed)
        
        dialog.exec()
    
    def apply_theme(self, theme: Theme):
        """Apply a color theme to the application."""
        styles = get_theme_styles(theme)
        
        # Main window style
        main_style = f"""
            QMainWindow {{
                background-color: {styles['main_bg']};
                color: {styles['text_color']};
            }}
            QWidget {{
                background-color: {styles['panel_bg']};
                color: {styles['text_color']};
            }}
            QLabel {{
                color: {styles['text_color']};
            }}
        """
        
        # Button styles
        button_style = f"""
            QPushButton {{
                background-color: {styles['button_secondary']};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_secondary_hover']};
            }}
        """
        
        # Start button special style
        start_button_style = f"""
            QPushButton {{
                background-color: {styles['button_primary']};
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """
        
        # Delete button style
        delete_button_style = f"""
            QPushButton {{
                background-color: {styles['button_danger']};
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_danger_hover']};
            }}
        """
        
        # Execution log style
        log_style = f"""
            QTextEdit {{
                background-color: {styles['log_bg']};
                color: {styles['log_text']};
                border: 2px solid {styles['button_primary']};
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """
        
        # Apply styles
        self.setStyleSheet(main_style)
        self.start_button.setStyleSheet(start_button_style)
        self.delete_routine_button.setStyleSheet(delete_button_style)
        self.execution_log.setStyleSheet(log_style)
        
        # Apply button style to other buttons
        for button in [self.new_routine_button, self.stop_button]:
            button.setStyleSheet(button_style)
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # You can add any additional logic here when settings change
        pass
    
    def auto_run_daily_routine(self):
        """Auto-run the daily routine if configured."""
        default_routine_name = self.settings_manager.get('default_routine_name', '')
        if not default_routine_name:
            return
        
        routine = self.routine_manager.get_routine(default_routine_name)
        if routine and routine.enabled and routine.actions:
            # Show welcome message if enabled
            if self.settings_manager.get('show_welcome_message', True):
                QMessageBox.information(
                    self, 
                    "Auto-Start", 
                    f"Starting your daily routine: {routine.name}"
                )
            
            # Start the routine
            self.current_routine = routine
            self.start_routine()
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>🌅 DailyFlow</h2>
        <p><b>Morning Routine Automation</b></p>
        <p>Version 1.0</p>
        <br>
        <p>DailyFlow helps you automate your morning routine by launching
        customized sequences of apps, websites, and system actions.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>✨ Custom routine builder</li>
        <li>🚀 One-click routine execution</li>
        <li>⏰ Automatic scheduling</li>
        <li>🎨 Multiple themes</li>
        <li>🔧 Advanced settings</li>
        </ul>
        <br>
        <p>Built with Python & PySide6</p>
        """
        
        QMessageBox.about(self, "About DailyFlow", about_text)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("DailyFlow")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()