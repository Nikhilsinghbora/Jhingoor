from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str


class ChatHistoryOut(BaseModel):
    messages: list[ChatMessageOut]


class ChatSendIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatSendOut(BaseModel):
    reply: str


@router.get("/messages", response_model=ChatHistoryOut)
async def list_messages(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
) -> ChatHistoryOut:
    res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    rows = list(reversed(res.scalars().all()))
    return ChatHistoryOut(
        messages=[ChatMessageOut(id=str(m.id), role=m.role, content=m.content) for m in rows]
    )


@router.post("/messages", response_model=ChatSendOut)
async def send_message(
    body: ChatSendIn,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> ChatSendOut:
    user_msg = ChatMessage(id=uuid4(), user_id=user.id, role="user", content=body.message)
    db.add(user_msg)
    await db.flush()
    try:
        from bot.brain import process_multimodel

        reply = await process_multimodel(prompt=body.message)
    except Exception:
        await db.rollback()
        raise
    db.add(ChatMessage(id=uuid4(), user_id=user.id, role="assistant", content=reply))
    await db.commit()
    return ChatSendOut(reply=reply)
