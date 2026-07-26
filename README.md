# FlyRank To-Do CRUD API

A simple, in-memory CRUD API built with Python and FastAPI for the FlyRank Backend Track.

## How to Run
1. Install dependencies: `pip install fastapi uvicorn`
2. Start the server: `uvicorn main:app --reload`
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

## Example cURL output
```bash
curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"

HTTP/1.1 201 Created
date: Sun, 26 Jul 2026 10:29:13 GMT
server: uvicorn
content-length: 44
content-type: application/json

{"id":4,"title":"Buy milk","done":false}