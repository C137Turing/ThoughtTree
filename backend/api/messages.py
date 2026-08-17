"""Message and chat API endpoints including SSE streaming."""

import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sse_starlette.sse import EventSourceResponse
from db.mysql import get_db, async_session_factory
from graphs.chat_graph import _get_config, _get_llm
from models.message import Message
from models.session import Session
from models.schemas import ChatRequest, MessageResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

router = APIRouter(prefix="/api/sessions", tags=["chat"])


async def _load_history(session_id: str) -> list:
    messages = []
    async with async_session_factory() as session:
        result = await session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(40)
        )
        history = result.scalars().all()
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                messages.append(SystemMessage(content=msg.content))

    if not messages:
        messages.append(SystemMessage(content=(
            "You are an AI requirements analysis assistant. "
            "Help users explore and clarify their software requirements. "
            "When you mention technical terms, explain them clearly. "
            "Use Markdown for formatting. Be concise but thorough."
        )))
    return messages


async def _save_messages(session_id: str, user_content: str, ai_content: str) -> tuple[str, str]:
    async with async_session_factory() as session:
        user_msg = Message(session_id=session_id, role="user", content=user_content)
        ai_msg = Message(session_id=session_id, role="assistant", content=ai_content)
        session.add(user_msg)
        session.add(ai_msg)
        await session.flush()
        uid, aid = user_msg.id, ai_msg.id
        await session.commit()
    return uid, aid


async def _stream_chat(session_id: str, user_content: str) -> AsyncGenerator[dict, None]:
    provider, model, api_key = await _get_config()
    llm = _get_llm(provider, model, api_key)
    history = await _load_history(session_id)
    history.append(HumanMessage(content=user_content))

    full_response = ""
    try:
        async for chunk in llm.astream(history):
            if hasattr(chunk, "content") and chunk.content:
                delta = chunk.content
                full_response += delta
                yield {"event": "token", "data": json.dumps({"delta": delta})}
    except Exception as e:
        yield {"event": "error", "data": json.dumps({"message": str(e)})}
        return

    try:
        user_id, ai_id = await _save_messages(session_id, user_content, full_response)
        yield {"event": "done", "data": json.dumps({"message_id": ai_id})}
    except Exception as e:
        yield {"event": "error", "data": json.dumps({"message": str(e)})}


@router.post("/{session_id}/chat")
async def chat_stream(session_id: str, req: ChatRequest):
    async with async_session_factory() as session:
        result = await session.execute(select(Session).where(Session.id == session_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Session not found")
    return EventSourceResponse(_stream_chat(session_id, req.content))


@router.get("/{session_id}/messages")
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]
