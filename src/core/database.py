"""
Database Manager - Handles all data persistence operations
Implements repository pattern with SQLite for offline-first approach.
"""

import sqlite3
import asyncio
import aiosqlite
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from src.models.goal import Goal
from src.models.task import Task
from src.models.note import Note
from src.models.project import Project
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseManager:
    """
    Database manager implementing repository pattern.
    Handles all data persistence with offline-first approach.
    """
    
    def __init__(self, db_path: str = "personal_os.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        
    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            # Ensure database directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            
            # Create connection
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            
            # Create tables
            await self._create_tables()
            
            # Insert sample data if database is empty
            await self._insert_sample_data()
            
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
            
    async def _create_tables(self) -> None:
        """Create all necessary database tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                timeline TEXT NOT NULL,
                motivation TEXT,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                target_date DATE,
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                goal_id INTEGER,
                project_id INTEGER,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                due_date TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                metadata TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals (id),
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                note_type TEXT DEFAULT 'text',
                source TEXT,
                tags TEXT,
                connections TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                goal_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                metadata TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS knowledge_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                connection_type TEXT DEFAULT 'related',
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                duration INTEGER NOT NULL,
                session_type TEXT DEFAULT 'pomodoro',
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                interruptions INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            await self.connection.execute(table_sql)
            
        await self.connection.commit()
        logger.debug("Database tables created successfully")
        
    async def _insert_sample_data(self) -> None:
        """Insert sample data if database is empty."""
        try:
            # Check if we have any goals
            cursor = await self.connection.execute("SELECT COUNT(*) FROM goals")
            count = await cursor.fetchone()
            
            if count[0] == 0:
                # Insert sample goals
                sample_goals = [
                    ("Launch my online business", "Create and launch a profitable online business", 
                     "career", "1Y", "Financial independence and creative freedom", "active", 25),
                    ("Learn Python programming", "Master Python for data science and web development", 
                     "learning", "6M", "Career advancement and personal growth", "active", 60),
                    ("Improve physical fitness", "Get in the best shape of my life", 
                     "health", "1Y", "Better health and confidence", "active", 40)
                ]
                
                for goal in sample_goals:
                    await self.connection.execute(
                        """INSERT INTO goals (title, description, category, timeline, motivation, status, progress)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""", goal
                    )
                
                # Insert sample tasks
                sample_tasks = [
                    ("Finalize business plan draft", "Complete the executive summary and financial projections", 
                     "high", "pending", 1, 2),
                    ("Schedule meeting with mentor", "Set up monthly mentorship session", 
                     "medium", "pending", 1, 30),
                    ("Research competitors' pricing", "Analyze pricing strategies of top 5 competitors", 
                     "medium", "pending", 1, 60),
                    ("Complete Python course module 3", "Finish data structures and algorithms section", 
                     "high", "pending", 2, 120),
                    ("Morning workout routine", "30-minute cardio and strength training", 
                     "medium", "pending", 3, 30)
                ]
                
                for task in sample_tasks:
                    await self.connection.execute(
                        """INSERT INTO tasks (title, description, priority, status, goal_id, estimated_duration)
                           VALUES (?, ?, ?, ?, ?, ?)""", task
                    )
                
                # Insert sample notes
                sample_notes = [
                    ("Marketing Campaign Ideas", "Social media strategy focusing on Instagram and TikTok to reach our target demographic. Consider influencer partnerships and user-generated content campaigns.", "idea", "brainstorm", "marketing,social"),
                    ("Customer Research Findings", "Key insights from user interviews: 1) Price sensitivity is high among 25-34 age group, 2) Mobile app is preferred over web, 3) Customer support is crucial for retention.", "research", "interviews", "research,customers"),
                    ("Business Plan Draft", "Executive summary completed. Need to flesh out financial projections and market analysis sections. Focus on scalability and competitive advantages.", "document", "planning", "business,planning")
                ]
                
                for note in sample_notes:
                    await self.connection.execute(
                        """INSERT INTO notes (title, content, note_type, source, tags)
                           VALUES (?, ?, ?, ?, ?)""", note
                    )
                
                await self.connection.commit()
                logger.info("Sample data inserted successfully")
                
        except Exception as e:
            logger.error(f"Failed to insert sample data: {e}")
            
    # Goal operations
    async def create_goal(self, goal: Goal) -> int:
        """Create a new goal and return its ID."""
        try:
            cursor = await self.connection.execute(
                """INSERT INTO goals (title, description, category, timeline, motivation, target_date, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (goal.title, goal.description, goal.category, goal.timeline, 
                 goal.motivation, goal.target_date, json.dumps(goal.metadata))
            )
            await self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            raise
            
    async def get_goals(self, status: Optional[str] = None) -> List[Goal]:
        """Retrieve goals, optionally filtered by status."""
        try:
            if status:
                cursor = await self.connection.execute(
                    "SELECT * FROM goals WHERE status = ? ORDER BY created_at DESC", (status,)
                )
            else:
                cursor = await self.connection.execute(
                    "SELECT * FROM goals ORDER BY created_at DESC"
                )
            
            rows = await cursor.fetchall()
            return [Goal.from_db_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve goals: {e}")
            return []
            
    async def update_goal_progress(self, goal_id: int, progress: int) -> bool:
        """Update goal progress."""
        try:
            await self.connection.execute(
                "UPDATE goals SET progress = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (progress, goal_id)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update goal progress: {e}")
            return False
            
    # Task operations
    async def create_task(self, task: Task) -> int:
        """Create a new task and return its ID."""
        try:
            cursor = await self.connection.execute(
                """INSERT INTO tasks (title, description, priority, goal_id, project_id, 
                   estimated_duration, due_date, tags, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task.title, task.description, task.priority, task.goal_id, 
                 task.project_id, task.estimated_duration, task.due_date,
                 ','.join(task.tags) if task.tags else None, json.dumps(task.metadata))
            )
            await self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
            
    async def get_tasks(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Task]:
        """Retrieve tasks, optionally filtered by status."""
        try:
            query = "SELECT * FROM tasks"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
                
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            return [Task.from_db_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {e}")
            return []
            
    async def get_today_tasks(self) -> List[Task]:
        """Get tasks for today based on priority and due dates."""
        try:
            today = datetime.now().date()
            cursor = await self.connection.execute(
                """SELECT * FROM tasks 
                   WHERE status = 'pending' 
                   AND (due_date IS NULL OR date(due_date) &lt;= ?)
                   ORDER BY 
                     CASE priority 
                       WHEN 'high' THEN 1 
                       WHEN 'medium' THEN 2 
                       WHEN 'low' THEN 3 
                     END,
                     created_at DESC
                   LIMIT 10""",
                (today,)
            )
            rows = await cursor.fetchall()
            return [Task.from_db_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve today's tasks: {e}")
            return []
            
    async def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        try:
            await self.connection.execute(
                """UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (task_id,)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
            
    # Note operations
    async def create_note(self, note: Note) -> int:
        """Create a new note and return its ID."""
        try:
            cursor = await self.connection.execute(
                """INSERT INTO notes (title, content, note_type, source, tags, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (note.title, note.content, note.note_type, note.source,
                 ','.join(note.tags) if note.tags else None, json.dumps(note.metadata))
            )
            await self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            raise
            
    async def get_notes(self, limit: Optional[int] = None) -> List[Note]:
        """Retrieve notes."""
        try:
            query = "SELECT * FROM notes ORDER BY created_at DESC"
            params = []
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            return [Note.from_db_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve notes: {e}")
            return []
            
    # Analytics operations
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        try:
            stats = {}
            
            # Task counts
            cursor = await self.connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = 'pending'"
            )
            stats['tasks_today'] = (await cursor.fetchone())[0]
            
            # Active goals count
            cursor = await self.connection.execute(
                "SELECT COUNT(*) FROM goals WHERE status = 'active'"
            )
            stats['active_goals'] = (await cursor.fetchone())[0]
            
            # Notes this week
            week_ago = datetime.now() - timedelta(days=7)
            cursor = await self.connection.execute(
                "SELECT COUNT(*) FROM notes WHERE created_at >= ?", (week_ago,)
            )
            stats['notes_this_week'] = (await cursor.fetchone())[0]
            
            # Focus score (mock calculation)
            stats['focus_score'] = 85  # This would be calculated based on actual focus sessions
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {}
            
    async def close(self) -> None:
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
