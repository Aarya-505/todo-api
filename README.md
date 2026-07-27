# FlyRank To-Do CRUD API

A simple, persistent CRUD API built with Python, FastAPI, and SQLite for the FlyRank Backend Track.

## Why SQLite?
- **Single file & zero setup:** Requires no separate database server installation[cite: 1].
- **Persistence:** Data outlives program restarts by saving directly to disk in `tasks.db`[cite: 1].

## Database Location
The database file is created automatically as `tasks.db` on the first application run. It is git-ignored so that every clean clone starts fresh[cite: 1].

## How to Run
1. Install dependencies: `pip install fastapi uvicorn`[cite: 1]
2. Start the server: `uvicorn main:app --reload`[cite: 1]
3. View the docs at `http://localhost:8000/docs`

## Endpoints
| HTTP Method | Endpoint | Purpose |
| ----------- | ----------- | ----------- |
| GET | `/` | API Metadata |
| GET | `/health` | Health Check |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a single task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## Example SQL Query (Stage 4)[cite: 1]
```sql
SELECT * FROM tasks WHERE done = 1;