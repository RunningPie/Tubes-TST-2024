from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from supabase import Client, create_client
from typing import Optional
import os
from app.services.auth import JWTBearer

supabase_router = APIRouter()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# print("Supabase URL:", SUPABASE_URL)

# Initialize Supabase client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _supabase_client
    print(_supabase_client)
    if _supabase_client is None:
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Supabase: {str(e)}")
    return _supabase_client

@supabase_router.post("/user-signup", summary="This is used for user signup with classic email and password")
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

@supabase_router.post("/user-signin", summary="This is used for user signin with classic email and password")
async def signin(
    email: str = Header(...),
    password: str = Header(...)
):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and Password headers are required")
    
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        token = response.session.access_token
        
        fastapi_response = JSONResponse(content={"message": "User signed in successfully"})
        fastapi_response.set_cookie(key="access_token", value=token, httponly=True)
        return fastapi_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/github-signin", summary="This is used for user signup with the help of GitHub OAuth Application")
async def github_signin(request: Request):
    print("masuk github_signin")
    try:
        client = get_supabase_client()
        print(request.url_for("callback"))
        response = client.auth.sign_in_with_oauth(
            {"provider": "github",
             "options": {
                 "redirect_to": f"{request.url_for("callback")}"
             }}
            )
        return RedirectResponse(url=response.url, status_code=301)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/google-signin", summary="This is used for user signup with the help of google OAuth Application")
async def google_signin():
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_oauth(
            {"provider": "google"}
            )
        return RedirectResponse(url=response.url, status_code=301)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/user-signout", summary="This is used for user signout")
async def user_signout():
    try:
        client = get_supabase_client()
        response = client.auth.sign_out()
        return {"message": "User signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@supabase_router.route("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    next = request.query_params.get("next", "/")
    client = get_supabase_client()
    if code:
        try:
            res = client.auth.exchange_code_for_session({"auth_code": code})
        except Exception as e:
            # Pass the error message as a query parameter
            error_message = f"Failed to exchange code for session: {str(e)}"
            return RedirectResponse(url=f"{next}?message={error_message}", status_code=302)   
    return RedirectResponse(next)

def supabase_callback(code, next):
    client = get_supabase_client()
    try:
        res = client.auth.exchange_code_for_session(auth_code=code)
        return RedirectResponse(next)
    except:
        return JSONResponse(status_code=500, content={"message": "Failed to exchange code for session"})