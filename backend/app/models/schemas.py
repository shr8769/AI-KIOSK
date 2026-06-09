from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ── Shared ────────────────────────────────────

class BaseResponse(BaseModel):
    success: bool = True
    request_id: Optional[str] = None


# ── /detect ───────────────────────────────────

class DetectRequest(BaseModel):
    frame_base64: Optional[str] = Field(None, description="Base64-encoded JPEG frame")
    source: str = Field("camera", description="'camera' | 'upload'")


class DetectResponse(BaseResponse):
    person_detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_box: Optional[Dict[str, float]] = None  # {x, y, w, h} normalised


# ── /asr ─────────────────────────────────────

class ASRRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded WAV/WEBM audio chunk")
    session_id: str
    language: str = "en"


class ASRResponse(BaseResponse):
    transcript: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    language_detected: str


# ── /riar ────────────────────────────────────

class AmbiguityLevel(str, Enum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    OUT_OF_SCOPE = "out_of_scope"


class RIARRequest(BaseModel):
    session_id: str
    transcript: str
    language: str = "en"


class RIARResponse(BaseResponse):
    ambiguity: AmbiguityLevel
    intent: Optional[str] = None
    clarification_probe: Optional[str] = None   # question to ask user
    ready_for_rag: bool


# ── /rag ─────────────────────────────────────

class RAGRequest(BaseModel):
    session_id: str
    query: str
    intent: Optional[str] = None
    language: str = "en"
    top_k: int = Field(5, ge=1, le=20)


class RAGSource(BaseModel):
    doc_id: str
    title: str
    snippet: str
    score: float


class RAGResponse(BaseResponse):
    answer: str
    sources: List[RAGSource] = []
    language: str


# ── /tts ─────────────────────────────────────

class TTSRequest(BaseModel):
    session_id: str
    text: str
    language: str = "en"
    voice_id: str = "default"


class TTSResponse(BaseResponse):
    audio_base64: str          # WAV encoded as base64
    duration_seconds: float
    sample_rate: int = 22050


# ── Session ──────────────────────────────────

class SessionCreateRequest(BaseModel):
    metadata: Dict[str, Any] = {}


class SessionResponse(BaseResponse):
    session_id: str
    created_at: str
    status: str
