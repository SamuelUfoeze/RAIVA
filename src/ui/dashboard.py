"""
Dashboard View - Main application dashboard
Shows personalized greeting, stats, and priority tasks.
"""

import flet as ft
from typing import Optional, Dict, Any
from datetime import datetime
from src.core.state_manager import StateManager
from src.core.database import DatabaseManager

class DashboardView:
    """Dashboard view showing user stats and priority items."""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
        self.stats: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the dashboard view."""
        # Refresh stats
        await self.state_manager.refresh_dashboard_stats()
        self.stats = self.state_manager.get_dashboard_stats()
        
    async def build(self) -> ft.Control:
        """Build the dashboard UI."""
        # Get current time for greeting
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        user_info = self.state_manager.get_user_info()
        user_name = user_info.get('name', 'User')
        
        # Create dashboard content
        return ft.Container(
            content=ft.Column([
                # Header section
                self._create_header_section(greeting, user_name),
                
                # Stats cards
                self._create_stats_section(),
                
                # Main content area
                ft.Row([
                    # Left column - Today's priorities
                    ft.Container(
                        content=self._create_priorities_section(),
                        width=400,
                        padding=20
                    ),
                    
                    # Right column - Recent captures and insights
                    ft.Container(
                        content=self._create_insights_section(),
                        expand=True,
                        padding=20
                    )
                ], expand=True)
                
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _create_header_section(self, greeting: str, user_name: str) -> ft.Control:
        """Create the header section with greeting and quick stats."""
        today = datetime.now().strftime("%A, %d %B")
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"{greeting}, {user_name}", 
                           size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(f"{today} • You have {self.stats.get('tasks_today', 0)} tasks for today",
                           size=16, color=ft.colors.WHITE70),
                    
                    # Quick stats row
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.WHITE, size=20),
                                ft.Column([
                                    ft.Text("AI Insight", size=12, color=ft.colors.WHITE70),
                                    ft.Text("You're most productive between 9-11 AM", 
                                           size=14, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
                                ], spacing=2)
                            ], spacing=10),
                            padding=15,
                            bgcolor=ft.colors.WHITE12,
                            border_radius=10
                        ),
                        
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.BOLT, color=ft.colors.WHITE, size=20),
                                ft.Column([
                                    ft.Text("Focus Score", size=12, color=ft.colors.WHITE70),
                                    ft.Text(f"{self.stats.get('focus_score', 85)}% (↑12% from last week)", 
                                           size=14, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
                                ], spacing=2)
                            ], spacing=10),
                            padding=15,
                            bgcolor=ft.colors.WHITE12,
                            border_radius=10
                        )
                    ], spacing=15)
                    
                ], spacing=15, expand=True),
                
                # Decorative illustration placeholder
                ft.Container(
                    content=ft.Icon(ft.icons.DASHBOARD, size=80, color=ft.colors.WHITE30),
                    width=120,
                    height=120,
                    bgcolor=ft.colors.WHITE12,
                    border_radius=15,
                    alignment=ft.alignment.center
                )
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=30,
            bgcolor=ft.colors.PURPLE,
            border_radius=15,
            gradient=ft.LinearGradient([
                ft.colors.PURPLE_400,
                ft.colors.PURPLE_600
            ])
        )
    
    def _create_stats_section(self) -> ft.Control:
        """Create the stats cards section."""
        return ft.Row([
            self._create_stat_card("Tasks Today", str(self.stats.get('tasks_today', 0)), 
                                 ft.icons.CHECK_CIRCLE, ft.colors.GREEN),
            self._create_stat_card("Active Goals", str(self.stats.get('active_goals', 0)), 
                                 ft.icons.TARGET, ft.colors.ORANGE),
            self._create_stat_card("Notes This Week", str(self.stats.get('notes_this_week', 0)), 
                                 ft.icons.NOTE, ft.colors.BLUE),
            self._create_stat_card("Focus Score", f"{self.stats.get('focus_score', 85)}%", 
                                 ft.icons.BOLT, ft.colors.PURPLE)
        ], spacing=15)
    
    def _create_stat_card(self, title: str, value: str, icon: str, color: str) -> ft.Control:
        """Create a single stat card."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=24),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(title, size=14, color=ft.colors.GREY_600)
            ], spacing=10),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_200),
            expand=True,
            height=100
        )
    
    def _create_priorities_section(self) -> ft.Control:
        """Create today's priorities section."""
        return ft.Column([
            ft.Row([
                ft.Icon(ft.icons.TODAY, color=ft.colors.ORANGE),
                ft.Text("Top 3 Today", size=18, weight=ft.FontWeight.BOLD),
                ft.TextButton("See All", on_click=lambda _: print("See all tasks"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Priority tasks
            self._create_task_item("Finalize business plan draft", "High Priority", "2 hours", 3),
            self._create_task_item("Schedule meeting with mentor", "Medium Priority", "30 min", 1),
            self._create_task_item("Research competitors' pricing", "Medium Priority", "1 hour", 5),
            
            # Recent captures section
            ft.Divider(height=20),
            ft.Row([
                ft.Icon(ft.icons.CAPTURE, color=ft.colors.GREEN),
                ft.Text("Recent Captures", size=18, weight=ft.FontWeight.BOLD),
                ft.TextButton("See All", on_click=lambda _: print("See all captures"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            self._create_capture_item("Voice Note", "Ideas for marketing campaign...", "2m ago", "Processed"),
            self._create_capture_item("Image", "Screenshot of competitor website", "15m ago", "Processing...")
            
        ], spacing=15)
    
    def _create_task_item(self, title: str, priority: str, duration: str, connections: int) -> ft.Control:
        """Create a task item."""
        priority_color = ft.colors.RED if "High" in priority else ft.colors.ORANGE if "Medium" in priority else ft.colors.GREEN
        
        return ft.Container(
            content=ft.Row([
                ft.Checkbox(value=False, on_change=lambda _: print(f"Task toggled: {title}")),
                ft.Column([
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(priority, size=12, color=ft.colors.WHITE),
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=priority_color,
                            border_radius=10
                        ),
                        ft.Text(duration, size=12, color=ft.colors.GREY_600),
                        ft.Row([
                            ft.Icon(ft.icons.LINK, size=12, color=ft.colors.GREY_600),
                            ft.Text(str(connections), size=12, color=ft.colors.GREY_600)
                        ], spacing=2)
                    ], spacing=8)
                ], spacing=5, expand=True),
                ft.IconButton(ft.icons.ARROW_FORWARD_IOS, 
                            icon_size=16, 
                            on_click=lambda _: print(f"Open task: {title}"))
            ], alignment=ft.CrossAxisAlignment.START),
            padding=15,
            bgcolor=ft.colors.GREY_50,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_200)
        )
    
    def _create_capture_item(self, type_name: str, description: str, time: str, status: str) -> ft.Control:
        """Create a capture item."""
        icon = ft.icons.MIC if type_name == "Voice Note" else ft.icons.IMAGE
        status_color = ft.colors.GREEN if status == "Processed" else ft.colors.ORANGE
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=ft.colors.WHITE, size=16),
                    width=32,
                    height=32,
                    bgcolor=ft.colors.GREEN if type_name == "Voice Note" else ft.colors.BLUE,
                    border_radius=8,
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(type_name, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color=ft.colors.GREY_600),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(status, size=10, color=ft.colors.WHITE),
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            bgcolor=status_color,
                            border_radius=8
                        ),
                        ft.Text(time, size=12, color=ft.colors.GREY_500)
                    ], spacing=8)
                ], spacing=2, expand=True),
                ft.IconButton(ft.icons.ARROW_FORWARD_IOS, 
                            icon_size=16, 
                            on_click=lambda _: print(f"Open capture: {type_name}"))
            ], alignment=ft.CrossAxisAlignment.START),
            padding=15,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_200)
        )
    
    def _create_insights_section(self) -> ft.Control:
        """Create the insights and connections section."""
        return ft.Column([
            # New connections section
            ft.Row([
                ft.Icon(ft.icons.LIGHTBULB, color=ft.colors.YELLOW_700),
                ft.Text("New Connections", size=18, weight=ft.FontWeight.BOLD),
                ft.TextButton("View Graph", on_click=lambda _: print("View knowledge graph"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.PURPLE, size=20),
                        ft.Text("AI found 3 new connections", size=14, weight=ft.FontWeight.BOLD)
                    ], spacing=10),
                    ft.Text("Based on your recent captures", size=12, color=ft.colors.GREY_600),
                    
                    ft.Divider(height=10),
                    
                    # Connection items
                    self._create_connection_item("Marketing Ideas", "Connects to your Business Plan", ft.colors.ORANGE),
                    self._create_connection_item("Customer Research", "Links to 3 existing projects", ft.colors.BLUE),
                    self._create_connection_item("Competitor Analysis", "Related to pricing strategy", ft.colors.GREEN)
                    
                ], spacing=10),
                padding=20,
                bgcolor=ft.colors.GREY_50,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_200)
            )
            
        ], spacing=15)
    
    def _create_connection_item(self, title: str, description: str, color: str) -> ft.Control:
        """Create a connection item."""
        return ft.Row([
            ft.Container(
                content=ft.Icon(ft.icons.LINK, color=ft.colors.WHITE, size=12),
                width=24,
                height=24,
                bgcolor=color,
                border_radius=12,
                alignment=ft.alignment.center
            ),
            ft.Column([
                ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=11, color=ft.colors.GREY_600)
            ], spacing=2, expand=True),
            ft.IconButton(ft.icons.ARROW_FORWARD_IOS, 
                        icon_size=12, 
                        on_click=lambda _: print(f"Open connection: {title}"))
        ], alignment=ft.CrossAxisAlignment.CENTER)
