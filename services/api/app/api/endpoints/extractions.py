from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.config import get_config
from app.models.session import Session
from app.models.form import Form
from app.models.audio import AudioRecord
from app.models.transcript import Transcript, TranscriptSegment as DBTranscriptSegment
from app.models.extraction import ExtractedField, EvidenceSpan
from app.schemas.extraction import ExtractedFieldSchema, ExtractedFieldUpdate

from ai.asr.providers import get_asr_provider
from ai.dialect.classifier import get_dialect_classifier
from ai.extraction.extractor import get_semantic_extractor
from ai.validation.validator import validate_field
from ai.confidence.estimator import calculate_field_confidence

router = APIRouter()

@router.post("/{session_id}/process")
async def process_session_pipeline(session_id: str, db: AsyncSession = Depends(get_db)):
    """Run the complete AI pipeline (ASR -> Semantics -> Validation -> Evidence)."""
    
    # 1. Load Session and Form
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.form).selectinload(Form.fields))
        .options(selectinload(Session.audio_records))
        .where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not session.audio_records:
        raise HTTPException(status_code=400, detail="No audio records found for session")
        
    # Get form schema
    schema = [
        {
            "id": f.id,
            "field_key": f.field_key,
            "label": f.label,
            "label_local": f.label_local,
            "field_type": f.field_type,
            "required": f.required,
            "risk_level": f.risk_level,
            "enum_values": f.enum_values,
            "min_value": f.min_value,
            "max_value": f.max_value,
            "unit": f.unit,
        }
        for f in session.form.fields
    ]
    
    config = get_config()
    session.status = "transcribing"
    await db.commit()
    
    try:
        # 2. ASR Phase
        asr = get_asr_provider(config.providers.asr_provider)
        # Assuming audio file exists, normally read bytes here
        audio_bytes = b"dummy_audio_bytes" 
        
        # Use mock scenario based on session notes or default to 01
        scenario = "tamil_agriculture_01"
        if session.notes and "scenario: " in session.notes:
            scenario = session.notes.split("scenario: ")[1].strip()
            
        asr_result = await asr.transcribe(audio_bytes, language=session.language, context={"scenario": scenario})
        
        db_transcript = Transcript(
            session_id=session.id,
            audio_id=session.audio_records[0].id,
            language=asr_result.language,
            full_text=asr_result.text,
            asr_provider=asr_result.provider,
            asr_model=asr_result.model,
            asr_model_version=asr_result.model_version,
            latency_ms=asr_result.latency_ms,
        )
        db.add(db_transcript)
        await db.commit()
        await db.refresh(db_transcript)
        
        for i, seg in enumerate(asr_result.segments):
            db_seg = DBTranscriptSegment(
                transcript_id=db_transcript.id,
                segment_index=i,
                text=seg.text,
                start_time=seg.start,
                end_time=seg.end,
                confidence=seg.confidence,
                language=seg.language,
            )
            db.add(db_seg)
            
        session.status = "transcribed"
        await db.commit()
        
        # 3. Dialect/Language Phase
        dialect_clf = get_dialect_classifier()
        dialect_result = await dialect_clf.classify(asr_result.text, asr_result.language)
        session.dialect = dialect_result.dialect
        session.dialect_confidence = dialect_result.confidence
        
        # 4. Semantic Extraction Phase
        session.status = "extracting"
        await db.commit()
        
        extractor = get_semantic_extractor(config.providers.semantic_provider)
        # Convert segments to dicts as expected by interface
        segments_dict = [{"text": s.text, "start": s.start, "end": s.end} for s in asr_result.segments]
        
        extract_result = await extractor.extract(
            transcript=asr_result.text,
            segments=segments_dict,
            schema=schema,
            language=session.language,
            dialect=session.dialect,
        )
        
        session.status = "extracted"
        
        # 5. Validation, Confidence & Evidence Phase
        session.status = "validating"
        schema_map = {f["field_key"]: f for f in schema}
        
        extracted_db_fields = []
        for field in extract_result.fields:
            field_def = schema_map.get(field.field_key)
            if not field_def:
                continue
                
            # Validate
            errors = validate_field(field.field_key, field.value, field_def)
            is_valid = len(errors) == 0
            
            # Confidence
            # Estimate ASR confidence based on matching segment if evidence exists
            asr_conf = 1.0
            if field.evidence:
                # Find matching segment for confidence
                matched = next((s for s in asr_result.segments if s.text == field.evidence.text), None)
                if matched:
                    asr_conf = matched.confidence
                    
            conf_result = calculate_field_confidence(
                model_confidence=field.confidence,
                asr_confidence=asr_conf,
                certainty=field.certainty,
                is_valid=is_valid,
                risk_level=field_def.get("risk_level", "low")
            )
            
            db_field = ExtractedField(
                session_id=session.id,
                field_key=field.field_key,
                value=str(field.value) if field.value is not None else None,
                value_type=field_def.get("field_type", "string"),
                model_confidence=field.confidence,
                heuristic_confidence=conf_result["heuristic_confidence"],
                final_confidence=conf_result["final_confidence"],
                status=conf_result["status"],
                certainty=field.certainty,
                extraction_provider=extract_result.provider,
                extraction_model=extract_result.model,
            )
            db.add(db_field)
            await db.commit()
            await db.refresh(db_field)
            extracted_db_fields.append(db_field)
            
            # Add Evidence Span
            if field.evidence:
                # Need to lookup the actual transcript_segment_id from DB using start time
                db_seg = await db.execute(
                    select(DBTranscriptSegment).where(
                        DBTranscriptSegment.transcript_id == db_transcript.id,
                        DBTranscriptSegment.start_time == field.evidence.start
                    )
                )
                db_seg_match = db_seg.scalar_one_or_none()
                
                evidence = EvidenceSpan(
                    extracted_field_id=db_field.id,
                    audio_id=session.audio_records[0].id,
                    transcript_segment_id=db_seg_match.id if db_seg_match else None,
                    evidence_text=field.evidence.text,
                    start_time=field.evidence.start,
                    end_time=field.evidence.end,
                    span_type="transcript"
                )
                db.add(evidence)
        
        await db.commit()
        
        # Check if clarification is needed
        needs_review = any(f.status == "needs_review" for f in extracted_db_fields)
        if needs_review:
            session.status = "needs_clarification"
        else:
            session.status = "under_review"
            
        await db.commit()
        
        return {"message": "Pipeline completed", "status": session.status}

    except Exception as e:
        session.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=List[ExtractedFieldSchema])
async def get_extractions(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all extractions and evidence for a session."""
    result = await db.execute(
        select(ExtractedField)
        .options(selectinload(ExtractedField.evidence_spans))
        .where(ExtractedField.session_id == session_id)
    )
    return result.scalars().all()
