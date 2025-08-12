import flet as ft
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio

class SimpleDB:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.init_db()
        self.populate_sample_data()
    
    def init_db(self):
        # Create tables
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                timeline TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                goal_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            )
        ''')
        
        # Added notes table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'Ideas',
                color TEXT DEFAULT '#FFFFFF',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT,
                status TEXT DEFAULT 'processing',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()

    def populate_sample_data(self):
        # Sample goals
        goals = [
            ("Launch my online business", "Create and launch a profitable online business", "Career", "1Y"),
            ("Learn Python programming", "Master Python for data analysis and automation", "Learning", "6M"),
            ("Improve physical fitness", "Get in the best shape of my life", "Health", "1Y")
        ]
        
        for goal in goals:
            self.conn.execute(
                "INSERT INTO goals (title, description, category, timeline) VALUES (?, ?, ?, ?)",
                goal
            )
        
        # Sample tasks
        tasks = [
            ("Finalize business plan draft", "Complete the executive summary and financial projections", "high", "pending", 1),
            ("Schedule meeting with mentor", "Book a session to discuss business strategy", "medium", "pending", 1),
            ("Research competitors' pricing", "Analyze pricing strategies of top 5 competitors", "medium", "pending", 1),
            ("Complete Python basics course", "Finish the fundamentals course on Coursera", "high", "pending", 2),
            ("Set up home gym", "Purchase equipment and create workout space", "low", "pending", 3)
        ]
        
        for task in tasks:
            self.conn.execute(
                "INSERT INTO tasks (title, description, priority, status, goal_id) VALUES (?, ?, ?, ?, ?)",
                task
            )
        
        # Added sample notes
        notes = [
            ("Marketing Campaign Ideas", "Social media strategy focusing on Instagram and TikTok to reach our target demographic. Consider influencer partnerships and user-generated content campaigns.", "Ideas", "#FFF3E0"),
            ("Customer Research Findings", "Key insights from user interviews: 1) Price sensitivity is high among 25-34 age group, 2) Mobile app is preferred over web, 3) Customer support is crucial for retention.", "Work", "#E8F5E8"),
            ("Business Plan Draft", "Executive summary completed. Need to flesh out financial projections and market analysis sections. Consider adding competitive analysis and risk assessment.", "Work", "#E3F2FD"),
            ("Learning Notes - Python", "Key concepts: List comprehensions, lambda functions, decorators. Practice projects: web scraper, data analysis tool, automation scripts.", "Learning", "#F3E5F5"),
            ("Weekend Project Ideas", "1) Build a personal finance tracker, 2) Create a habit tracking app, 3) Develop a recipe recommendation system using ML", "Personal", "#FFF8E1")
        ]
        
        for note in notes:
            self.conn.execute(
                "INSERT INTO notes (title, content, category, color) VALUES (?, ?, ?, ?)",
                note
            )
        
        # Sample captures
        captures = [
            ('voice', 'Ideas for marketing campaign...', 'processed', '{"duration": "2m", "transcribed": true}'),
            ('image', 'Screenshot of competitor website', 'processing', '{"size": "1.2MB", "format": "PNG"}'),
            ('text', 'Quick note about meeting insights', 'processed', '{"source": "whatsapp"}')
        ]
        
        for capture in captures:
            self.conn.execute(
                "INSERT INTO captures (type, content, status, metadata) VALUES (?, ?, ?, ?)",
                capture
            )
        
        self.conn.commit()

    def get_notes(self):
        cursor = self.conn.execute(
            "SELECT id, title, content, category, color, created_at FROM notes ORDER BY created_at DESC"
        )
        return [
            {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'color': row[4],
                'created_at': row[5]
            }
            for row in cursor.fetchall()
        ]

    def add_note(self, title, content, category="Ideas", color="#FFFFFF"):
        self.conn.execute(
            "INSERT INTO notes (title, content, category, color) VALUES (?, ?, ?, ?)",
            (title, content, category, color)
        )
        self.conn.commit()

    def update_note(self, note_id, title, content, category, color):
        self.conn.execute(
            "UPDATE notes SET title=?, content=?, category=?, color=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (title, content, category, color, note_id)
        )
        self.conn.commit()

    def delete_note(self, note_id):
        self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.conn.commit()

    def get_tasks(self):
        cursor = self.conn.execute(
            "SELECT id, title, description, priority, status, goal_id, created_at FROM tasks ORDER BY created_at DESC"
        )
        return [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'goal_id': row[5],
                'created_at': row[6]
            }
            for row in cursor.fetchall()
        ]

    def get_goals(self):
        cursor = self.conn.execute(
            "SELECT id, title, description, category, timeline, status, created_at FROM goals ORDER BY created_at DESC"
        )
        return [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'timeline': row[4],
                'status': row[5],
                'created_at': row[6]
            }
            for row in cursor.fetchall()
        ]

class PersonalOSApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = SimpleDB()
        self.current_view = "dashboard"
        self.notes_view_mode = "grid"
        self.is_mobile = False
        self.is_tablet = False
        self.editing_note_id = None
        self.note_dialog = None
        self.category_dialog = None
        self.new_category_field = None
        self.editor_container = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.page.title = "Personal Operating System"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.on_resized = self.on_window_resize
        self.check_screen_size()
        
        # Main layout
        self.page.add(
            ft.Row([
                self.create_navigation(),
                ft.Container(
                    content=self.get_current_view(),
                    expand=True,
                    padding=20
                )
            ], expand=True)
        )
        
        self.page.update()
    
    def on_window_resize(self, e):
        self.check_screen_size()
        self.page.clean()
        self.setup_ui()
    
    def check_screen_size(self):
        width = self.page.window.width or 1200
        self.is_mobile = width < 768
        self.is_tablet = 768 <= width < 1024

    def get_current_view(self):
        if self.current_view == "dashboard":
            return self.create_dashboard()
        elif self.current_view == "notes":
            return self.create_notes_view()
        elif self.current_view == "knowledge":
            return self.create_knowledge_graph_view()
        elif self.current_view == "goals":
            return self.create_goals_view()
        elif self.current_view == "tasks":
            return self.create_tasks_view()
        elif self.current_view == "focus":
            return self.create_focus_view()
        elif self.current_view == "productivity":
            return self.create_productivity_view()
        elif self.current_view == "analytics":
            return self.create_analytics_view()
        else:
            return self.create_dashboard()

    def create_navigation(self):
        nav_items = [
            ("Dashboard", "dashboard", ft.Icons.DASHBOARD),
            ("Notes", "notes", ft.Icons.NOTE),
            ("Knowledge", "knowledge", ft.Icons.ACCOUNT_TREE),
            ("Goals", "goals", ft.Icons.TRACK_CHANGES),
            ("Tasks", "tasks", ft.Icons.CHECK_CIRCLE),
            ("Focus", "focus", ft.Icons.TIMER),
            ("Productivity", "productivity", ft.Icons.TRENDING_UP),
            ("Analytics", "analytics", ft.Icons.ANALYTICS),
        ]
        
        if self.is_mobile:
            return ft.Container(
                height=0,  # Hide sidebar on mobile
                width=0,
                content=ft.Column([])
            )
        
        return ft.Container(
            width=250,
            bgcolor=ft.Colors.GREY_50,
            padding=20,
            content=ft.Column([
                # Logo/Title
                ft.Container(
                    padding=ft.padding.only(bottom=30),
                    content=ft.Row([
                        ft.Icon(ft.Icons.PSYCHOLOGY, color=ft.Colors.PURPLE, size=32),
                        ft.Text("Personal OS", size=18, weight=ft.FontWeight.W_700)
                    ])
                ),
                
                # Navigation items
                ft.Column([
                    ft.Container(
                        padding=10,
                        margin=ft.margin.symmetric(vertical=2),
                        bgcolor=ft.Colors.PURPLE if item[1] == self.current_view else ft.Colors.TRANSPARENT,
                        border_radius=8,
                        content=ft.TextButton(
                            content=ft.Row([
                                ft.Icon(item[2], color=ft.Colors.WHITE if item[1] == self.current_view else ft.Colors.GREY_700),
                                ft.Text(item[0], color=ft.Colors.WHITE if item[1] == self.current_view else ft.Colors.GREY_700)
                            ]),
                            on_click=lambda e, view=item[1]: self.navigate_to(view)
                        )
                    ) for item in nav_items
                ])
            ])
        )
    
    def create_bottom_navigation(self):
        if not self.is_mobile:
            return ft.Container(height=0)
        
        nav_items = [
            ("Dashboard", "dashboard", ft.Icons.DASHBOARD),
            ("Notes", "notes", ft.Icons.NOTE),
            ("Tasks", "tasks", ft.Icons.CHECK_CIRCLE),
            ("Focus", "focus", ft.Icons.TIMER),
            ("More", "more", ft.Icons.MORE_HORIZ),
        ]
        
        return ft.Container(
            height=80,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_300)),
            content=ft.Row([
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        ft.IconButton(
                            icon=item[2],
                            icon_color=ft.Colors.PURPLE if item[1] == self.current_view else ft.Colors.GREY_500,
                            on_click=lambda e, view=item[1]: self.navigate_to(view)
                        ),
                        ft.Text(item[0], size=10, 
                               color=ft.Colors.PURPLE if item[1] == self.current_view else ft.Colors.GREY_500,
                               text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
                ) for item in nav_items
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        )

    def navigate_to(self, view):
        self.current_view = view
        self.page.clean()
        self.setup_ui()

    def create_dashboard(self):
        # Get current time for greeting
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        # Get stats
        tasks = self.db.get_tasks()
        goals = self.db.get_goals()
        notes = self.db.get_notes()
        
        today_tasks = [t for t in tasks if t['status'] == 'pending']
        active_goals = [g for g in goals if g['status'] == 'active']
        
        dashboard_content = ft.Column([
            # Header with greeting and AI insight
            ft.Container(
                padding=30,
                margin=ft.margin.only(bottom=20),
                bgcolor=ft.Colors.PURPLE,
                border_radius=10,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(f"{greeting}, Alex", size=28, color=ft.Colors.WHITE, weight=ft.FontWeight.W_700),
                            ft.Text(f"Monday, 10 June • You have {len(today_tasks)} tasks for today", 
                                   size=16, color=ft.Colors.WHITE70)
                        ], expand=True),
                    ]),
                    ft.Container(height=15),
                    ft.Row([
                        ft.Icon(ft.Icons.PSYCHOLOGY, color=ft.Colors.WHITE70, size=20),
                        ft.Text("AI Insight: You're most productive between 9-11 AM", 
                               color=ft.Colors.WHITE70, size=14),
                        ft.Container(expand=True),
                        ft.Row([
                            ft.Icon(ft.Icons.FLASH_ON, color=ft.Colors.WHITE70, size=20),
                            ft.Text("Focus Score: 85% (↑12% from last week)", 
                                   color=ft.Colors.WHITE70, size=14)
                        ])
                    ])
                ])
            ),
            
            # Stats cards
            ft.Row([
                self.create_stat_card("Tasks Today", str(len(today_tasks)), ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN),
                self.create_stat_card("Active Goals", str(len(active_goals)), ft.Icons.TRACK_CHANGES, ft.Colors.ORANGE),
                self.create_stat_card("Notes This Week", str(len(notes)), ft.Icons.NOTE, ft.Colors.BLUE),
                self.create_stat_card("Focus Score", "85%", ft.Icons.FLASH_ON, ft.Colors.PURPLE),
            ], wrap=True),
            
            ft.Container(height=20),
            
            # Today's Priority and Recent Captures
            ft.Row([
                # Today's Priority
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Today's Priority", size=18, weight=ft.FontWeight.W_700),
                            ft.TextButton("See All", style=ft.ButtonStyle(color=ft.Colors.PURPLE))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Column([
                            self.create_task_item(task) for task in today_tasks[:3]
                        ])
                    ])
                ),
                
                ft.Container(width=20),
                
                # Recent Captures
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        ft.Text("Recent Captures", size=18, weight=ft.FontWeight.W_700),
                        ft.Column([
                            self.create_capture_item("Voice Note", "Ideas for marketing campaign...", "2m ago", ft.Icons.MIC),
                            self.create_capture_item("Image", "Screenshot of competitor website", "15m ago", ft.Icons.IMAGE),
                        ])
                    ])
                )
            ], wrap=True if self.is_mobile else False)
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=dashboard_content, expand=True),
                self.create_bottom_navigation()
            ])
        
        return dashboard_content
    
    def create_stat_card(self, title, value, icon, color):
        return ft.Container(
            width=200,
            padding=20,
            margin=5,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
            content=ft.Row([
                ft.Icon(icon, color=color, size=24),
                ft.Column([
                    ft.Text(value, size=24, weight=ft.FontWeight.W_700),
                    ft.Text(title, size=12, color=ft.Colors.GREY_600)
                ], spacing=2)
            ])
        )
    
    def create_task_item(self, task):
        priority_colors = {
            'high': ft.Colors.RED,
            'medium': ft.Colors.ORANGE,
            'low': ft.Colors.GREEN
        }
        
        return ft.Container(
            padding=15,
            margin=ft.margin.symmetric(vertical=5),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_200),
            content=ft.Row([
                ft.Checkbox(value=False),
                ft.Column([
                    ft.Text(task['title'], weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=priority_colors.get(task['priority'], ft.Colors.GREY),
                            border_radius=4,
                            content=ft.Text(task['priority'].title(), size=10, color=ft.Colors.WHITE)
                        ),
                        ft.Text("2 hours", size=12, color=ft.Colors.GREY_600)
                    ])
                ], expand=True),
                ft.Text("3", size=12, color=ft.Colors.GREY_600)
            ])
        )
    
    def create_capture_item(self, type_name, content, time, icon):
        return ft.Container(
            padding=15,
            margin=ft.margin.symmetric(vertical=5),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_200),
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.PURPLE),
                ft.Column([
                    ft.Text(type_name, weight=ft.FontWeight.W_500),
                    ft.Text(content, size=12, color=ft.Colors.GREY_600)
                ], expand=True),
                ft.Text(time, size=10, color=ft.Colors.GREY_500)
            ])
        )
    
    def create_notes_view(self):
        notes = self.db.get_notes()
        
        notes_content = ft.Column([
            # Header
            ft.Row([
                ft.Text("Notes", size=24, weight=ft.FontWeight.W_700),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.GRID_VIEW,
                        selected=self.notes_view_mode == "grid",
                        on_click=lambda e: self.toggle_notes_view("grid")
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LIST,
                        selected=self.notes_view_mode == "list",
                        on_click=lambda e: self.toggle_notes_view("list")
                    ),
                    ft.ElevatedButton(
                        "New Note",
                        icon=ft.Icons.ADD,
                        bgcolor=ft.Colors.PURPLE,
                        color=ft.Colors.WHITE,
                        on_click=self.show_new_note_dialog
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=20),
            
            # Notes content
            self.create_notes_content(notes)
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=notes_content, expand=True),
                self.create_bottom_navigation()
            ])
        
        return notes_content
    
    def create_notes_content(self, notes):
        if self.notes_view_mode == "grid":
            # Grid view
            rows = []
            for i in range(0, len(notes), 2):
                row_notes = notes[i:i+2]
                row = ft.Row([
                    self.create_note_card(note) for note in row_notes
                ], wrap=True)
                rows.append(row)
            return ft.Column(rows)
        else:
            # List view
            return ft.Column([
                self.create_note_list_item(note) for note in notes
            ])
    
    def show_new_note_dialog(self, e):
        self.editing_note_id = None
        self.show_note_dialog()
    
    def show_edit_note_dialog(self, note_id):
        self.editing_note_id = note_id
        self.show_note_dialog()
    
    def show_note_dialog(self):
        # Get note data if editing
        note_data = None
        if self.editing_note_id:
            notes = self.db.get_notes()
            note_data = next((n for n in notes if n['id'] == self.editing_note_id), None)
        
        self.note_title = ft.TextField(
            hint_text="Note title...",
            value=note_data['title'] if note_data else "",
            border=ft.InputBorder.NONE,
            text_size=20,
            content_padding=ft.padding.all(0)
        )
        
        # Color picker for note background
        self.selected_note_color = note_data.get('color', '#FFFFFF') if note_data else '#FFFFFF'
        color_options = [
            '#FFFFFF', '#FFF3E0', '#E8F5E8', '#E3F2FD', '#F3E5F5', 
            '#FFF8E1', '#FCE4EC', '#E0F2F1', '#F1F8E9', '#FFEBEE'
        ]
        
        def update_color_picker():
            for i, container in enumerate(self.color_picker.controls):
                color = color_options[i]
                container.border = ft.border.all(2, ft.Colors.PURPLE if color == self.selected_note_color else ft.Colors.TRANSPARENT)
        
        def change_color(color):
            self.selected_note_color = color
            self.editor_container.bgcolor = color
            update_color_picker()
            self.page.update()
        
        self.color_picker = ft.Row([
            ft.Container(
                width=30,
                height=30,
                bgcolor=color,
                border_radius=15,
                border=ft.border.all(2, ft.Colors.PURPLE if color == self.selected_note_color else ft.Colors.TRANSPARENT),
                on_click=lambda e, c=color: change_color(c)
            ) for color in color_options
        ], wrap=True, spacing=10)
        
        # Category selector as icon with popup
        self.note_category = note_data['category'] if note_data else "Ideas"
        self.category_button = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCAL_OFFER, size=16, color=ft.Colors.GREY_600),
                ft.Text(self.note_category, size=12, color=ft.Colors.GREY_600)
            ]),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
            on_click=self.show_category_picker
        )
        
        # Content field without borders
        self.note_content = ft.TextField(
            hint_text="Start writing...",
            value=note_data['content'] if note_data else "",
            multiline=True,
            min_lines=15,
            max_lines=25,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.all(0),
            expand=True
        )
        
        # Functional attachment menu with handlers
        def handle_attachment(attachment_type):
            # Placeholder functionality for attachments
            if attachment_type == "pen":
                self.note_content.value += "\n[Drawing placeholder]"
            elif attachment_type == "media":
                self.note_content.value += "\n[Media attachment placeholder]"
            elif attachment_type == "table":
                self.note_content.value += "\n| Column 1 | Column 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
            elif attachment_type == "checklist":
                self.note_content.value += "\n☐ Task 1\n☐ Task 2\n☐ Task 3"
            self.page.update()
        
        attachment_menu = ft.PopupMenuButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.Colors.PURPLE,
            items=[
                ft.PopupMenuItem(
                    text="Pen/Drawing", 
                    icon=ft.Icons.DRAW,
                    on_click=lambda e: handle_attachment("pen")
                ),
                ft.PopupMenuItem(
                    text="Upload Media", 
                    icon=ft.Icons.PHOTO_LIBRARY,
                    on_click=lambda e: handle_attachment("media")
                ),
                ft.PopupMenuItem(
                    text="Add Table", 
                    icon=ft.Icons.TABLE_CHART,
                    on_click=lambda e: handle_attachment("table")
                ),
                ft.PopupMenuItem(
                    text="Add Checklist", 
                    icon=ft.Icons.CHECKLIST,
                    on_click=lambda e: handle_attachment("checklist")
                )
            ]
        )
        
        # Note editor container with selected color
        self.editor_container = ft.Container(
            bgcolor=self.selected_note_color,
            border_radius=12,
            padding=20,
            content=ft.Column([
                self.note_title,
                ft.Container(height=10),
                ft.Row([
                    self.category_button,
                    ft.Container(expand=True),
                    attachment_menu
                ]),
                ft.Container(height=15),
                self.note_content
            ], expand=True),
            expand=True
        )
        
        def save_note(e):
            if self.note_title.value and self.note_content.value:
                if self.editing_note_id:
                    self.db.update_note(
                        self.editing_note_id,
                        self.note_title.value,
                        self.note_content.value,
                        self.note_category,
                        self.selected_note_color
                    )
                else:
                    self.db.add_note(
                        self.note_title.value,
                        self.note_content.value,
                        self.note_category,
                        self.selected_note_color
                    )
                    
                self.note_dialog.open = False
                self.page.update()
                self.navigate_to("notes")
        
        def cancel_note(e):
            self.note_dialog.open = False
            self.page.update()
        
        self.note_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Text("Edit Note" if self.editing_note_id else "New Note", size=18),
                ft.Container(expand=True),
                ft.Text("Colors", size=12, color=ft.Colors.GREY_600)
            ]),
            content=ft.Column([
                self.color_picker,
                ft.Container(height=10),
                self.editor_container
            ], width=500, height=600),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_note),
                ft.ElevatedButton(
                    "Save Note",
                    bgcolor=ft.Colors.PURPLE,
                    color=ft.Colors.WHITE,
                    on_click=save_note
                )
            ]
        )
        
        self.page.overlay.append(self.note_dialog)
        self.note_dialog.open = True
        self.page.update()
    
    def change_note_color(self, color):
        self.selected_note_color = color
        if hasattr(self, 'note_dialog') and hasattr(self, 'editor_container'):
            self.editor_container.bgcolor = color
            self.page.update()

    def show_category_picker(self, e):
        categories = ["Ideas", "Work", "Personal", "Learning", "Projects", "Health", "Finance"]
        
        def select_category(category):
            self.note_category = category
            self.category_button.content.controls[1].value = category
            self.category_dialog.open = False
            self.page.update()
        
        def add_new_category(e):
            if self.new_category_field.value.strip():
                new_cat = self.new_category_field.value.strip()
                self.note_category = new_cat
                self.category_button.content.controls[1].value = new_cat
                self.category_dialog.open = False
                self.page.update()
        
        self.new_category_field = ft.TextField(
            hint_text="Enter new category",
            width=200
        )
        
        category_items = []
        for cat in categories:
            category_items.append(
                ft.ListTile(
                    title=ft.Text(cat),
                    on_click=lambda e, c=cat: select_category(c)
                )
            )
        
        category_items.append(ft.Divider())
        category_items.append(
            ft.Row([
                self.new_category_field,
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    on_click=add_new_category
                )
            ])
        )
        
        self.category_dialog = ft.AlertDialog(
            title=ft.Text("Select Category"),
            content=ft.Column(category_items, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_category_dialog())
            ]
        )
        
        self.page.overlay.append(self.category_dialog)
        self.category_dialog.open = True
        self.page.update()
    
    def close_category_dialog(self):
        self.category_dialog.open = False
        self.page.update()

    def create_note_card(self, note):
        note_color = note.get('color', '#FFFFFF')
        return ft.Container(
            width=300 if not self.is_mobile else None,
            height=200,
            padding=20,
            margin=10,
            bgcolor=note_color,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
            content=ft.Column([
                ft.Row([
                    ft.Text(note['title'], size=16, weight=ft.FontWeight.W_700),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text="Edit",
                                icon=ft.Icons.EDIT,
                                on_click=lambda e: self.show_edit_note_dialog(note['id'])
                            ),
                            ft.PopupMenuItem(
                                text="Delete",
                                icon=ft.Icons.DELETE,
                                on_click=lambda e: self.delete_note(note['id'])
                            )
                        ]
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Text(note['content'][:100] + "..." if len(note['content']) > 100 else note['content'],
                       size=12, color=ft.Colors.GREY_600),
                
                ft.Container(expand=True),
                
                ft.Row([
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.PURPLE_100,
                        border_radius=12,
                        content=ft.Text(note['category'], size=10, color=ft.Colors.PURPLE)
                    ),
                    ft.Text(note['created_at'][:10], size=10, color=ft.Colors.GREY_500)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        )

    def create_note_list_item(self, note):
        note_color = note.get('color', '#FFFFFF')
        return ft.Container(
            padding=20,
            margin=ft.margin.symmetric(vertical=5),
            bgcolor=note_color,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_200),
            content=ft.Row([
                ft.Column([
                    ft.Text(note['title'], size=16, weight=ft.FontWeight.W_700),
                    ft.Text(note['content'][:150] + "..." if len(note['content']) > 150 else note['content'],
                           size=12, color=ft.Colors.GREY_600),
                    ft.Row([
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=ft.Colors.PURPLE_100,
                            border_radius=12,
                            content=ft.Text(note['category'], size=10, color=ft.Colors.PURPLE)
                        ),
                        ft.Text(note['created_at'][:10], size=10, color=ft.Colors.GREY_500)
                    ])
                ], expand=True),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Edit",
                            icon=ft.Icons.EDIT,
                            on_click=lambda e: self.show_edit_note_dialog(note['id'])
                        ),
                        ft.PopupMenuItem(
                            text="Delete",
                            icon=ft.Icons.DELETE,
                            on_click=lambda e: self.delete_note(note['id'])
                        )
                    ]
                )
            ])
        )

    def delete_note(self, note_id):
        self.db.delete_note(note_id)
        self.navigate_to("notes")  # Refresh notes view

    def toggle_notes_view(self, mode):
        self.notes_view_mode = mode
        self.navigate_to("notes")  # Refresh notes view

    def create_knowledge_graph_view(self):
        content = ft.Column([
            ft.Text("Knowledge Graph", size=24, weight=ft.FontWeight.W_700),
            ft.Container(height=20),
            
            # Knowledge graph visualization placeholder
            ft.Container(
                height=400,
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                content=ft.Column([
                    ft.Icon(ft.Icons.ACCOUNT_TREE, size=64, color=ft.Colors.GREY_400),
                    ft.Text("Interactive Knowledge Graph", size=18, color=ft.Colors.GREY_600),
                    ft.Text("Visualize connections between your notes, tasks, and goals", 
                           size=12, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            
            # AI Insights
            ft.Container(
                padding=20,
                margin=ft.margin.only(top=20),
                bgcolor=ft.Colors.PURPLE_50,
                border_radius=12,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PSYCHOLOGY, color=ft.Colors.PURPLE),
                        ft.Text("AI Insights", size=16, weight=ft.FontWeight.W_700)
                    ]),
                    ft.Text("Your 'Marketing Campaign' note connects to 7 other items and might be a key project focus.",
                           size=12, color=ft.Colors.GREY_600)
                ])
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

    def create_analytics_view(self):
        content = ft.Column([
            ft.Text("Analytics", size=24, weight=ft.FontWeight.W_700),
            ft.Container(height=20),
            
            # Analytics cards
            ft.Row([
                self.create_stat_card("Productivity Score", "85%", ft.Icons.TRENDING_UP, ft.Colors.GREEN),
                self.create_stat_card("Tasks Completed", "47", ft.Icons.CHECK_CIRCLE, ft.Colors.BLUE),
                self.create_stat_card("Focus Time", "6.2h", ft.Icons.TIMER, ft.Colors.ORANGE),
                self.create_stat_card("Notes Created", "23", ft.Icons.NOTE, ft.Colors.PURPLE),
            ], wrap=True),
            
            ft.Container(height=30),
            
            # Charts placeholder
            ft.Container(
                height=300,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
                content=ft.Column([
                    ft.Text("Weekly Productivity Trends", size=16, weight=ft.FontWeight.W_700),
                    ft.Container(
                        expand=True,
                        content=ft.Column([
                            ft.Icon(ft.Icons.ANALYTICS, size=64, color=ft.Colors.GREY_400),
                            ft.Text("Analytics charts coming soon", color=ft.Colors.GREY_500)
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

    def create_productivity_view(self):
        content = ft.Column([
            ft.Text("Productivity Hub", size=24, weight=ft.FontWeight.W_700),
            ft.Container(height=20),
            
            # Quick actions
            ft.Row([
                ft.ElevatedButton(
                    "Start Focus Session",
                    icon=ft.Icons.PLAY_ARROW,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.navigate_to("focus")
                ),
                ft.ElevatedButton(
                    "Quick Capture",
                    icon=ft.Icons.ADD,
                    bgcolor=ft.Colors.PURPLE,
                    color=ft.Colors.WHITE,
                    on_click=self.show_new_note_dialog
                ),
                ft.ElevatedButton(
                    "Review Goals",
                    icon=ft.Icons.TRACK_CHANGES,
                    bgcolor=ft.Colors.ORANGE,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.navigate_to("goals")
                )
            ], wrap=True),
            
            ft.Container(height=30),
            
            # Productivity insights
            ft.Container(
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
                content=ft.Column([
                    ft.Text("Today's Productivity Insights", size=18, weight=ft.FontWeight.W_700),
                    ft.Container(height=15),
                    ft.Row([
                        ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN),
                        ft.Text("You're 12% more productive than last week", color=ft.Colors.GREY_700)
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.BLUE),
                        ft.Text("Best focus time: 9:00 AM - 11:00 AM", color=ft.Colors.GREY_700)
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.LIGHTBULB, color=ft.Colors.ORANGE),
                        ft.Text("Consider breaking large tasks into smaller chunks", color=ft.Colors.GREY_700)
                    ])
                ])
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

    def create_goals_view(self):
        content = ft.Column([
            ft.Text("Goals & Projects", size=24, weight=ft.FontWeight.W_700),
            ft.Text("Goals management coming soon...", color=ft.Colors.GREY_500)
        ])
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

    def create_tasks_view(self):
        content = ft.Column([
            ft.Text("Tasks", size=24, weight=ft.FontWeight.W_700),
            ft.Text("Task management coming soon...", color=ft.Colors.GREY_500)
        ])
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

    def create_focus_view(self):
        content = ft.Column([
            ft.Text("Focus Timer", size=24, weight=ft.FontWeight.W_700),
            ft.Text("Pomodoro timer coming soon...", color=ft.Colors.GREY_500)
        ])
        
        if self.is_mobile:
            return ft.Column([
                ft.Container(content=content, expand=True),
                self.create_bottom_navigation()
            ])
        return content

async def main(page: ft.Page):
    app = PersonalOSApp(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_WEB)
