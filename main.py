"""
Main entry point for DailyFlow application.
"""
import sys
import argparse
from main_window import main as gui_main
from models import RoutineManager
from action_executor import ActionExecutor


def run_routine_cli(routine_name: str):
    """Run a routine from command line (for scheduled execution)."""
    print(f"DailyFlow: Starting routine '{routine_name}'")
    
    # Load routine manager
    routine_manager = RoutineManager()
    routine = routine_manager.get_routine(routine_name)
    
    if not routine:
        print(f"Error: Routine '{routine_name}' not found.")
        return 1
    
    if not routine.enabled:
        print(f"Error: Routine '{routine_name}' is disabled.")
        return 1
    
    if not routine.actions:
        print(f"Error: Routine '{routine_name}' has no actions.")
        return 1
    
    # Execute routine actions
    print(f"Executing {len(routine.actions)} actions...")
    
    # Create a simple synchronous executor for CLI
    from action_executor import ActionExecutor
    
    class CLIExecutor:
        def execute_routine(self, actions):
            for i, action in enumerate(actions, 1):
                if not action.enabled:
                    print(f"  [{i}] Skipping disabled action")
                    continue
                    
                print(f"  [{i}] {self._get_action_description(action)}")
                
                # Create a temporary GUI app context for actions that need it
                from PySide6.QtWidgets import QApplication
                if not QApplication.instance():
                    app = QApplication([])
                
                executor = ActionExecutor()
                success = executor._execute_single_action(action)
                
                if success:
                    print(f"      [OK] Completed")
                else:
                    print(f"      [FAIL] Failed")
        
        def _get_action_description(self, action):
            executor = ActionExecutor()
            return executor._get_action_description(action)
    
    cli_executor = CLIExecutor()
    cli_executor.execute_routine(routine.actions)
    
    print("*** Routine completed! ***")
    return 0


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="DailyFlow - Morning Routine Automation")
    parser.add_argument(
        "--routine", 
        help="Run a specific routine by name (for scheduled execution)"
    )
    parser.add_argument(
        "--list-routines", 
        action="store_true",
        help="List all available routines"
    )
    
    args = parser.parse_args()
    
    if args.list_routines:
        # List available routines
        routine_manager = RoutineManager()
        routines = routine_manager.get_all_routines()
        
        if not routines:
            print("No routines found.")
            return 0
        
        print("Available routines:")
        for routine in routines:
            status = "enabled" if routine.enabled else "disabled"
            scheduled = f" (scheduled at {routine.scheduled_time})" if routine.scheduled_time else ""
            print(f"  - {routine.name} [{status}]{scheduled}")
            if routine.description:
                print(f"    {routine.description}")
        return 0
    
    if args.routine:
        # Run specific routine from command line
        return run_routine_cli(args.routine)
    
    # No arguments provided, start GUI
    gui_main()


if __name__ == "__main__":
    main()