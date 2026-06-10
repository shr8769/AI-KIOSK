from fastapi import APIRouter, HTTPException, Request

from app.core.session_store import close_session, create_session, get_session
from app.models.schemas import (
    ASRRequest,
    ASRResponse,
    ClarifyRequest,
    ClarifyResponse,
    ClarifyResponse,
    RAGRequest,
    RAGResponse,
    RAGRequest,
    RAGResponse,
    RIARRequest,
    RIARResponse,
    RouteRequest,
    RouteResponse,
    SessionHistoryResponse,
    TTSRequest,
    TTSResponse,
)
from app.services.mock_services import (
    asr_service,
    detection_service,
    rag_service,
    riar_service,
    route_service,
    tts_service,
)

router = APIRouter()


# ── Health ────────────────────────────────────

@router.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "ai-kiosk-backend"}


# ── /events ───────────────────────────────────

from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models.shared_models import KioskEvent

class EventRequest(BaseModel):
    event_type: str
    camera_id: str
    timestamp: Optional[str] = None
    payload: Dict[str, Any] = {}

class EventResponse(BaseModel):
    status: str
    action_taken: str
    session_id: Optional[str] = None
    message: Optional[str] = None

@router.post("/events", response_model=EventResponse, tags=["pipeline"])
async def handle_events(body: EventRequest, request: Request):
    """
    Unified ingestion endpoint for all edge sensor events.
    """
    import logging
    import uuid
    logger = logging.getLogger(__name__)
    
    logger.info(f"Received Event: {body.event_type} | Camera: {body.camera_id}")

    if body.event_type == "PERSON_DETECTED":
        # Check if session exists (simplified logic for now)
        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        await create_session(metadata={"camera_id": body.camera_id})
        
        return EventResponse(
            status="success",
            action_taken="session_created",
            session_id=session_id,
            message="Welcome to PES University."
        )

    elif body.event_type == "PERSON_LEFT":
        logger.info(f"Closing session for camera {body.camera_id}")
        return EventResponse(
            status="success",
            action_taken="session_closed",
            session_id="dummy_id"
        )

    elif body.event_type == "HEARTBEAT":
        return EventResponse(status="success", action_taken="heartbeat_logged")

    else:
        raise HTTPException(status_code=400, detail="Unknown event type")


# ── /asr ─────────────────────────────────────

@router.post("/asr", response_model=ASRResponse, tags=["pipeline"])
async def asr(body: ASRRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await asr_service.transcribe(body)
    return result


# ── /riar ────────────────────────────────────

@router.post("/riar", response_model=RIARResponse, tags=["pipeline"])
async def riar(body: RIARRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await riar_service.classify(body)
    return result

@router.post("/riar/clarify", response_model=ClarifyResponse, tags=["pipeline"])
async def riar_clarify(body: ClarifyRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await riar_service.clarify(body)
    return result


# ── /route ───────────────────────────────────

@router.post("/route", response_model=RouteResponse, tags=["pipeline"])
async def route_query(body: RouteRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await route_service.route(body)
    return result


# ── /rag ─────────────────────────────────────

@router.post("/rag", response_model=RAGResponse, tags=["pipeline"])
async def rag(body: RAGRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await rag_service.generate(body)
    return result


# ── /tts ─────────────────────────────────────

@router.post("/tts", response_model=TTSResponse, tags=["pipeline"])
async def tts(body: TTSRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await tts_service.synthesize(body)
    return result


# ── /session ─────────────────────────────────

@router.get("/session/{session_id}/history", response_model=SessionHistoryResponse, tags=["session"])
async def session_history(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionHistoryResponse(
        session_id=session_id,
        turns=[],
        total_turns=0,
        session_duration_seconds=0
    )
