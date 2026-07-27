# FlyRank To-Do CRUD API

A robust, multi-stage persistent CRUD API built with Python, FastAPI, and relational databases for the FlyRank Backend Track.

---

## Project Evolution & Stages

This repository demonstrates incremental backend development from local file-based storage to containerized production databases:

* **Stage 1–3:** Built core CRUD endpoints (`GET`, `POST`, `PUT`, `DELETE`), request validation via Pydantic, and parameterized SQL handling.
* **Stage 4 (SQLite Exploration):** Explored local file-based persistence using SQLite (`tasks.db`) for zero-setup execution.
* **Stage 5 (Production Migration):** Upgraded the architecture to a containerized **Docker & PostgreSQL** stack to meet advanced environment requirements.

---

## Tech Stack
* **Framework:** FastAPI (Python)
* **Server:** Uvicorn
* **Database (Current):** PostgreSQL 15 (via Docker)
* **Database (Early Stages):** SQLite (`tasks.db`)
* **Driver:** `psycopg2-binary`

---

## Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/Aarya-505/todo-api.git](https://github.com/Aarya-505/todo-api.git)
cd todo-api

```
### Set Up Virtual Environment
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

```
### Install Dependencies
```
pip install fastapi uvicorn psycopg2-binary

```

### Start the PostgreSQL Docker Container

To run the application with the current PostgreSQL backend, spin up the container mapping port 5433 (or 5432):

```
docker run --name todo-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=todo_db -p 5433:5432 -d postgres:15

```
### Run the Application

```
uvicorn main:app --reload

```

Access the interactive API documentation at: http://127.0.0.1:8000/docs

### API Endpoints

| HTTP Method | Endpoint | Purpose |
| ----------- | ----------- | ----------- |
| GET | `/` | API Metadata |
| GET | `/health` | Health Check |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a single task by ID |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{id}` | Update an existing task |
| DELETE | `/tasks/{id}` | Delete a task |