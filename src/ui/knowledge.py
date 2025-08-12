"""
Knowledge View - Knowledge base and graph interface
"""

import flet as ft
from src.core.state_manager import StateManager
from src.core.database import DatabaseManager

class KnowledgeView:
    """Knowledge view for managing knowledge base."""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
        
    async def initialize(self):
        """Initialize the knowledge view."""
        pass
        
    async def build(self) -> ft.Control:
        """Build the knowledge UI."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Knowledge Base", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Knowledge graph and notes interface coming soon...")
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
