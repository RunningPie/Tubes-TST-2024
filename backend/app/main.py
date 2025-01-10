from fastapi import Depends, FastAPI, Request
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from dotenv import load_dotenv
import os

load_dotenv()

from app.services.supabase import supabase_router, get_validated_domains
from app.services.task_manager import taskmanager_router
from app.services.simple_rbfl_system import rbfl_router

app = FastAPI(
    title="TaskHub-Hazel's API Documentation",  # Title of the API
    description="This is where you can find out how to use all available APIs in this project. Currently there are only authtentication routes",  # Description of the API
    version="1.0.0",  # Version of the API
    docs_url="/docs",  # URL path for the Swagger docs (default is /docs)
    redoc_url="/redoc"  # URL path for the ReDoc docs (optional)
)

allowed_origins = get_validated_domains()
print(allowed_origins)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode (GET, POST, dll.)
    allow_headers=["*"],  # Mengizinkan semua header
)

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=JSONResponse, summary="This is the default route, used for health checking")
async def home(request: Request):
    # Example: Get tasks from Supabase or another service
    return {"message": "This is the default route, used for health checking"}

# @app.get("/register", response_class=HTMLResponse, summary="This is the route for registration")
# async def register(request: Request):
#     pass
#     # Example: Get tasks from Supabase or another service
#     # return templates.TemplateResponse("register.html", {"request": request})

@app.get("/protected-home", summary="This is the default redirect after a successful login, using classic JWT")
def protected_route(request: Request):
    return {"message": "This is a fallback page. You have successfully logged in but the frontend is likely responding"}
    # return templates.TemplateResponse("login_success.html", {"request": request})

app.include_router(supabase_router)
app.include_router(taskmanager_router)
app.include_router(rbfl_router)

for route in app.routes:
    print(route.path, route.name)