"""Session CRUD API endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.mysql import get_db, async_session_factory
from models.session import Session
from models.session_tree import SessionTree
from models.schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


async def _maintain_closure(session: AsyncSession, session_id: str, parent_id: Optional[str]) -> None:
    """Update closure table when a session's parent changes."""
    await session.execute(
        delete(SessionTree).where(SessionTree.descendant_id == session_id)
    )
    session.add(SessionTree(ancestor_id=session_id, descendant_id=session_id, depth=0))
    if parent_id:
        result = await session.execute(
            select(SessionTree).where(SessionTree.descendant_id == parent_id)
        )
        for st in result.scalars().all():
            session.add(SessionTree(
                ancestor_id=st.ancestor_id,
                descendant_id=session_id,
                depth=st.depth + 1,
            ))
    await session.flush()


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """Get all sessions."""
    query = select(Session).order_by(Session.created_at.desc())
    if status:
        query = query.where(Session.status == status)
    result = await db.execute(query)
    return [SessionResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    req: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new session."""
    session_id = str(uuid.uuid4())
    root_id = req.root_id or session_id

    db_session = Session(
        id=session_id,
        title=req.title,
        parent_id=req.parent_id,
        root_id=root_id,
        status="open",
    )
    db.add(db_session)
    await db.flush()
    await _maintain_closure(db, session_id, req.parent_id)
    await db.commit()
    return SessionResponse.model_validate(db_session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(s)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, req: SessionUpdate, db: AsyncSession = Depends(get_db)):
    """Update a session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    update_data = req.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(Session).where(Session.id == session_id).values(**update_data))
        await db.flush()
        await db.refresh(s)
    return SessionResponse.model_validate(s)


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session. Children promoted via SET NULL FK."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(s)
    await db.commit()


@router.get("/{session_id}/tree", response_model=list[SessionResponse])
async def get_session_tree(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get subtree."""
    result = await db.execute(
        select(Session)
        .join(SessionTree, Session.id == SessionTree.descendant_id)
        .where(SessionTree.ancestor_id == session_id)
        .order_by(SessionTree.depth)
    )
    return [SessionResponse.model_validate(s) for s in result.scalars().all()]