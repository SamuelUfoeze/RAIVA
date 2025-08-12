"""
Task Model - Represents actionable tasks
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

@dataclass
class Task:
    """Task model representing actionable items."""
    
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    priority: str = "medium"  # high, medium, low
    status: str = "pending"  # pending, in_progress, completed, cancelled
    goal_id: Optional[int] = None
    project_id: Optional[int] = None
    estimated_duration: Optional[int] = None  # minutes
    actual_duration: Optional[int] = None  # minutes
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_db_row(cls, row) -> 'Task':
        """Create Task instance from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'] or "",
            priority=row['priority'],
            status=row['status'],
            goal_id=row['goal_id'],
            project_id=row['project_id'],
            estimated_duration=row['estimated_duration'],
            actual_duration=row['actual_duration'],
            due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            tags=row['tags'].split(',') if row['tags'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
