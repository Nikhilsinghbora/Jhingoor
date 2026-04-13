from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime

class Base(DeclarativeBase):
    pass

class Profile(Base):
    __tablename__ = "profiles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    daily_goal_kcal: Mapped[int] = mapped_column(Integer, default=2000)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profiles.id"))
    type: Mapped[str] = mapped_column(String) # 'food', 'workout', 'chat'
    raw_text: Mapped[str] = mapped_column(String, nullable=True)
    ai_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profiles.id"), primary_key=True)
    log_date: Mapped[date] = mapped_column(Date, primary_key=True, server_default=func.current_date())
    total_calories: Mapped[int] = mapped_column(Integer, default=0)
    total_protein: Mapped[int] = mapped_column(Integer, default=0)
    water_intake_ml: Mapped[int] = mapped_column(Integer, default=0)