import json
import re

from datetime import datetime

import supabase

async def save_jhingoor_data(user_id: int, raw_text: str, ai_response: str):
    # 1. Extract JSON from AI text using Regex
    json_pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, ai_response, re.DOTALL)
    
    if not match:
        return None # Just a regular chat, no data to log
        
    data = json.loads(match.group(1))
    kcal = data.get("calories", 0)
    protein = data.get("protein", 0)
    log_type = data.get("type", "food")

    # 2. Insert into activity_logs
    supabase.table("activity_logs").insert({
        "user_id": user_id,
        "type": log_type,
        "raw_text": raw_text,
        "ai_json": data
    }).execute()

    # 3. Upsert into daily_logs
    today = datetime.utcnow().date().isoformat()
    
    # We use 'rpc' (Remote Procedure Call) or a manual select/update
    # For a clean interview demo, let's do a select then update
    res = supabase.table("daily_logs").select("*").eq("user_id", user_id).eq("log_date", today).execute()
    
    if not res.data:
        supabase.table("daily_logs").insert({
            "user_id": user_id,
            "total_calories": kcal,
            "total_protein": protein
        }).execute()
    else:
        new_kcal = res.data[0]['total_calories'] + kcal
        new_protein = res.data[0]['total_protein'] + protein
        supabase.table("daily_logs").update({
            "total_calories": new_kcal,
            "total_protein": new_protein
        }).eq("user_id", user_id).eq("log_date", today).execute()
        
    return kcal, protein