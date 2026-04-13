from sqlalchemy import select, update
from .models import Profile, ActivityLog, DailyLog
from datetime import date

async def get_or_create_profile(session, user_id, name):
    res = await session.execute(select(Profile).where(Profile.telegram_id == user_id))
    profile = res.scalar_one_or_none()
    
    if not profile:
        profile = Profile(telegram_id=user_id, name=name)
        session.add(profile)
        await session.commit()
    return profile

async def log_user_activity(session, user_id, log_type, raw_text, ai_data):
    # 1. Add to Activity Log
    new_activity = ActivityLog(
        user_id=user_id,
        type=log_type,
        raw_text=raw_text,
        ai_json=ai_data
    )
    session.add(new_activity)
    
    # 2. Extract numbers
    kcal = ai_data.get("calories", 0)
    protein = ai_data.get("protein", 0)
    
    # 3. Upsert into Daily Log
    today = date.today()
    res = await session.execute(
        select(DailyLog).where(DailyLog.user_id == user_id, DailyLog.log_date == today)
    )
    daily = res.scalar_one_or_none()
    
    if not daily:
        daily = DailyLog(user_id=user_id, log_date=today, total_calories=kcal, total_protein=protein)
        session.add(daily)
    else:
        daily.total_calories += kcal
        daily.total_protein += protein
    
    await session.commit()
    return kcal, protein