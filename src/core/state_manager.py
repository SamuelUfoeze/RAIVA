"""
State Manager - Centralized state management for the application
Implements observer pattern for reactive UI updates.
"""

from typing import Dict, Any, List, Callable, Optional
import asyncio
from datetime import datetime
from src.core.database import DatabaseManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StateManager:
    """
    Centralized state manager implementing observer pattern.
    Manages application state and notifies observers of changes.
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._observers: Dict[str, List[Callable]] = {}
        self._db_manager: Optional[DatabaseManager] = None
        
    async def initialize(self, db_manager: DatabaseManager) -> None:
        """Initialize state manager with database connection."""
        self._db_manager = db_manager
        await self._load_initial_state()
        logger.info("State manager initialized")
        
    async def _load_initial_state(self) -> None:
        """Load initial state from database."""
        try:
            # Load dashboard stats
            stats = await self._db_manager.get_dashboard_stats()
            self._state['dashboard_stats'] = stats
            
            # Load user preferences
            self._state['user_preferences'] = {
                'theme': 'light',
                'notifications_enabled': True,
                'focus_duration': 25,  # Pomodoro default
                'break_duration': 5
            }
            
            # Load current user info (mock data)
            self._state['current_user'] = {
                'name': 'Alex Johnson',
                'plan': 'Free Plan',
                'storage_used': 85
            }
            
            logger.debug("Initial state loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load initial state: {e}")
            
    def subscribe(self, key: str, callback: Callable) -> None:
        """Subscribe to state changes for a specific key."""
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(callback)
        
    def unsubscribe(self, key: str, callback: Callable) -> None:
        """Unsubscribe from state changes."""
        if key in self._observers and callback in self._observers[key]:
            self._observers[key].remove(callback)
            
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value by key."""
        return self._state.get(key, default)
        
    async def set_state(self, key: str, value: Any) -> None:
        """Set state value and notify observers."""
        old_value = self._state.get(key)
        self._state[key] = value
        
        # Notify observers if value changed
        if old_value != value:
            await self._notify_observers(key, value, old_value)
            
    async def update_state(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values."""
        for key, value in updates.items():
            await self.set_state(key, value)
            
    async def _notify_observers(self, key: str, new_value: Any, old_value: Any) -> None:
        """Notify all observers of state change."""
        if key in self._observers:
            for callback in self._observers[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(key, new_value, old_value)
                    else:
                        callback(key, new_value, old_value)
                except Exception as e:
                    logger.error(f"Observer callback error: {e}")
                    
    async def refresh_dashboard_stats(self) -> None:
        """Refresh dashboard statistics from database."""
        if self._db_manager:
            stats = await self._db_manager.get_dashboard_stats()
            await self.set_state('dashboard_stats', stats)
            
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get current dashboard statistics."""
        return self.get_state('dashboard_stats', {})
        
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        return self.get_state('current_user', {})
        
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return self.get_state('user_preferences', {})
