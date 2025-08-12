"""
Goals View - Goal setting and tracking interface
"""

import flet as ft
from src.core.state_manager import StateManager
from src.core.database import DatabaseManager

class GoalsView:
    """Goals view for setting and tracking objectives."""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
        
    async def initialize(self):
        """Initialize the goals view."""
        pass
        
    async def build(self) -> ft.Control:
        """Build the goals UI."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Goals View", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Goal setting and tracking interface coming soon...")
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
