import json
import re

from datetime import datetime
from sqlalchemy import select
from .models import ActivityLog, DailyLog
from .session import AsyncSessionLocal

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

    today = datetime.utcnow().date()

    async with AsyncSessionLocal() as session:
        session.add(
            ActivityLog(
                user_id=user_id,
                type=log_type,
                raw_text=raw_text,
                ai_json=data,
            )
        )

        existing_daily = await session.scalar(
            select(DailyLog).where(
                DailyLog.user_id == user_id,
                DailyLog.log_date == today,
            )
        )

        if not existing_daily:
            session.add(
                DailyLog(
                    user_id=user_id,
                    log_date=today,
                    total_calories=kcal,
                    total_protein=protein,
                )
            )
        else:
            existing_daily.total_calories += kcal
            existing_daily.total_protein += protein

        await session.commit()

    return kcal, protein