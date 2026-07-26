from fastapi import FastAPI

app = FastAPI()

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