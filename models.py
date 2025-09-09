"""
Data models for DailyFlow routine management.
"""
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os


class ActionType(Enum):
    OPEN_APP = "open_app"
    OPEN_WEBSITE = "open_website" 
    SHOW_MESSAGE = "show_message"
    PLAY_MUSIC = "play_music"
    DELAY = "delay"
    DO_NOT_DISTURB = "do_not_disturb"


@dataclass
class Action:
    """Represents a single action in a routine."""
    action_type: ActionType
    parameters: Dict[str, Any]
    enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        return cls(
            action_type=ActionType(data['action_type']),
            parameters=data['parameters'],
            enabled=data.get('enabled', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'parameters': self.parameters,
            'enabled': self.enabled
        }


@dataclass
class Routine:
    """Represents a complete routine with multiple actions."""
    name: str
    description: str = ""
    actions: List[Action] = None
    scheduled_time: str = ""  # Format: "HH:MM"
    enabled: bool = True
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Routine':
        actions = [Action.from_dict(action_data) for action_data in data.get('actions', [])]
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            actions=actions,
            scheduled_time=data.get('scheduled_time', ''),
            enabled=data.get('enabled', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'actions': [action.to_dict() for action in self.actions],
            'scheduled_time': self.scheduled_time,
            'enabled': self.enabled
        }


class RoutineManager:
    """Manages routine storage and persistence."""
    
    def __init__(self, config_file: str = "dailyflow_config.json"):
        self.config_file = config_file
        self.routines: List[Routine] = []
        self.load_routines()
    
    def add_routine(self, routine: Routine) -> bool:
        """Add a new routine. Returns False if name already exists."""
        if any(r.name == routine.name for r in self.routines):
            return False
        self.routines.append(routine)
        self.save_routines()
        return True
    
    def update_routine(self, old_name: str, updated_routine: Routine) -> bool:
        """Update an existing routine."""
        for i, routine in enumerate(self.routines):
            if routine.name == old_name:
                self.routines[i] = updated_routine
                self.save_routines()
                return True
        return False
    
    def delete_routine(self, name: str) -> bool:
        """Delete a routine by name."""
        for i, routine in enumerate(self.routines):
            if routine.name == name:
                del self.routines[i]
                self.save_routines()
                return True
        return False
    
    def get_routine(self, name: str) -> Routine:
        """Get a routine by name."""
        for routine in self.routines:
            if routine.name == name:
                return routine
        return None
    
    def get_all_routines(self) -> List[Routine]:
        """Get all routines."""
        return self.routines.copy()
    
    def save_routines(self):
        """Save routines to JSON file."""
        try:
            data = {
                'routines': [routine.to_dict() for routine in self.routines]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving routines: {e}")
    
    def load_routines(self):
        """Load routines from JSON file."""
        if not os.path.exists(self.config_file):
            self.routines = []
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.routines = [Routine.from_dict(routine_data) 
                           for routine_data in data.get('routines', [])]
        except Exception as e:
            print(f"Error loading routines: {e}")
            self.routines = []


def create_sample_routine() -> Routine:
    """Create a sample routine for demonstration."""
    actions = [
        Action(ActionType.SHOW_MESSAGE, {"message": "Good morning! Starting your day..."}),
        Action(ActionType.DELAY, {"seconds": 2}),
        Action(ActionType.OPEN_WEBSITE, {"url": "https://gmail.com"}),
        Action(ActionType.OPEN_APP, {"app_path": "notepad.exe"}),
        Action(ActionType.DELAY, {"seconds": 1}),
        Action(ActionType.SHOW_MESSAGE, {"message": "All set! Have a productive day!"})
    ]
    
    return Routine(
        name="Morning Startup",
        description="Basic morning routine to get started",
        actions=actions
    )