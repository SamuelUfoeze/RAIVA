"""
Project Model - Represents collections of related tasks
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, date
import json

@dataclass
class Project:
    """Project model representing collections of tasks."""
    
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    status: str = "active"  # active, completed, paused, cancelled
    progress: int = 0  # 0-100
    goal_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[date] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_db_row(cls, row) -> 'Project':
        """Create Project instance from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'] or "",
            status=row['status'],
            progress=row['progress'],
            goal_id=row['goal_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            due_date=date.fromisoformat(row['due_date']) if row['due_date'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
