import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend import database as db
from backend import schemas

app = FastAPI(
    title="TaskCraft API",
    description="Full-stack To-Do Application REST API Backend with SQLite",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initializes the database schema and seeds default data if empty."""
    db.init_db()
    db.seed_initial_data_if_empty()


# --- REST API Endpoints ---

@app.get("/api/todos", response_model=List[schemas.TodoResponse])
def read_todos(
    search: Optional[str] = Query(None, description="Search term for title or description"),
    status: Optional[str] = Query(None, description="Filter by status: pending, completed, or all"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, or all"),
    sort_by: Optional[str] = Query("created_at_desc", description="Sort order: created_at_desc, created_at_asc, due_date_asc, priority_desc")
):
    """Retrieve list of todos with search, filter, and sorting options."""
    return db.get_todos(search=search, status=status, category=category, priority=priority, sort_by=sort_by)


@app.get("/api/todos/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats():
    """Get real-time dashboard analytics and metrics."""
    return db.get_stats()


@app.get("/api/todos/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(todo_id: int):
    """Fetch details of a single todo item by ID."""
    todo = db.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/api/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: schemas.TodoCreate):
    """Create a new todo item with subtasks."""
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return db.create_todo(
        title=payload.title.strip(),
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        due_date=payload.due_date,
        subtasks=payload.subtasks
    )


@app.put("/api/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, payload: schemas.TodoUpdate):
    """Update an existing todo item."""
    todo = db.get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    updated = db.update_todo(
        todo_id=todo_id,
        title=payload.title.strip(),
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        due_date=payload.due_date,
        status=payload.status
    )
    return updated


@app.patch("/api/todos/{todo_id}/toggle", response_model=schemas.TodoResponse)
def toggle_todo(todo_id: int):
    """Quick toggle completion status of a todo."""
    updated = db.toggle_todo_status(todo_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    """Delete a todo item."""
    success = db.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None


@app.post("/api/todos/{todo_id}/subtasks", response_model=schemas.TodoResponse)
def add_subtask(todo_id: int, payload: schemas.SubtaskCreate):
    """Add a subtask to an existing todo."""
    updated = db.add_subtask(todo_id, payload.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.patch("/api/subtasks/{subtask_id}/toggle", response_model=schemas.TodoResponse)
def toggle_subtask(subtask_id: int):
    """Toggle completion status of a subtask."""
    updated = db.toggle_subtask(subtask_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return updated


@app.delete("/api/subtasks/{subtask_id}", response_model=schemas.TodoResponse)
def delete_subtask(subtask_id: int):
    """Delete a subtask."""
    updated = db.delete_subtask(subtask_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return updated


@app.post("/api/seed")
def seed_data():
    """Manually re-seed initial sample data."""
    db.seed_initial_data_if_empty()
    return {"message": "Database seeded successfully"}


# --- Serve Static Frontend Files ---
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
