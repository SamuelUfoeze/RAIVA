"""
Navigation Manager - Handles app navigation and responsive layout
"""

import flet as ft
from typing import Dict, Any, Callable, Optional

class NavigationManager:
    """Manages application navigation and responsive layout."""
    
    def __init__(self, page: ft.Page, views: Dict[str, Any], on_navigate: Callable):
        self.page = page
        self.views = views
        self.on_navigate = on_navigate
        self.current_route = "dashboard"
        
    def create_layout(self, content: ft.Control, current_route: str) -> ft.Control:
        """Create the main layout with navigation."""
        self.current_route = current_route
        
        # Check if mobile layout
        is_mobile = self.page.window_width < 768 if self.page.window_width else False
        
        if is_mobile:
            return self._create_mobile_layout(content)
        else:
            return self._create_desktop_layout(content)
    
    def _create_desktop_layout(self, content: ft.Control) -> ft.Control:
        """Create desktop layout with sidebar."""
        return ft.Row([
            # Sidebar
            ft.Container(
                content=self._create_sidebar(),
                width=250,
                bgcolor=ft.colors.GREY_50,
                border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.GREY_200))
            ),
            # Main content
            ft.Container(
                content=content,
                expand=True,
                bgcolor=ft.colors.WHITE
            )
        ], expand=True, spacing=0)
    
    def _create_mobile_layout(self, content: ft.Control) -> ft.Control:
        """Create mobile layout with bottom navigation."""
        return ft.Column([
            # Main content
            ft.Container(
                content=content,
                expand=True,
                bgcolor=ft.colors.WHITE
            ),
            # Bottom navigation
            self._create_bottom_navigation()
        ], spacing=0)
    
    def _create_sidebar(self) -> ft.Control:
        """Create desktop sidebar navigation."""
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("P", color=ft.colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
                        width=40,
                        height=40,
                        bgcolor=ft.colors.PURPLE,
                        border_radius=20,
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text("Personal OS", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Your second brain", size=12, color=ft.colors.GREY_600)
                    ], spacing=2)
                ], spacing=10),
                padding=20
            ),
            
            # User info
            ft.Container(
                content=ft.Row([
                    ft.CircleAvatar(
                        content=ft.Text("AJ", color=ft.colors.WHITE),
                        bgcolor=ft.colors.BLUE,
                        radius=20
                    ),
                    ft.Column([
                        ft.Text("Alex Johnson", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Free Plan • 85% storage", size=12, color=ft.colors.GREY_600)
                    ], spacing=2)
                ], spacing=10),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                bgcolor=ft.colors.WHITE,
                margin=ft.margin.symmetric(horizontal=10),
                border_radius=10
            ),
            
            # Search
            ft.Container(
                content=ft.TextField(
                    hint_text="Search...",
                    prefix_icon=ft.icons.SEARCH,
                    border=ft.InputBorder.OUTLINE,
                    dense=True
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            ),
            
            # Navigation items
            ft.Column([
                self._create_nav_item("Dashboard", ft.icons.DASHBOARD, "dashboard"),
                self._create_nav_item("Knowledge Graph", ft.icons.ACCOUNT_TREE, "knowledge"),
                self._create_nav_item("Goals & Projects", ft.icons.TARGET, "goals"),
                self._create_nav_item("Tasks", ft.icons.CHECK_BOX, "tasks"),
                self._create_nav_item("Focus Timer", ft.icons.TIMER, "focus"),
                self._create_nav_item("Analytics", ft.icons.ANALYTICS, "analytics")
            ], spacing=5),
            
            # Recent items
            ft.Container(
                content=ft.Column([
                    ft.Text("RECENT ITEMS", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_600),
                    self._create_recent_item("Marketing Campaign", ft.icons.CAMPAIGN, ft.colors.ORANGE),
                    self._create_recent_item("Business Plan", ft.icons.BUSINESS, ft.colors.GREEN),
                    self._create_recent_item("Finalize draft", ft.icons.CHECK, ft.colors.BLUE)
                ], spacing=10),
                padding=20
            ),
            
            # Quick capture button
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.ADD, color=ft.colors.WHITE),
                        ft.Text("Quick Capture", color=ft.colors.WHITE)
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.colors.PURPLE,
                    color=ft.colors.WHITE,
                    on_click=lambda _: print("Quick capture clicked")
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
            
        ], spacing=10, expand=True)
    
    def _create_nav_item(self, title: str, icon: str, route: str) -> ft.Control:
        """Create a navigation item."""
        is_active = self.current_route == route
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, 
                       color=ft.colors.PURPLE if is_active else ft.colors.GREY_600,
                       size=20),
                ft.Text(title, 
                       color=ft.colors.PURPLE if is_active else ft.colors.GREY_700,
                       weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL)
            ], spacing=15),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=ft.colors.PURPLE_50 if is_active else None,
            border_radius=10,
            margin=ft.margin.symmetric(horizontal=10),
            on_click=lambda _, r=route: self.on_navigate(r)
        )
    
    def _create_recent_item(self, title: str, icon: str, color: str) -> ft.Control:
        """Create a recent item."""
        return ft.Row([
            ft.Container(
                content=ft.Icon(icon, color=ft.colors.WHITE, size=12),
                width=24,
                height=24,
                bgcolor=color,
                border_radius=6,
                alignment=ft.alignment.center
            ),
            ft.Text(title, size=13, expand=True)
        ], spacing=10)
    
    def _create_bottom_navigation(self) -> ft.Control:
        """Create mobile bottom navigation."""
        return ft.Container(
            content=ft.Row([
                self._create_bottom_nav_item("Today", ft.icons.TODAY, "dashboard"),
                self._create_bottom_nav_item("Notes", ft.icons.NOTE, "knowledge"),
                self._create_bottom_nav_item("Goals", ft.icons.TARGET, "goals"),
                self._create_bottom_nav_item("Focus", ft.icons.TIMER, "focus"),
                self._create_bottom_nav_item("Profile", ft.icons.PERSON, "profile")
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            height=80,
            bgcolor=ft.colors.WHITE,
            border=ft.border.only(top=ft.border.BorderSide(1, ft.colors.GREY_200)),
            padding=ft.padding.symmetric(vertical=10)
        )
    
    def _create_bottom_nav_item(self, title: str, icon: str, route: str) -> ft.Control:
        """Create a bottom navigation item."""
        is_active = self.current_route == route
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, 
                       color=ft.colors.PURPLE if is_active else ft.colors.GREY_600,
                       size=24),
                ft.Text(title, 
                       size=12,
                       color=ft.colors.PURPLE if is_active else ft.colors.GREY_600,
                       weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            on_click=lambda _, r=route: self.on_navigate(r),
            padding=10
        )
    
    def update_responsive_layout(self):
        """Update layout based on screen size changes."""
        # This would be called on window resize
        pass
