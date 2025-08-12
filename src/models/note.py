"""
Note Model - Represents captured ideas and information
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

@dataclass
class Note:
    """Note model representing captured information."""
    
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    note_type: str = "text"  # text, voice, image, link, document
    source: str = ""  # whatsapp, manual, web_clip, etc.
    tags: List[str] = field(default_factory=list)
    connections: List[int] = field(default_factory=list)  # IDs of connected items
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_db_row(cls, row) -> 'Note':
        """Create Note instance from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            note_type=row['note_type'],
            source=row['source'] or "",
            tags=row['tags'].split(',') if row['tags'] else [],
            connections=json.loads(row['connections']) if row['connections'] else [],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
