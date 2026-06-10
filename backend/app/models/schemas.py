from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.shared_models import Turn

# ── /detect ───────────────────────────────────

class BoundingBoxModel(BaseModel):
    x: int
    y: int
    w: int
    h: int

class DetectRequest(BaseModel):
    camera_id: str = "cam_front_01"
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_box: BoundingBoxModel
    detected_at: Optional[datetime] = None
    frame_width: int = 1920
    frame_height: int = 1080

class DetectResponse(BaseModel):
    session_id: str
    action: str
    greeting_text: str
    greeting_audio_url: str
    language_prompt: str

# ── /asr ─────────────────────────────────────

class ASRRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded WAV/WEBM audio chunk")
    session_id: str
    language_hint: Optional[str] = "en"
    turn_id: int

class ASRResponse(BaseModel):
    session_id: str
    turn_id: int
    transcript: str
    transcript_en: Optional[str] = None
    detected_language: str
    confidence: float
    duration_ms: int
    latency_ms: int

# ── /riar ────────────────────────────────────

class TurnModel(BaseModel):
    turn_id: int
    role: str
    text: str

class RIARRequest(BaseModel):
    session_id: str
    turn_id: int
    query: str
    language: str = "en"
    session_history: List[TurnModel] = []

class ProbeChunkModel(BaseModel):
    chunk_id: str
    text: str
    score: float

class RIARResponse(BaseModel):
    session_id: str
    ambiguity_detected: bool
    ambiguity_score: float
    ambiguity_type: str
    refined_query: Optional[str] = None
    domain: Optional[str] = None
    routing_confidence: float
    requires_clarification: bool
    clarification_question: Optional[str] = None
    clarification_audio_url: Optional[str] = None
    probe_chunks: Optional[List[ProbeChunkModel]] = None

class ClarifyRequest(BaseModel):
    session_id: str
    turn_id: int
    clarification_response: str
    original_query: str
    ambiguity_type: str

class ClarifyResponse(BaseModel):
    session_id: str
    refined_query: str
    domain: str
    routing_confidence: float
    ready_for_rag: bool

# ── /route ───────────────────────────────────

class RouteRequest(BaseModel):
    session_id: str
    refined_query: str
    domain: str
    language: str = "en"
    top_k: int = 5

class RetrievedChunkModel(BaseModel):
    chunk_id: str
    source: str
    page: Optional[int] = None
    text: str
    relevance_score: float

class RouteResponse(BaseModel):
    session_id: str
    agent: str
    domain: str
    retrieved_chunks: List[RetrievedChunkModel]
    context_window: str
    retrieval_latency_ms: int

# ── /rag ─────────────────────────────────────

class RAGRequest(BaseModel):
    session_id: str
    query: str
    context: str
    domain: str
    language: str = "en"
    max_tokens: int = 500
    citations_required: bool = True

class RAGResponse(BaseModel):
    session_id: str
    answer: str
    answer_en: Optional[str] = None
    citations: List[str]
    model_used: str
    tokens_used: int
    generation_latency_ms: int
    confidence_score: float

# ── /tts ─────────────────────────────────────

class TTSRequest(BaseModel):
    session_id: str
    text: str
    language: str = "en"
    voice_id: str = "default"
    speed: float = 1.0
    format: str = "mp3"

class TTSResponse(BaseModel):
    session_id: str
    audio_url: str
    duration_seconds: float
    format: str
    latency_ms: int

# ── Session ──────────────────────────────────

class SessionHistoryResponse(BaseModel):
    session_id: str
    turns: List[Any]
    total_turns: int
    session_duration_seconds: int
