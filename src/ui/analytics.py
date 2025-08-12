"""
Analytics View - Analytics and insights interface
"""

import flet as ft
from src.core.state_manager import StateManager
from src.core.database import DatabaseManager

class AnalyticsView:
    """Analytics view for productivity insights."""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
        
    async def initialize(self):
        """Initialize the analytics view."""
        pass
        
    async def build(self) -> ft.Control:
        """Build the analytics UI."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Analytics", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Productivity analytics and insights coming soon...")
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
