"""
Tasks View - Task management interface
"""

import flet as ft
from src.core.state_manager import StateManager
from src.core.database import DatabaseManager

class TasksView:
    """Tasks view for managing user tasks."""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
        
    async def initialize(self):
        """Initialize the tasks view."""
        pass
        
    async def build(self) -> ft.Control:
        """Build the tasks UI."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Tasks View", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Task management interface coming soon...")
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
