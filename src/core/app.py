"""
Main Application Class - Central coordinator for the Personal OS
Implements clean architecture with separation of concerns.
"""

import flet as ft
from typing import Optional, Dict, Any
from src.ui.navigation import NavigationManager
from src.ui.dashboard import DashboardView
from src.ui.tasks import TasksView
from src.ui.goals import GoalsView
from src.ui.knowledge import KnowledgeView
from src.ui.focus import FocusView
from src.ui.analytics import AnalyticsView
from src.core.database import DatabaseManager
from src.core.state_manager import StateManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PersonalOSApp:
    """
    Main application class following single responsibility principle.
    Coordinates between UI, data, and business logic layers.
    """
    
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db_manager = db_manager
        self.state_manager = StateManager()
        self.navigation_manager: Optional[NavigationManager] = None
        self.current_view: Optional[ft.Control] = None
        self.views: Dict[str, Any] = {}
        
        # Configure page settings
        self._configure_page()
        
    def _configure_page(self) -> None:
        """Configure page settings for responsive design."""
        self.page.title = "Personal Operating System"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.spacing = 0
        
        # Responsive design settings
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 320
        self.page.window_min_height = 568
        
        # Theme configuration
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.PURPLE,
            use_material3=True
        )
        
    async def initialize(self) -> None:
        """Initialize the application components."""
        try:
            logger.info("Initializing Personal OS application...")
            
            # Initialize state manager
            await self.state_manager.initialize(self.db_manager)
            
            # Initialize views
            await self._initialize_views()
            
            # Setup navigation
            self.navigation_manager = NavigationManager(
                page=self.page,
                views=self.views,
                on_navigate=self._handle_navigation
            )
            
            # Load initial view
            await self._load_dashboard()
            
            # Setup page resize handler
            self.page.on_resize = self._handle_resize
            
            logger.info("Personal OS application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
            
    async def _initialize_views(self) -> None:
        """Initialize all application views."""
        try:
            self.views = {
                "dashboard": DashboardView(self.state_manager, self.db_manager),
                "tasks": TasksView(self.state_manager, self.db_manager),
                "goals": GoalsView(self.state_manager, self.db_manager),
                "knowledge": KnowledgeView(self.state_manager, self.db_manager),
                "focus": FocusView(self.state_manager, self.db_manager),
                "analytics": AnalyticsView(self.state_manager, self.db_manager)
            }
            
            # Initialize each view
            for view_name, view in self.views.items():
                await view.initialize()
                logger.debug(f"Initialized {view_name} view")
                
        except Exception as e:
            logger.error(f"Failed to initialize views: {e}")
            raise
            
    async def _load_dashboard(self) -> None:
        """Load the dashboard as the initial view."""
        await self._handle_navigation("dashboard")
        
    async def _handle_navigation(self, route: str) -> None:
        """Handle navigation between views."""
        try:
            if route not in self.views:
                logger.warning(f"Unknown route: {route}")
                return
                
            # Get the target view
            target_view = self.views[route]
            
            # Update current view
            if self.current_view:
                self.page.controls.clear()
                
            # Build the new view
            view_content = await target_view.build()
            
            # Create layout with navigation
            layout = self.navigation_manager.create_layout(view_content, route)
            
            # Update page
            self.page.controls = [layout]
            self.current_view = view_content
            
            # Update page
            self.page.update()
            
            logger.debug(f"Navigated to {route}")
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            await self._show_error_dialog(f"Navigation failed: {str(e)}")
            
    def _handle_resize(self, e) -> None:
        """Handle page resize events for responsive design."""
        try:
            # Update navigation layout based on screen size
            if self.navigation_manager:
                self.navigation_manager.update_responsive_layout()
                self.page.update()
                
        except Exception as e:
            logger.error(f"Resize handling error: {e}")
            
    async def _show_error_dialog(self, message: str) -> None:
        """Show error dialog to user."""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog())
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def _close_dialog(self) -> None:
        """Close the current dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
