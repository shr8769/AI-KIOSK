from fastapi import APIRouter, HTTPException, Request

from app.core.session_store import get_session
from app.models.schemas import (
    ASRRequest,
    ASRResponse,
    ClarifyRequest,
    ClarifyResponse,
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


@router.get(
    "/session/{session_id}/history", response_model=SessionHistoryResponse, tags=["session"]
)
async def session_history(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionHistoryResponse(
        session_id=session_id, turns=[], total_turns=0, session_duration_seconds=0
    )
