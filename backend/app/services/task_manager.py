from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from supabase import Client, create_client
import os

taskmanager_router = APIRouter()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Validasi object yang dikirimkan ke database
class Team(BaseModel):
    team_id: str
    team_name: str
    created_at: str
    creator_id: str
    
class TeamMember(BaseModel):
    member_id: str
    member_name: str
    team_id: int
    role: str
    created_at: str

class Availability(BaseModel):
    member_id: str
    start_time: str
    end_time: str
    created_at: str

class Task(BaseModel):
    team_id: str
    task_name: str
    priority: int
    assigned_to: str
    created_at: str
    
def validate_request_json(request_json, *keys_to_validate):
    for key in keys_to_validate:
        if key not in request_json:
            raise HTTPException(status_code=400, detail=f"Missing required key: {key}")

# Endpoint: Membuat team baru
@taskmanager_router.post("/create-team", summary="Create a new team")
async def create_team(new_team_details: dict):
    
    # Validate json body
    validate_request_json(new_team_details, "team_name", "creator_id")
    
    # Membuat id team baru dengan metode auto increment
    req_team_ids = client.table("teams").select("team_id").execute()
    curr_team_ids = []
    for team_id in req_team_ids.data:
        curr_team_ids.append(team_id["team_id"])
    try:
        max_team_id = max(curr_team_ids)
    except:
        max_team_id = 0
    new_team_id = str(int(max_team_id) + 1) # melakukan increment ke max team id
    
    new_created_at = datetime.now().isoformat()
    new_team_data = Team(
        team_id=new_team_id,
        team_name=new_team_details["team_name"],
        created_at=new_created_at,
        creator_id=new_team_details["creator_id"]
    )
    
    response = client.table("teams").insert(new_team_data.model_dump()).execute()
    if response:
        return {"message": "Team created successfully", "response": response}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())

# Endpoint: Menambahkan anggota ke team
@taskmanager_router.post("/add-team-member", summary="Add a new team member to a team")
async def add_team_member(new_member_details: dict):
    
    # Validate json body
    validate_request_json(new_member_details, "team_id", "member_name")
    
    # Membuat id anggota team baru dengan metode auto increment
    req_member_ids = client.table("team_members").select("member_id").execute()
    curr_member_ids = []
    for member_id in req_member_ids.data:
        curr_member_ids.append(member_id["member_id"])
    try:
        max_member_id = max(curr_member_ids)
    except:
        max_member_id = 0
    new_member_id = str(int(max_member_id) + 1) # melakukan increment ke max team id
    
    new_created_at = datetime.now().isoformat()
    try:
        new_member_role = new_member_details["role"]
    except KeyError:
        new_member_role = ""
    new_member_data = TeamMember(
        member_id=new_member_id,
        team_id=new_member_details["team_id"],
        member_name=new_member_details["member_name"],
        role=new_member_role,
        created_at=new_created_at,
    )
    
    response = client.table("team_members").insert(new_member_data.model_dump()).execute()
    if response:
        return {"message": "Team member added successfully", "response": response}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())

# Endpoint: Menambahkan ketersediaan anggota team
@taskmanager_router.post("/add-members-availability", summary="Add a certain member's availability")
async def add_member_avail(new_avail_details: dict):
    
    # Validate json body
    validate_request_json(new_avail_details, "member_id", "start_time", "end_time")
    
    new_created_at = datetime.now().isoformat()

    new_avail_data = Availability(
        member_id = new_avail_details["member_id"],
        start_time = new_avail_details["start_time"],
        end_time = new_avail_details["end_time"],
        created_at = new_created_at
    )
    
    response = client.table("availability").insert(new_avail_data.model_dump()).execute()
    if response:
        return {"message": "Member availability added successfully", "response": response}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())
    
# Endpoint: Menambahkan task milik team
@taskmanager_router.post("/add-team-task", summary="Add a certain team's availability")
async def add_member_avail(new_task_details: dict):
    
    # Validate json body
    validate_request_json(new_task_details, "team_id", "task_name", "priority")
    
    new_created_at = datetime.now().isoformat()
    new_task_assignee = "1"

    new_task_data = Task(
        team_id = new_task_details["team_id"],
        task_name = new_task_details["task_name"],
        priority = new_task_details["priority"],
        assigned_to = new_task_assignee,
        created_at = new_created_at
    )
    
    response = client.table("task").insert(new_task_data.model_dump()).execute()
    if response:
        return {"message": "Member task added successfully", "response": response}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())
    
# Endpoint: Melihat anggota team
@taskmanager_router.get("/show-team-members", summary="Shows team members of a certain team")
async def show_team_member(team: dict):
    team_id = team["team_id"]
    response = client.table("team_members")\
        .select("member_name, role")\
        .eq("team_id", team_id)\
        .execute()
    if response:
        return {"message": f"Showing members from team id: {team_id}", "data": response.data}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())
    
# Endpoint: Melihat task dari suatu team
@taskmanager_router.get("/show-team-tasks", summary="Shows team tasks of a certain team")
async def show_team_member(team: dict):
    team_id = team["team_id"]
    response = client.table("task")\
        .select("task_name, priority")\
        .eq("team_id", team_id)\
        .execute()
    if response:
        return {"message": f"Showing tasks from team id: {team_id}", "data": response.data}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())
