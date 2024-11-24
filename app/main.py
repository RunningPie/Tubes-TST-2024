from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request

from app.services.supabase import supabase_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Example: Get tasks from Supabase or another service
    tasks = [{"id": 1, "name": "Task 1"}, {"id": 2, "name": "Task 2"}]
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

app.include_router(supabase_router)
