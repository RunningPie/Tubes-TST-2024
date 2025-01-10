from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import os
import app.services.rule_based_fuzzy_logic as rbfl
import app.services.supabase as supabase
import uuid

rbfl_router = APIRouter()

# Endpoint: Membuat simple rbfl
@rbfl_router.post("/create-rbfl", summary="create a new rule based fuzzy logic for your service")
async def create_rbfl(request: Request):
    if supabase.validate_api_key(request):
        new_rbfl_details = await request.json()   
        new_rbfl_details["creator_key"] = request.headers.get("API-Key")
        new_rbfl_details["id"] = str(uuid.uuid4())
        if "sandbox" not in request.headers:
            new_rbfl = Simple_RBFL(**new_rbfl_details)
            
            response = supabase.client.table("rbfl_systems").insert(new_rbfl.model_dump()).execute()
            if response:
                return {"message": "Rule Based Fuzzy Logic created successfully", "response": response}
            raise HTTPException(status_code=500, detail=response.model_dump_json())
        else:
            return {
                "message": "Sandbox Rule Based Fuzzy Logic created successfully",
                "response": {
                    "data": [
                        new_rbfl_details
                    ],
                    "count": None
                }
            }

# Endpoint: Memprediksi menggunakan simple rbfl
@rbfl_router.get("/rbfl-evaluate", summary="Evaluates your rules against a new object with the variables you've set before.")
async def predict_rbfl(request: Request):
    if supabase.validate_api_key(request):
        if "sandbox" in request.headers:
            return { "message": "Evaluation Successful", "Evaluation Score": 99.99 }
        else:
            lookup_rbfl = supabase.client.table("rbfl_systems").select("*")\
                .eq("id", request.query_params.get("id"))\
                .eq("creator_key", request.headers.get("API-Key")).data
            if len(lookup_rbfl) == 0:
                raise HTTPException(status_code=404, detail="Rule Based Fuzzy Logic not found")
            else:
                input_variables = [
                    (lookup_rbfl[0]["variable1_name"], lookup_rbfl[0]["variable1_min"], lookup_rbfl[0]["variable1_max"]),
                    (lookup_rbfl[0]["variable2_name"], lookup_rbfl[0]["variable2_min"], lookup_rbfl[0]["variable2_max"])
                ]
                rbfl_router = rbfl.simple_fuzzy(input_variables)
                
                results = rbfl_router.evaluate([
                    float(request.query_params.get("variable1")),
                    float(request.query_params.get("variable2"))
                ])
                
                return {"message": "Evaluation successful", "Evaluation Score": results}