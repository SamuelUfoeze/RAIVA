"""
Goal Model - Represents user goals and objectives
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import json

@dataclass
class Goal:
    """Goal model representing user objectives."""
    
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    category: str = "personal"  # career, health, learning, finance, social, personal
    timeline: str = "1Y"  # 1M, 3M, 6M, 1Y, 5Y
    motivation: str = ""
    status: str = "active"  # active, completed, paused, cancelled
    progress: int = 0  # 0-100
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    target_date: Optional[date] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_db_row(cls, row) -> 'Goal':
        """Create Goal instance from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'] or "",
            category=row['category'],
            timeline=row['timeline'],
            motivation=row['motivation'] or "",
            status=row['status'],
            progress=row['progress'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            target_date=date.fromisoformat(row['target_date']) if row['target_date'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'timeline': self.timeline,
            'motivation': self.motivation,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'metadata': self.metadata
        }
