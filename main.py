import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Header, Depends
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

# Reusable Auth Dependency (The Guard)
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail={"error": "Access token required"}
        )
    
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = authorization
    
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=401, 
            detail={"error": "Invalid or expired token"}
        )

# Protected Profile Route (Using the reusable dependency)
@app.get("/protected/profile", status_code=200)
def protected_profile(current_user = Depends(get_current_user)):
    return {"user": current_user}

# Stage 4: Protected Logout Route
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def log_out(current_user = Depends(get_current_user)):
    try:
        # End the session with Supabase
        supabase.auth.sign_out()
        return
    except Exception:
        raise HTTPException(status_code=400, detail="Error logging out")