from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import RedirectResponse
from supabase import Client, create_client
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

supabase_router = APIRouter()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Supabase: {str(e)}")
    return _supabase_client

@supabase_router.get("/user-signup", summary="This is used for user signup with classic email and password")
async def signup(
    email: str = Header(...),
    password: str = Header(...)
):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and Password headers are required")
    
    try:
        client = get_supabase_client()
        response = client.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/user-login", summary="This is used for user login with classic email and password")
async def login(
    email: str = Header(...),
    password: str = Header(...)
):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and Password headers are required")
    
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/github-login", summary="This is used for user signup with the help of GitHub OAuth Application")
async def github_login():
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_oauth(
            {"provider": "github"}
            )
        return RedirectResponse(url=response.url, status_code=301)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/google-login", summary="This is used for user signup with the help of google OAuth Application")
async def google_login():
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_oauth(
            {"provider": "google"}
            )
        return RedirectResponse(url=response.url, status_code=301)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
