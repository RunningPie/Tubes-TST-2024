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


# Initialize Supabase client
# _supabase_client: Optional[Client] = None
client = create_client(SUPABASE_URL, SUPABASE_KEY)

base_url = os.getenv("BASE_URL")

@supabase_router.post("/user-signup", summary="This is used for user signup with classic email and password")
async def signup(
    email: str = Header(...),
    password: str = Header(...)
):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and Password headers are required")
    
    try:
        # client = get_supabase_client()
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
        # client = get_supabase_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        token = response.session.access_token
        
        fastapi_response = RedirectResponse(url=base_url + "/protected-home", status_code=302)
        fastapi_response.set_cookie(key="access_token", value=token, httponly=True)
        return fastapi_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/github-signin", summary="This is used for user signup with the help of GitHub OAuth Application")
async def github_signin(request: Request):
    try:
        response = client.auth.sign_in_with_oauth(
            {"provider": "github",
             "options": {
                 "redirect_to": f"{request.url_for("callback")}"
             }}
            )
        return RedirectResponse(url=response.url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/google-signin", summary="This is used for user signup with the help of google OAuth Application")
async def google_signin(request: Request):
    try:
        # client = get_supabase_client()
        response = client.auth.sign_in_with_oauth(
            {"provider": "google",
             "options": {
                 "redirect_to": f"{request.url_for("callback")}"
             }}
            )
        return RedirectResponse(url=response.url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@supabase_router.get("/user-signout", summary="This is used for user signout")
async def user_signout(request: Request):
    try:
        # client = get_supabase_client()
        response = client.auth.sign_out()
        redirect_res = RedirectResponse(url=request.base_url, status_code=302)
        
        cookies_to_clear = ['session_id', 'auth_token', 'access_token']
        for cookie_name in cookies_to_clear:
            redirect_res.delete_cookie(cookie_name)
            
        return redirect_res
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@supabase_router.route("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    next = request.query_params.get("next", "/protected-home")
    if code:
        try:
            res = client.auth.exchange_code_for_session({"auth_code": code})
            
            # Fixed session token extraction
            access_token = None
            if hasattr(res, 'session'):
                access_token = res.session.access_token
            elif isinstance(res, dict):
                access_token = res.get('access_token')
            
            if not access_token:
                raise ValueError("No access token found in response")
            
            fastapi_response = RedirectResponse(url=base_url + "/protected-home", status_code=302)
            fastapi_response.set_cookie(key="access_token", value=access_token, httponly=True)
            return fastapi_response
        
        except Exception as e:
            # Pass the error message as a query parameter
            error_message = f"Failed to exchange code for session: {str(e)}"
            return RedirectResponse(url=f"{next}?message={error_message}", status_code=302)   
    return RedirectResponse(next)

# def supabase_callback(code, next):
#     # client = get_supabase_client()
#     try:
#         res = client.auth.exchange_code_for_session(auth_code=code)
#         return RedirectResponse(next)
#     except:
#         return JSONResponse(status_code=500, content={"message": "Failed to exchange code for session"})