from fastapi import FastAPI, HTTPException

app = FastAPI()

# Our in-memory "database"
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Walk the dog", "done": False}
]

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
    # If the loop finishes without finding the task, return a 404 error
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")