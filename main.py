import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class AuthCredentials(BaseModel):
    email: str
    password: str

@app.get("/health")
def health_check():
    return {"status": "Server running and connected to Supabase"}

# Stage 1: Sign Up Route
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def sign_up(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return {"message": "User registered successfully", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Stage 1: Log In Route
@app.post("/auth/login", status_code=status.HTTP_200_OK)
def log_in(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

# Stage 2: Public Route
@app.get("/public/info", status_code=200)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# Stage 2: Unverified Protected Route
@app.get("/protected/profile", status_code=200)
def protected_profile(authorization: str = Header(None)):
    # Check if the header is missing, malformed, or doesn't have a token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail={"error": "Access token required"}
        )
    
    # Placeholder response for Stage 2 (real verification comes in Stage 3)
    return {"message": "Token received, verification pending in Stage 3"}