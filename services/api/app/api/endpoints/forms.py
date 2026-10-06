from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models.form import Form, FormField
from app.schemas.form import FormSchema

router = APIRouter()

@router.get("/", response_model=List[FormSchema])
async def list_forms(db: AsyncSession = Depends(get_db)):
    """List all active forms with their fields."""
    result = await db.execute(
        select(Form).where(Form.is_active == True)
    )
    forms = result.scalars().all()
    # Explicitly load fields if not lazy loaded appropriately in prod
    # For now relying on standard sqlalchemy patterns
    return forms

@router.get("/{form_id}", response_model=FormSchema)
async def get_form(form_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific form by ID."""
    result = await db.execute(select(Form).where(Form.id == form_id))
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form
