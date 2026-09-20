import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "todos.db")


def get_connection() -> sqlite3.Connection:
    """Creates and returns a database connection with row factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes the SQLite database tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Create todos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'Personal',
                priority TEXT NOT NULL DEFAULT 'medium',
                status TEXT NOT NULL DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create subtasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                todo_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                is_completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE CASCADE
            );
        """)
        
        # Performance indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_category ON todos(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subtasks_todo_id ON subtasks(todo_id);")
        
        conn.commit()


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a sqlite3.Row object to a Python dictionary."""
    return {key: row[key] for key in row.keys()}


def seed_initial_data_if_empty():
    """Seeds default realistic initial tasks if database is brand new."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM todos;")
        count = cursor.fetchone()["count"]
        
        if count > 0:
            return

        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (now + timedelta(days=5)).strftime("%Y-%m-%d")
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        sample_todos = [
            {
                "title": "Build Full-Stack TaskCraft Application",
                "description": "Design and code FastAPI backend, SQLite database, and high-performance Glassmorphism UI.",
                "category": "Work",
                "priority": "high",
                "status": "pending",
                "due_date": tomorrow,
                "subtasks": ["Implement SQLite schemas", "Build REST API endpoints", "Create Responsive UI"]
            },
            {
                "title": "Weekly Grocery Shopping",
                "description": "Buy fresh fruits, vegetables, almond milk, and pantry staples.",
                "category": "Shopping",
                "priority": "medium",
                "status": "pending",
                "due_date": tomorrow,
                "subtasks": ["Organic Apples & Bananas", "Spinach & Kale", "Almond Milk"]
            },
            {
                "title": "Morning 5K Jog & Yoga Stretch",
                "description": "Maintain fitness routine and complete a 20-minute post-run yoga session.",
                "category": "Health",
                "priority": "medium",
                "status": "completed",
                "due_date": yesterday,
                "subtasks": ["Hydrate 500ml water", "5km jog in park", "Stretching routine"]
            },
            {
                "title": "Monthly Budget & Expense Review",
                "description": "Review subscriptions, savings goals, and categorize bank statements.",
                "category": "Finance",
                "priority": "low",
                "status": "pending",
                "due_date": next_week,
                "subtasks": ["Check credit card statement", "Transfer to savings account"]
            }
        ]

        for item in sample_todos:
            cursor.execute("""
                INSERT INTO todos (title, description, category, priority, status, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """, (item["title"], item["description"], item["category"], item["priority"], item["status"], item["due_date"]))
            
            todo_id = cursor.lastrowid
            
            for sub in item["subtasks"]:
                is_comp = 1 if item["status"] == "completed" else 0
                cursor.execute("""
                    INSERT INTO subtasks (todo_id, title, is_completed)
                    VALUES (?, ?, ?);
                """, (todo_id, sub, is_comp))

        conn.commit()


def get_todos(
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: Optional[str] = "created_at_desc"
) -> List[Dict[str, Any]]:
    """Retrieves todos with flexible search, filter, and sorting options."""
    query = "SELECT * FROM todos WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])

    if status and status.lower() != "all":
        query += " AND status = ?"
        params.append(status.lower())

    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category)

    if priority and priority.lower() != "all":
        query += " AND priority = ?"
        params.append(priority.lower())

    # Order by mapping
    if sort_by == "due_date_asc":
        query += " ORDER BY CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END, due_date ASC"
    elif sort_by == "priority_desc":
        query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END"
    elif sort_by == "created_at_asc":
        query += " ORDER BY created_at ASC"
    else:
        # Default: created_at desc
        query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        todos = []
        for row in rows:
            todo = dict_from_row(row)
            # Fetch subtasks for each todo
            cursor.execute("SELECT * FROM subtasks WHERE todo_id = ? ORDER BY id ASC", (todo["id"],))
            todo["subtasks"] = [dict_from_row(sub) for sub in cursor.fetchall()]
            todos.append(todo)

        return todos


def get_todo_by_id(todo_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single todo item by ID with its subtasks."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?;", (todo_id,))
        row = cursor.fetchone()
        if not row:
            return None

        todo = dict_from_row(row)
        cursor.execute("SELECT * FROM subtasks WHERE todo_id = ? ORDER BY id ASC", (todo_id,))
        todo["subtasks"] = [dict_from_row(sub) for sub in cursor.fetchall()]
        return todo


def create_todo(
    title: str,
    description: Optional[str] = "",
    category: str = "Personal",
    priority: str = "medium",
    due_date: Optional[str] = None,
    subtasks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Creates a new todo item and its subtasks."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO todos (title, description, category, priority, status, due_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pending', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """, (title, description or "", category, priority, due_date))
        
        todo_id = cursor.lastrowid

        if subtasks:
            for sub_title in subtasks:
                if sub_title and sub_title.strip():
                    cursor.execute("""
                        INSERT INTO subtasks (todo_id, title, is_completed)
                        VALUES (?, ?, 0);
                    """, (todo_id, sub_title.strip()))

        conn.commit()
        return get_todo_by_id(todo_id)


def update_todo(
    todo_id: int,
    title: str,
    description: Optional[str] = "",
    category: str = "Personal",
    priority: str = "medium",
    due_date: Optional[str] = None,
    status: str = "pending"
) -> Optional[Dict[str, Any]]:
    """Updates an existing todo item."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE todos
            SET title = ?, description = ?, category = ?, priority = ?, due_date = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (title, description or "", category, priority, due_date, status, todo_id))
        
        conn.commit()
        return get_todo_by_id(todo_id)


def toggle_todo_status(todo_id: int) -> Optional[Dict[str, Any]]:
    """Toggles status between pending and completed."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM todos WHERE id = ?;", (todo_id,))
        row = cursor.fetchone()
        if not row:
            return None

        new_status = "completed" if row["status"] == "pending" else "pending"
        cursor.execute("""
            UPDATE todos
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (new_status, todo_id))

        # Also toggle subtasks to match if completing todo
        if new_status == "completed":
            cursor.execute("UPDATE subtasks SET is_completed = 1 WHERE todo_id = ?;", (todo_id,))

        conn.commit()
        return get_todo_by_id(todo_id)


def delete_todo(todo_id: int) -> bool:
    """Deletes a todo item by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?;", (todo_id,))
        conn.commit()
        return cursor.rowcount > 0


def add_subtask(todo_id: int, title: str) -> Optional[Dict[str, Any]]:
    """Adds a subtask to a todo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM todos WHERE id = ?;", (todo_id,))
        if not cursor.fetchone():
            return None

        cursor.execute("""
            INSERT INTO subtasks (todo_id, title, is_completed)
            VALUES (?, ?, 0);
        """, (todo_id, title.strip()))
        
        conn.commit()
        return get_todo_by_id(todo_id)


def toggle_subtask(subtask_id: int) -> Optional[Dict[str, Any]]:
    """Toggles completion state of a subtask."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT todo_id, is_completed FROM subtasks WHERE id = ?;", (subtask_id,))
        row = cursor.fetchone()
        if not row:
            return None

        new_val = 0 if row["is_completed"] == 1 else 1
        cursor.execute("UPDATE subtasks SET is_completed = ? WHERE id = ?;", (new_val, subtask_id))
        
        todo_id = row["todo_id"]
        conn.commit()
        return get_todo_by_id(todo_id)


def delete_subtask(subtask_id: int) -> Optional[Dict[str, Any]]:
    """Deletes a subtask."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT todo_id FROM subtasks WHERE id = ?;", (subtask_id,))
        row = cursor.fetchone()
        if not row:
            return None

        todo_id = row["todo_id"]
        cursor.execute("DELETE FROM subtasks WHERE id = ?;", (subtask_id,))
        conn.commit()
        return get_todo_by_id(todo_id)


def get_stats() -> Dict[str, Any]:
    """Calculates dashboard analytics and metrics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM todos;")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as completed FROM todos WHERE status = 'completed';")
        completed = cursor.fetchone()["completed"]

        cursor.execute("SELECT COUNT(*) as pending FROM todos WHERE status = 'pending';")
        pending = cursor.fetchone()["pending"]

        cursor.execute("SELECT COUNT(*) as high_priority FROM todos WHERE priority = 'high' AND status = 'pending';")
        high_priority = cursor.fetchone()["high_priority"]

        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM todos 
            GROUP BY category 
            ORDER BY count DESC;
        """)
        category_counts = {row["category"]: row["count"] for row in cursor.fetchall()}

        percentage = round((completed / total * 100)) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high_priority,
            "completion_rate": percentage,
            "categories": category_counts
        }
