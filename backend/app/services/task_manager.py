from fastapi import APIRouter, HTTPException, Depends, Header, Request
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import os
import app.services.rule_based_fuzzy_logic as rbfl
import app.services.supabase as supabase

taskmanager_router = APIRouter()

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
        
def determine_task_assignee(team_id, task_priority):
    req_member_ids = supabase.client.table("team_members").select("member_id").eq("team_id", team_id).execute().data
    team_members = []
    for member_id in req_member_ids:
        team_members.append(member_id["member_id"])
    
    member_suitabilities = {}
    for member_id in team_members:
        print(member_id)
        req_availability = supabase.client.table("availability").select("*").eq("member_id", member_id).execute().data
        total_available_time = 0
        for availability in req_availability:
            start_time = datetime.fromisoformat(availability["start_time"])
            end_time = datetime.fromisoformat(availability["end_time"])
            curr_available_time = (end_time - start_time).total_seconds()/3600
            total_available_time += curr_available_time
        print(f"Member {member_id} has total available time of {total_available_time} for {len(req_availability)} entries")
        
        req_tasks = supabase.client.table("task").select("*").eq("assigned_to", member_id).execute().data
        total_priority = 0
        for task in req_tasks:
            total_priority += int(task["priority"])
        avg_priority = total_priority/len(req_tasks) if len(req_tasks) > 0 else 5
        print(f"Member {member_id} has average priority of {avg_priority} for {len(req_tasks)} tasks")
        
        rbfl_system = rbfl.create_workload_availability_system()
        suitability_score = rbfl_system.evaluate({
            "workload": total_available_time,
            "availability": avg_priority
        })
        member_suitabilities[member_id] = suitability_score
    
    # Sort member suitability scores
    sorted_suitability_scores = dict(sorted(member_suitabilities.items(), key=lambda item: item[1], reverse=True))
    print(f"Sorted member suitability scores: {sorted_suitability_scores}")
    
    # Ambil member yang memiliki skor tertinggi
    best_suitable_member = list(sorted_suitability_scores.keys())[:int(task_priority)][-1]
    print(f"Best suitable member: {best_suitable_member}")
    
    return best_suitable_member
    

# Endpoint: Membuat team baru
@taskmanager_router.post("/create-team", summary="Create a new team")
async def create_team(request: Request):
    if supabase.validate_api_key(request):
        if "sandbox" in request.headers:
            new_team_details = await request.json()
            return {
                "message": "Sandbox Team created successfully",
                "response": {
                    "data": [
                        {
                            "team_id": "0",
                            "team_name": new_team_details["team_name"],
                            "created_at": "2222-01-09T20:20:13.61856+00:00",
                            "creator_id": "e6e6e6e6-9b9b-4545-9a9a-edededededed"
                        }
                    ],
                    "count": None
                }
            }
        else:
            try:
                access_token = request.cookies.get("access_token")
                new_creator_id = supabase.client.auth.get_user(access_token).user.id
            except Exception as e:
                # Apabila service yang menembak API endpoint ini, bukan user dari webapp sendiri
                print(e)
                access_token = request.headers.get("API-Key")
                new_creator_id = access_token
            
            new_team_details = await request.json()
            
            # Validate json body
            validate_request_json(new_team_details, "team_name")
            
            # Membuat id team baru dengan metode auto increment
            req_team_ids = supabase.client.table("teams").select("team_id").execute()
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
                creator_id=new_creator_id
            )
            
            response = supabase.client.table("teams").insert(new_team_data.model_dump()).execute()
            if response:
                return {"message": "Team created successfully", "response": response}
            raise HTTPException(status_code=500, detail=response.model_dump_json())
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Endpoint: Menambahkan anggota ke team
@taskmanager_router.post("/add-team-member", summary="Add a new team member to a team")
async def add_team_member(request: Request):
    new_member_details = await request.json()
    
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Team member added successfully",
            "response": {
                "data": [
                    {
                        "member_id": "1",
                        "member_name": new_member_details["member_name"],
                        "team_id": new_member_details["team_id"],
                        "role": new_member_details.get("role", "Member"),
                        "created_at": "2222-01-09T20:20:13.61856+00:00"
                    }
                ],
                "count": None
            }
        }
    
    # Validate json body
    validate_request_json(new_member_details, "team_id", "member_name")
    
    # Validate if current user is allowed to add to the team id
    try:
        creator_id = supabase.client.table("teams").select("creator_id").eq("team_id", new_task_details["team_id"]).execute().data[0]["creator_id"]
        print(creator_id)
        if current_user!= creator_id:
            raise HTTPException(status_code=403, detail="You are not authorized to add team members to this team")
    except:
        raise HTTPException(status_code=404, detail="Team not found")


    # Membuat id anggota team baru dengan metode auto increment
    req_member_ids = supabase.client.table("team_members").select("member_id").execute()
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
    
    response = supabase.client.table("team_members").insert(new_member_data.model_dump()).execute()
    if response:
        return {"message": "Team member added successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())

# Endpoint: Menambahkan ketersediaan anggota team
@taskmanager_router.post("/add-members-availability", summary="Add a certain member's availability")
async def add_member_avail(request: Request):
    new_avail_details = await request.json()
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Member availability added successfully",
            "response": {
                "data": [
                    {
                        "member_id": new_avail_details["member_id"],
                        "start_time": new_avail_details["start_time"],
                        "end_time": new_avail_details["end_time"],
                        "created_at": "2222-01-09T20:20:13.61856+00:00"
                    }
                ],
                "count": None
            }
        }

    # Validate json body
    validate_request_json(new_avail_details, "member_id", "start_time", "end_time")
    
    new_created_at = datetime.now().isoformat()

    new_avail_data = Availability(
        member_id = new_avail_details["member_id"],
        start_time = new_avail_details["start_time"],
        end_time = new_avail_details["end_time"],
        created_at = new_created_at
    )
    
    response = supabase.client.table("availability").insert(new_avail_data.model_dump()).execute()
    if response:
        return {"message": "Member availability added successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())
    
# Endpoint: Menambahkan task milik team
@taskmanager_router.post("/add-team-task", summary="Add a certain team's availability")
async def add_team_task(request: Request):
    new_task_details = await request.json()
    
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Team task added successfully",
            "response": {
                "data": [
                    {
                        "team_id": new_task_details["team_id"],
                        "task_name": new_task_details["task_name"],
                        "priority": new_task_details["priority"],
                        "assigned_to": "1",  # Dummy assigned member ID
                        "created_at": "2222-01-09T20:20:13.61856+00:00"
                    }
                ],
                "count": None
            }
        }
    
    # Validate json body
    validate_request_json(new_task_details, "team_id", "task_name", "priority")
    
    # Validate if current user is allowed to add to the team id
    try:
        access_token = request.cookies.get("access_token")
        current_user = supabase.client.auth.get_user(access_token).user.id
    except Exception as e:
        print(e)
        access_token = request.headers.get("API-Key")
        current_user = access_token

    try:
        creator_id = supabase.client.table("teams").select("creator_id").eq("team_id", new_task_details["team_id"]).execute().data[0]["creator_id"]
        print(creator_id)
        if current_user!= creator_id:
            raise HTTPException(status_code=403, detail="You are not authorized to add team tasks to this team")
    except:
        raise HTTPException(status_code=404, detail="Team not found")

    new_created_at = datetime.now().isoformat()
    new_task_assignee = determine_task_assignee(team_id=new_task_details["team_id"], task_priority=new_task_details["priority"])
    print(new_task_assignee)

    new_task_data = Task(
        team_id = new_task_details["team_id"],
        task_name = new_task_details["task_name"],
        priority = new_task_details["priority"],
        assigned_to = new_task_assignee,
        created_at = new_created_at
    )
    
    response = supabase.client.table("task").insert(new_task_data.model_dump()).execute()
    if response:
        return {"message": "Member task added successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())
    
# Endpoint: Melihat team
@taskmanager_router.get("/show-teams", summary="Shows team members of a certain team")
async def show_teams(request: Request):
    if supabase.validate_api_key(request):
        print(request.headers)
        if "sandbox" not in request.headers:
            try:
                access_token = request.cookies.get("access_token")
                curr_user = supabase.client.auth.get_user(access_token).user.id
            except Exception as e:
                print(e)
                access_token = request.headers.get("API-Key")
                curr_user = access_token
            
            response = supabase.client.table("teams")\
                .select("team_id, team_name")\
                .eq("creator_id", curr_user)\
                .execute()
            if response:
                return {"message": f"Showing teams created by: {curr_user}", "data": response.data}
            raise HTTPException(status_code=500, detail=response.model_dump_json())
        else:
            return {
                "message": "Showing teams created by: Sanbox",
                "data": [
                    {
                        "team_id": "1",
                        "team_name": "testing1"
                    },
                    {
                        "team_id": "2",
                        "team_name": "testing2"
                    },
                    {
                        "team_id": "3",
                        "team_name": "testing3"
                    }
                ]
            }
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
# Endpoint: Melihat anggota team
@taskmanager_router.get("/show-team-members", summary="Shows team members of a certain team")
async def show_team_member(request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Showing members from team id: 1",
            "data": [
                {
                    "member_name": "John Doe",
                    "role": "Leader",
                    "teams": {
                        "team_name": "testing1"
                    }
                },
                {
                    "member_name": "Jane Smith",
                    "role": "Developer",
                    "teams": {
                        "team_name": "testing1"
                    }
                }
            ]
        }
    try:
        access_token = request.cookies.get("access_token")
        curr_user = supabase.client.auth.get_user(access_token).user.id
    except Exception as e:
        print(e)
        access_token = request.headers.get("API-Key")
        curr_user = access_token

    team_id = request.query_params.get("team_id")

    team_creator = supabase.client.table("teams").select("creator_id").eq("team_id", team_id).data
    if (team_creator != curr_user):
        raise HTTPException(status_code=403, detail="You are not authorized to view team members")
    
    response = supabase.client.table("team_members")\
        .select("member_name, role, teams(team_name)")\
        .eq("team_id", team_id)\
        .execute()
    if response:
        return {"message": f"Showing members from team id: {team_id}", "data": response.data}
    raise HTTPException(status_code=500, detail=response.model_dump_json())
    
# Endpoint: Melihat task dari suatu team
@taskmanager_router.get("/show-team-tasks", summary="Shows team tasks of a certain team")
async def show_team_tasks(request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Showing tasks from team id: 1",
            "data": [
                {
                    "task_name": "Implement Login",
                    "priority": 1
                },
                {
                    "task_name": "Create Database",
                    "priority": 2
                },
                {
                    "task_name": "Write Documentation",
                    "priority": 3
                }
            ]
        }

    try:
        access_token = request.cookies.get("access_token")
        curr_user = supabase.client.auth.get_user(access_token).user.id
    except Exception as e:
        print(e)
        access_token = request.headers.get("API-Key")
        curr_user = access_token

    team_id = request.query_params.get("team_id")
    
    team_creator = supabase.client.table("teams").select("creator_id").eq("team_id", team_id).data
    if (team_creator != curr_user):
        raise HTTPException(status_code=403, detail="You are not authorized to view team members")

    response = supabase.client.table("task")\
        .select("task_name, priority")\
        .eq("team_id", team_id)\
        .execute()
    if response:
        return {"message": f"Showing tasks from team id: {team_id}", "data": response.data}
    raise HTTPException(status_code=500, detail=response.model_dump_json())

# Endpoint: Menghapus anggota dari tim
@taskmanager_router.delete("/remove-team-member", summary="Remove a team member")
async def remove_team_member(request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Team member removed successfully",
            "response": {
                "data": [],
                "count": None
            }
        }

    request_data = await request.json()
    validate_request_json(request_data, "team_id", "member_id")

    team_id = request_data["team_id"]
    member_id = request_data["member_id"]

    response = supabase.client.table("team_members").delete().eq("team_id", team_id).eq("member_id", member_id).execute()
    if response:
        return {"message": "Team member removed successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())

# Endpoint: Melihat ketersediaan anggota
@taskmanager_router.get("/view-availability", summary="View team members' availability")
async def view_availability(team_id: str, request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Team members' availability",
            "data": [
                {
                    "member_id": "1",
                    "start_time": "2222-01-09T09:00:00",
                    "end_time": "2222-01-09T17:00:00",
                    "created_at": "2222-01-09T20:20:13.61856+00:00"
                },
                {
                    "member_id": "2",
                    "start_time": "2222-01-09T10:00:00",
                    "end_time": "2222-01-09T18:00:00",
                    "created_at": "2222-01-09T20:20:13.61856+00:00"
                }
            ]
        }

    response = supabase.client.table("availability").select("*").eq("team_id", team_id).execute()
    if response:
        return {"message": "Team members' availability", "data": response.data}
    raise HTTPException(status_code=500, detail=response.model_dump_json())

# Endpoint: Menghapus ketersediaan anggota
@taskmanager_router.delete("/remove-availability", summary="Remove a team member's availability")
async def remove_availability(request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Availability removed successfully",
            "response": {
                "data": [],
                "count": None
            }
        }

    request_data = await request.json()
    validate_request_json(request_data, "member_id", "start_time")

    member_id = request_data["member_id"]
    start_time = request_data["start_time"]

    response = supabase.client.table("availability").delete().eq("member_id", member_id).eq("start_time", start_time).execute()
    if response:
        return {"message": "Availability removed successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())

# Endpoint: Menghapus tugas
@taskmanager_router.delete("/remove-task", summary="Remove a task")
async def remove_task(request: Request):
    if "sandbox" in request.headers:
        return {
            "message": "Sandbox Task removed successfully",
            "response": {
                "data": [],
                "count": None
            }
        }

    request_data = await request.json()
    validate_request_json(request_data, "team_id", "task_name")

    team_id = request_data["team_id"]
    task_name = request_data["task_name"]

    response = supabase.client.table("task").delete().eq("team_id", team_id).eq("task_name", task_name).execute()
    if response:
        return {"message": "Task removed successfully", "response": response}
    raise HTTPException(status_code=500, detail=response.model_dump_json())