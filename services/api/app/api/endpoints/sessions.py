from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.session import Session
from app.schemas.session import SessionSchema, SessionCreate, SessionStatusUpdate

router = APIRouter()

# Note: In a real app, user_id would come from auth token Dependency
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001" 

@router.post("/", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new data capture session."""
    db_session = Session(
        user_id=MOCK_USER_ID,
        form_id=session_in.form_id,
        organization_id=session_in.organization_id,
        title=session_in.title,
        language=session_in.language,
        status="created"
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@router.get("/{session_id}", response_model=SessionSchema)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.patch("/{session_id}/status", response_model=SessionSchema)
async def update_session_status(
    session_id: str, 
    status_update: SessionStatusUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update session state machine status."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not session.can_transition_to(status_update.status):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid state transition from {session.status} to {status_update.status}"
        )
        
    session.status = status_update.status
    await db.commit()
    await db.refresh(session)
    return session
