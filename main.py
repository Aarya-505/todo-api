from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()

# Helper function to connect to our SQLite database
def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    # This row_factory allows us to access columns by name (e.g., task["title"])
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and seed initial data if empty
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the tasks table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    # Check if the table is empty before seeding
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Learn FastAPI", 1),
            ("Walk the dog", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks)
        conn.commit()
        
    conn.close()

# Run database initialization on startup
init_db()

# Pydantic models for validation
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# Stage 1: Root and health endpoints
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Stage 1: Read all tasks from the database
@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    tasks_list = []
    for row in rows:
        tasks_list.append({
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        })
    return tasks_list

# Stage 1: Read a single task by ID using a parameterized query
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

# Stage 2: Create a new task in the database
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    if not task_in.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task_in.title.strip(), 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

# Stage 3: Update an existing task using SQL UPDATE
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_in: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if task exists first
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    # Determine updated values (retain existing if not provided)
    new_title = task_in.title.strip() if task_in.title is not None else row["title"]
    if task_in.title is not None and not new_title:
        conn.close()
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    new_done = int(task_in.done) if task_in.done is not None else row["done"]
    
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    
    # Fetch updated row to return
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    updated_row = cursor.fetchone()
    conn.close()
    
    return {
        "id": updated_row["id"],
        "title": updated_row["title"],
        "done": bool(updated_row["done"])
    }

# Stage 3: Delete a task using SQL DELETE
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return None