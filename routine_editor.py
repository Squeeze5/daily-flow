"""
Routine editor widget for creating and editing routines.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTextEdit, QLabel, QPushButton, QListWidget, 
                             QListWidgetItem, QComboBox, QSpinBox, QTimeEdit,
                             QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                             QMessageBox, QGroupBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtGui import QFont
from models import Routine, Action, ActionType
from typing import Optional


class ActionDialog(QDialog):
    """Dialog for creating/editing individual actions."""
    
    def __init__(self, action: Optional[Action] = None, parent=None):
        super().__init__(parent)
        self.action = action
        self.init_ui()
        
        if action:
            self.load_action(action)
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Edit Action" if self.action else "New Action")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Action type selection
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItem("Open Application", ActionType.OPEN_APP)
        self.action_type_combo.addItem("Open Website", ActionType.OPEN_WEBSITE)
        self.action_type_combo.addItem("Show Message", ActionType.SHOW_MESSAGE)
        self.action_type_combo.addItem("Play Music", ActionType.PLAY_MUSIC)
        self.action_type_combo.addItem("Delay/Wait", ActionType.DELAY)
        self.action_type_combo.addItem("Do Not Disturb", ActionType.DO_NOT_DISTURB)
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        form_layout.addRow("Action Type:", self.action_type_combo)
        
        # Enable checkbox
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(True)
        form_layout.addRow("Enabled:", self.enabled_checkbox)
        
        layout.addLayout(form_layout)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)
        layout.addWidget(self.params_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize parameters for first action type
        self.on_action_type_changed()
    
    def on_action_type_changed(self):
        """Handle action type change."""
        # Clear existing parameter widgets
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        action_type = self.action_type_combo.currentData()
        
        if action_type == ActionType.OPEN_APP:
            self.app_path_edit = QLineEdit()
            self.app_path_edit.setPlaceholderText("e.g., notepad.exe, C:\\Program Files\\...\\app.exe")
            self.params_layout.addRow("Application Path:", self.app_path_edit)
            
        elif action_type == ActionType.OPEN_WEBSITE:
            self.url_edit = QLineEdit()
            self.url_edit.setPlaceholderText("e.g., https://gmail.com, youtube.com")
            self.params_layout.addRow("Website URL:", self.url_edit)
            
        elif action_type == ActionType.SHOW_MESSAGE:
            self.message_title_edit = QLineEdit()
            self.message_title_edit.setPlaceholderText("Message Title (optional)")
            self.message_title_edit.setText("DailyFlow")
            self.params_layout.addRow("Title:", self.message_title_edit)
            
            self.message_text_edit = QTextEdit()
            self.message_text_edit.setPlaceholderText("Enter your message here...")
            self.message_text_edit.setMaximumHeight(100)
            self.params_layout.addRow("Message:", self.message_text_edit)
            
        elif action_type == ActionType.PLAY_MUSIC:
            self.music_url_edit = QLineEdit()
            self.music_url_edit.setPlaceholderText("e.g., https://open.spotify.com/playlist/...")
            self.params_layout.addRow("Music URL:", self.music_url_edit)
            
            self.music_command_edit = QLineEdit()
            self.music_command_edit.setPlaceholderText("Or system command (optional)")
            self.params_layout.addRow("System Command:", self.music_command_edit)
            
        elif action_type == ActionType.DELAY:
            self.delay_spinbox = QSpinBox()
            self.delay_spinbox.setRange(1, 3600)  # 1 second to 1 hour
            self.delay_spinbox.setValue(5)
            self.delay_spinbox.setSuffix(" seconds")
            self.params_layout.addRow("Delay Duration:", self.delay_spinbox)
            
        elif action_type == ActionType.DO_NOT_DISTURB:
            info_label = QLabel("This action will mute the system volume.")
            info_label.setStyleSheet("color: #666; font-style: italic;")
            self.params_layout.addRow(info_label)
    
    def load_action(self, action: Action):
        """Load an existing action into the dialog."""
        # Set action type
        for i in range(self.action_type_combo.count()):
            if self.action_type_combo.itemData(i) == action.action_type:
                self.action_type_combo.setCurrentIndex(i)
                break
        
        # Set enabled state
        self.enabled_checkbox.setChecked(action.enabled)
        
        # Load parameters based on action type
        params = action.parameters
        
        if action.action_type == ActionType.OPEN_APP:
            if hasattr(self, 'app_path_edit'):
                self.app_path_edit.setText(params.get('app_path', ''))
                
        elif action.action_type == ActionType.OPEN_WEBSITE:
            if hasattr(self, 'url_edit'):
                self.url_edit.setText(params.get('url', ''))
                
        elif action.action_type == ActionType.SHOW_MESSAGE:
            if hasattr(self, 'message_title_edit'):
                self.message_title_edit.setText(params.get('title', 'DailyFlow'))
            if hasattr(self, 'message_text_edit'):
                self.message_text_edit.setPlainText(params.get('message', ''))
                
        elif action.action_type == ActionType.PLAY_MUSIC:
            if hasattr(self, 'music_url_edit'):
                self.music_url_edit.setText(params.get('url', ''))
            if hasattr(self, 'music_command_edit'):
                self.music_command_edit.setText(params.get('command', ''))
                
        elif action.action_type == ActionType.DELAY:
            if hasattr(self, 'delay_spinbox'):
                self.delay_spinbox.setValue(params.get('seconds', 5))
    
    def get_action(self) -> Optional[Action]:
        """Get the action from the dialog inputs."""
        action_type = self.action_type_combo.currentData()
        enabled = self.enabled_checkbox.isChecked()
        parameters = {}
        
        try:
            if action_type == ActionType.OPEN_APP:
                app_path = self.app_path_edit.text().strip()
                if not app_path:
                    QMessageBox.warning(self, "Invalid Input", "Application path is required.")
                    return None
                parameters['app_path'] = app_path
                
            elif action_type == ActionType.OPEN_WEBSITE:
                url = self.url_edit.text().strip()
                if not url:
                    QMessageBox.warning(self, "Invalid Input", "Website URL is required.")
                    return None
                parameters['url'] = url
                
            elif action_type == ActionType.SHOW_MESSAGE:
                title = self.message_title_edit.text().strip() or "DailyFlow"
                message = self.message_text_edit.toPlainText().strip()
                if not message:
                    QMessageBox.warning(self, "Invalid Input", "Message text is required.")
                    return None
                parameters['title'] = title
                parameters['message'] = message
                
            elif action_type == ActionType.PLAY_MUSIC:
                url = self.music_url_edit.text().strip()
                command = self.music_command_edit.text().strip()
                if not url and not command:
                    QMessageBox.warning(self, "Invalid Input", "Either music URL or system command is required.")
                    return None
                if url:
                    parameters['url'] = url
                if command:
                    parameters['command'] = command
                    
            elif action_type == ActionType.DELAY:
                seconds = self.delay_spinbox.value()
                parameters['seconds'] = seconds
                
            elif action_type == ActionType.DO_NOT_DISTURB:
                # No parameters needed
                pass
            
            return Action(action_type, parameters, enabled)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create action: {str(e)}")
            return None


class RoutineEditor(QWidget):
    """Widget for editing routines."""
    
    routine_changed = Signal(Routine)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_routine = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the editor UI."""
        layout = QVBoxLayout(self)
        
        # Basic routine information
        info_group = QGroupBox("Routine Information")
        info_layout = QFormLayout(info_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_routine_data_changed)
        info_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.textChanged.connect(self.on_routine_data_changed)
        info_layout.addRow("Description:", self.description_edit)
        
        self.scheduled_time_edit = QTimeEdit()
        self.scheduled_time_edit.setDisplayFormat("HH:mm")
        self.scheduled_time_edit.timeChanged.connect(self.on_routine_data_changed)
        info_layout.addRow("Scheduled Time:", self.scheduled_time_edit)
        
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self.on_routine_data_changed)
        info_layout.addRow("Enabled:", self.enabled_checkbox)
        
        layout.addWidget(info_group)
        
        # Actions section
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Action list controls
        controls_layout = QHBoxLayout()
        
        self.add_action_button = QPushButton("➕ Add Action")
        self.add_action_button.clicked.connect(self.add_action)
        controls_layout.addWidget(self.add_action_button)
        
        self.edit_action_button = QPushButton("✏️ Edit Action")
        self.edit_action_button.clicked.connect(self.edit_action)
        self.edit_action_button.setEnabled(False)
        controls_layout.addWidget(self.edit_action_button)
        
        self.delete_action_button = QPushButton("🗑️ Delete Action")
        self.delete_action_button.clicked.connect(self.delete_action)
        self.delete_action_button.setEnabled(False)
        controls_layout.addWidget(self.delete_action_button)
        
        controls_layout.addStretch()
        
        self.move_up_button = QPushButton("⬆️ Move Up")
        self.move_up_button.clicked.connect(self.move_action_up)
        self.move_up_button.setEnabled(False)
        controls_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("⬇️ Move Down")
        self.move_down_button.clicked.connect(self.move_action_down)
        self.move_down_button.setEnabled(False)
        controls_layout.addWidget(self.move_down_button)
        
        actions_layout.addLayout(controls_layout)
        
        # Actions list
        self.actions_list = QListWidget()
        self.actions_list.currentRowChanged.connect(self.on_action_selection_changed)
        actions_layout.addWidget(self.actions_list)
        
        layout.addWidget(actions_group)
        
        # Apply button
        self.apply_button = QPushButton("💾 Save Changes")
        self.apply_button.clicked.connect(self.save_routine)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.apply_button)
    
    def load_routine(self, routine: Routine):
        """Load a routine into the editor."""
        self.current_routine = routine
        
        # Load basic information
        self.name_edit.setText(routine.name)
        self.description_edit.setPlainText(routine.description)
        self.enabled_checkbox.setChecked(routine.enabled)
        
        # Load scheduled time
        if routine.scheduled_time:
            time_parts = routine.scheduled_time.split(':')
            if len(time_parts) == 2:
                hour, minute = int(time_parts[0]), int(time_parts[1])
                self.scheduled_time_edit.setTime(QTime(hour, minute))
        
        # Load actions
        self.load_actions()
    
    def load_actions(self):
        """Load actions into the list."""
        self.actions_list.clear()
        
        if not self.current_routine:
            return
        
        for i, action in enumerate(self.current_routine.actions):
            item_text = self.get_action_display_text(action)
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            
            # Style disabled actions
            if not action.enabled:
                item.setText(f"[DISABLED] {item_text}")
                
            self.actions_list.addItem(item)
    
    def get_action_display_text(self, action: Action) -> str:
        """Get display text for an action."""
        if action.action_type == ActionType.OPEN_APP:
            app_path = action.parameters.get('app_path', '')
            return f"Open App: {app_path}"
        elif action.action_type == ActionType.OPEN_WEBSITE:
            url = action.parameters.get('url', '')
            return f"Open Website: {url}"
        elif action.action_type == ActionType.SHOW_MESSAGE:
            message = action.parameters.get('message', '')[:50]
            return f"Show Message: {message}..."
        elif action.action_type == ActionType.PLAY_MUSIC:
            url = action.parameters.get('url', action.parameters.get('command', ''))
            return f"Play Music: {url}"
        elif action.action_type == ActionType.DELAY:
            seconds = action.parameters.get('seconds', 0)
            return f"Wait {seconds} seconds"
        elif action.action_type == ActionType.DO_NOT_DISTURB:
            return "Enable Do Not Disturb"
        return "Unknown Action"
    
    def on_action_selection_changed(self, current_row):
        """Handle action selection change."""
        has_selection = current_row >= 0
        self.edit_action_button.setEnabled(has_selection)
        self.delete_action_button.setEnabled(has_selection)
        self.move_up_button.setEnabled(has_selection and current_row > 0)
        self.move_down_button.setEnabled(
            has_selection and current_row < self.actions_list.count() - 1
        )
    
    def add_action(self):
        """Add a new action."""
        dialog = ActionDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()
            if action and self.current_routine:
                self.current_routine.actions.append(action)
                self.load_actions()
                self.actions_list.setCurrentRow(len(self.current_routine.actions) - 1)
    
    def edit_action(self):
        """Edit the selected action."""
        current_row = self.actions_list.currentRow()
        if current_row < 0 or not self.current_routine:
            return
        
        action = self.current_routine.actions[current_row]
        dialog = ActionDialog(action, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_action = dialog.get_action()
            if updated_action:
                self.current_routine.actions[current_row] = updated_action
                self.load_actions()
                self.actions_list.setCurrentRow(current_row)
    
    def delete_action(self):
        """Delete the selected action."""
        current_row = self.actions_list.currentRow()
        if current_row < 0 or not self.current_routine:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Action",
            "Are you sure you want to delete this action?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.current_routine.actions[current_row]
            self.load_actions()
    
    def move_action_up(self):
        """Move the selected action up."""
        current_row = self.actions_list.currentRow()
        if current_row <= 0 or not self.current_routine:
            return
        
        # Swap actions
        actions = self.current_routine.actions
        actions[current_row], actions[current_row - 1] = actions[current_row - 1], actions[current_row]
        
        self.load_actions()
        self.actions_list.setCurrentRow(current_row - 1)
    
    def move_action_down(self):
        """Move the selected action down."""
        current_row = self.actions_list.currentRow()
        if current_row < 0 or current_row >= len(self.current_routine.actions) - 1:
            return
        
        # Swap actions
        actions = self.current_routine.actions
        actions[current_row], actions[current_row + 1] = actions[current_row + 1], actions[current_row]
        
        self.load_actions()
        self.actions_list.setCurrentRow(current_row + 1)
    
    def on_routine_data_changed(self):
        """Handle routine data changes."""
        # This method is called when basic routine info changes
        pass
    
    def save_routine(self):
        """Save the current routine changes."""
        if not self.current_routine:
            return
        
        # Update routine with current form data
        self.current_routine.name = self.name_edit.text().strip()
        self.current_routine.description = self.description_edit.toPlainText().strip()
        self.current_routine.enabled = self.enabled_checkbox.isChecked()
        
        # Update scheduled time
        time = self.scheduled_time_edit.time()
        self.current_routine.scheduled_time = time.toString("HH:mm")
        
        # Emit signal to notify parent
        self.routine_changed.emit(self.current_routine)