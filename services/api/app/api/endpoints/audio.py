from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import aiofiles
from pathlib import Path

from app.database import get_db
from app.config import get_config
from app.models.audio import AudioRecord
from app.models.session import Session

router = APIRouter()

@router.post("/upload")
async def upload_audio(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload audio for a session."""
    config = get_config()
    
    # Verify session exists
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status not in ("created", "recording", "failed"):
        raise HTTPException(status_code=400, detail="Session cannot accept audio in current state")
        
    # Save file
    os.makedirs(config.storage.upload_dir, exist_ok=True)
    file_ext = Path(file.filename).suffix or ".webm"
    file_name = f"{session_id}{file_ext}"
    file_path = config.storage.upload_dir / file_name
    
    # Read file size (could enforce max size here)
    size = 0
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        size = len(content)
        await out_file.write(content)
        
    # Create DB record
    record = AudioRecord(
        session_id=session_id,
        file_path=str(file_path),
        file_name=file.filename,
        mime_type=file.content_type,
        file_size_bytes=size,
        status="uploaded"
    )
    db.add(record)
    
    # Update session status
    session.status = "uploaded"
    
    await db.commit()
    await db.refresh(record)
    
    # In a real app, this background task would trigger the ASR pipeline
    # background_tasks.add_task(process_audio_pipeline, session_id, record.id)
    
    return {"message": "Audio uploaded successfully", "audio_id": record.id}
