from fastapi import APIRouter, HTTPException, Request

from app.core.session_store import close_session, create_session, get_session
from app.models.schemas import (
    ASRRequest,
    ASRResponse,
    DetectRequest,
    DetectResponse,
    RAGRequest,
    RAGResponse,
    RIARRequest,
    RIARResponse,
    SessionCreateRequest,
    SessionResponse,
    TTSRequest,
    TTSResponse,
)
from app.services.mock_services import (
    asr_service,
    detection_service,
    rag_service,
    riar_service,
    tts_service,
)

router = APIRouter()


# ── Health ────────────────────────────────────

@router.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "ai-kiosk-backend"}


# ── Sessions ──────────────────────────────────

@router.post("/session", response_model=SessionResponse, tags=["session"])
async def session_create(body: SessionCreateRequest):
    session = await create_session(metadata=body.metadata)
    return SessionResponse(session_id=session.session_id, created_at=session.created_at, status=session.status)


@router.get("/session/{session_id}", response_model=SessionResponse, tags=["session"])
async def session_get(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session_id=session.session_id, created_at=session.created_at, status=session.status)


@router.delete("/session/{session_id}", tags=["session"])
async def session_close(session_id: str):
    ok = await close_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found or already closed")
    return {"success": True, "session_id": session_id, "status": "closed"}


# ── /detect ───────────────────────────────────

@router.post("/detect", response_model=DetectResponse, tags=["pipeline"])
async def detect(body: DetectRequest, request: Request):
    result = await detection_service.detect(body.frame_base64, body.source)
    result.request_id = getattr(request.state, "request_id", None)
    return result


# ── /asr ─────────────────────────────────────

@router.post("/asr", response_model=ASRResponse, tags=["pipeline"])
async def asr(body: ASRRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await asr_service.transcribe(body.audio_base64, body.session_id, body.language)
    result.request_id = getattr(request.state, "request_id", None)
    return result


# ── /riar ────────────────────────────────────

@router.post("/riar", response_model=RIARResponse, tags=["pipeline"])
async def riar(body: RIARRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await riar_service.classify(body.session_id, body.transcript, body.language)
    result.request_id = getattr(request.state, "request_id", None)
    return result


# ── /rag ─────────────────────────────────────

@router.post("/rag", response_model=RAGResponse, tags=["pipeline"])
async def rag(body: RAGRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await rag_service.retrieve_and_generate(
        body.session_id, body.query, body.intent, body.language, body.top_k
    )
    result.request_id = getattr(request.state, "request_id", None)
    return result


# ── /tts ─────────────────────────────────────

@router.post("/tts", response_model=TTSResponse, tags=["pipeline"])
async def tts(body: TTSRequest, request: Request):
    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await tts_service.synthesise(
        body.session_id, body.text, body.language, body.voice_id
    )
    result.request_id = getattr(request.state, "request_id", None)
    return result
