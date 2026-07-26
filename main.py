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