from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from supabase import Client, create_client
from typing import Optional
from datetime import datetime
import uuid
import os

supabase_router = APIRouter()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

base_url = os.getenv("BASE_URL")
frontend_url = os.getenv("FRONTEND_URL")

def validate_api_key(request: Request):
    requester_domain_origin = request.headers.get("Origin")
    
    # Lookup domain key in db
    try:
        lookup_response = client.table("API_KEYS").select("*").eq("domain", requester_domain_origin).execute().data[0]["key"]
        print(request.headers.get("API-Key"))
        print(lookup_response)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Domain not found")

    return lookup_response == request.headers.get("API-Key")

def get_validated_domains():
    # Lookup domain key in db
    lookup_response = client.table("API_KEYS").select("domain").execute().data
    
    return [domain["domain"] for domain in lookup_response]

@supabase_router.post("/request-api-key", summary="This is used for user signup with classic email and password")
async def request_api_key(request: Request):
    if validate_api_key(request):
        req_body = await request.json()
        email = req_body['email']
        password = req_body['password']
        
        # Generate API key and save it in db
        try:
            new_key = str(uuid.uuid4())
            client.table("API_KEYS").insert({"domain": request_body["domain"], "key": new_key, "created_at": datetime.now().isoformat()}).execute()
            return {"message": "API key generated successfully", "key": new_key}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Failed to generate API key")
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")

@supabase_router.post("/user-signup", summary="This is used for user signup with classic email and password")
async def signup(request: Request):
    if validate_api_key(request):
        req_body = await request.json()
        email = req_body['email']
        password = req_body['password']
        
        print(email, password)
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and Password headers are required")
        
        try:
            # client = get_supabase_client()
            response = client.auth.sign_up({"email": email, "password": password})
            return response
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")

@supabase_router.post("/user-signin", summary="This is used for user signin with classic email and password")
async def signin(
    request: Request
):
    if validate_api_key(request):
        email = request.headers.get("email")
        password = request.headers.get("password")
        
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
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")

@supabase_router.get("/github-signin", summary="This is used for user signup with the help of GitHub OAuth Application")
async def github_signin(request: Request):
    try:
        response = client.auth.sign_in_with_oauth(
            {"provider": "github",
             "options": {
                 "redirect_to": base_url + "/callback"
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
                 "redirect_to": base_url + "/callback"
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
        redirect_res = RedirectResponse(url=frontend_url + "/index.html", status_code=302)
        
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
            
            user = client.auth.get_user()
            print(user)
            print()
            print("================================================================")
            print()
            for attr in user.__dict__:
                print(f"{attr}: {user.__dict__[attr]}\n\n")

            user_identities = client.auth.get_user().user.identities
            print(user_identities)
            user_fullname = user_identities[0].identity_data["full_name"]
            print(f"User Fullname: {user_fullname}")
            
            # Set fullname dalam cookie
            fastapi_response = RedirectResponse(url=frontend_url + "/home.html", status_code=302)
            fastapi_response.set_cookie(key="access_token", value=access_token, httponly=True)
            fastapi_response.set_cookie(key="user_fullname", value=user_fullname, httponly=False)  # Menyimpan fullname di cookie
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