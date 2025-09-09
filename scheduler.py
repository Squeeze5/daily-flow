"""
Scheduler integration for DailyFlow.
Handles scheduling routines to run at specific times.
"""
import os
import sys
import subprocess
from typing import List, Optional
from models import Routine


class SchedulerManager:
    """Manages scheduling routines using Windows Task Scheduler."""
    
    def __init__(self):
        self.task_prefix = "DailyFlow_"
        self.app_path = os.path.abspath(sys.argv[0])
        
    def schedule_routine(self, routine: Routine) -> bool:
        """Schedule a routine to run at a specific time."""
        if not routine.scheduled_time:
            return False
        
        task_name = f"{self.task_prefix}{routine.name.replace(' ', '_')}"
        
        try:
            # Create a batch script to run the routine
            script_path = self._create_runner_script(routine.name)
            
            # Create the scheduled task using schtasks
            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'"{script_path}"',
                '/sc', 'daily',
                '/st', routine.scheduled_time,
                '/f'  # Force create/overwrite
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error scheduling routine {routine.name}: {e}")
            return False
    
    def unschedule_routine(self, routine_name: str) -> bool:
        """Remove a scheduled routine."""
        task_name = f"{self.task_prefix}{routine_name.replace(' ', '_')}"
        
        try:
            cmd = ['schtasks', '/delete', '/tn', task_name, '/f']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Also remove the runner script
            script_path = os.path.join(os.path.dirname(self.app_path), f"run_{routine_name.replace(' ', '_')}.bat")
            if os.path.exists(script_path):
                os.remove(script_path)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error unscheduling routine {routine_name}: {e}")
            return False
    
    def update_routine_schedule(self, old_name: str, routine: Routine) -> bool:
        """Update the schedule for a routine."""
        # Remove old schedule
        self.unschedule_routine(old_name)
        
        # Add new schedule if time is specified
        if routine.scheduled_time:
            return self.schedule_routine(routine)
        return True
    
    def get_scheduled_routines(self) -> List[str]:
        """Get list of currently scheduled routine names."""
        try:
            cmd = ['schtasks', '/query', '/fo', 'csv']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            scheduled_routines = []
            for line in result.stdout.split('\\n')[1:]:  # Skip header
                if line.strip() and self.task_prefix in line:
                    # Extract task name and convert back to routine name
                    task_name = line.split(',')[0].strip('"')
                    if task_name.startswith(self.task_prefix):
                        routine_name = task_name[len(self.task_prefix):].replace('_', ' ')
                        scheduled_routines.append(routine_name)
            
            return scheduled_routines
            
        except Exception as e:
            print(f"Error getting scheduled routines: {e}")
            return []
    
    def _create_runner_script(self, routine_name: str) -> str:
        """Create a batch script to run a specific routine."""
        script_name = f"run_{routine_name.replace(' ', '_')}.bat"
        script_path = os.path.join(os.path.dirname(self.app_path), script_name)
        
        # Get the directory of the main script
        app_dir = os.path.dirname(self.app_path)
        
        # Create batch script content
        script_content = f'''@echo off
cd /d "{app_dir}"
python main.py --routine "{routine_name}"
'''
        
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            return script_path
        except Exception as e:
            print(f"Error creating runner script: {e}")
            return ""
    
    def is_task_scheduler_available(self) -> bool:
        """Check if Windows Task Scheduler is available."""
        try:
            result = subprocess.run(['schtasks', '/?'], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False


class SimpleScheduler:
    """Simple in-app scheduler for basic scheduling needs."""
    
    def __init__(self):
        self.scheduled_routines = {}
        
    def schedule_routine(self, routine: Routine, callback) -> bool:
        """Schedule a routine to run at a specific time (in-app only)."""
        if not routine.scheduled_time:
            return False
            
        # This would need to be implemented with QTimer for in-app scheduling
        # For now, this is a placeholder for future enhancement
        self.scheduled_routines[routine.name] = {
            'time': routine.scheduled_time,
            'callback': callback
        }
        return True
    
    def unschedule_routine(self, routine_name: str) -> bool:
        """Remove a scheduled routine."""
        if routine_name in self.scheduled_routines:
            del self.scheduled_routines[routine_name]
            return True
        return False
    
    def get_scheduled_routines(self) -> List[str]:
        """Get list of scheduled routine names."""
        return list(self.scheduled_routines.keys())