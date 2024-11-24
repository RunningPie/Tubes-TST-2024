from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
from dotenv import load_dotenv
import os

load_dotenv()

from app.services.supabase import supabase_router, supabase_callback
from app.services.auth import JWTBearer

app = FastAPI(
    title="TaskHub-Hazel's API Documentation",  # Title of the API
    description="This is where you can find out how to use all available APIs in this project. Currently there are only authtentication routes",  # Description of the API
    version="1.0.0",  # Version of the API
    docs_url="/docs",  # URL path for the Swagger docs (default is /docs)
    redoc_url="/redoc"  # URL path for the ReDoc docs (optional)
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse, summary="This is the default route, used for health checking")
async def home(request: Request):
    # Example: Get tasks from Supabase or another service
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, summary="This is the route for registration")
async def register(request: Request):
    # Example: Get tasks from Supabase or another service
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/protected-home", dependencies=[Depends(JWTBearer())], summary="This is the default redirect after a successful login, using classic JWT")
def protected_route(request: Request):
    return templates.TemplateResponse("login_success.html", {"request": request})

app.include_router(supabase_router)
