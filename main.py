from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Our in-memory "database"
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Walk the dog", "done": False}
]

# Pydantic model for input validation
class TaskCreate(BaseModel):
    title: str

# Stage 1: Root endpoint returning API description
@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# Stage 1: Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Stage 2: List all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# Stage 2: Get a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Stage 3: Create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    # Validate that the title isn't just empty spaces
    if not task_in.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    # Find the highest ID currently in the list and add 1
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {
        "id": new_id,
        "title": task_in.title,
        "done": False
    }
    tasks.append(new_task)
    return new_task