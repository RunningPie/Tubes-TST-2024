from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import os
import app.services.rule_based_fuzzy_logic as rbfl
import app.services.supabase as supabase

rbfl_system = APIRouter()

# Validasi object yang dikirimkan di request
class Team(BaseModel):
    team_id: str
    team_name: str
    created_at: str
    creator_id: str

# Endpoint: Melihat task dari suatu team
@rbfl_system.post("/show-team-tasks", summary="Shows team tasks of a certain team")
async def show_team_tasks(team: dict):
    team_id = team["team_id"]
    response = supabase.client.table("task")\
        .select("task_name, priority")\
        .eq("team_id", team_id)\
        .execute()
    if response:
        return {"message": f"Showing tasks from team id: {team_id}", "data": response.data}
    raise HTTPException(status_code=response.status_code, detail=response.model_dump_json())
