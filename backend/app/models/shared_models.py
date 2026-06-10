import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Detection Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int


@dataclass
class DetectionEvent:
    camera_id: str
    confidence: float
    bounding_box: BoundingBox
    detected_at: datetime = field(default_factory=datetime.utcnow)
    frame_width: int = 1920
    frame_height: int = 1080

    def to_dict(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "confidence": self.confidence,
            "bounding_box": {
                "x": self.bounding_box.x,
                "y": self.bounding_box.y,
                "w": self.bounding_box.w,
                "h": self.bounding_box.h,
            },
            "detected_at": self.detected_at.isoformat(),
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Speech Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ASRResult:
    session_id: str
    turn_id: int
    transcript: str
    transcript_en: Optional[str]   # English translation if original was KN/HI
    detected_language: str         # "en" | "kn" | "hi"
    confidence: float
    duration_ms: int
    latency_ms: int


@dataclass
class TTSResult:
    session_id: str
    audio_url: str
    duration_seconds: float
    format: str                    # "mp3" | "wav"
    latency_ms: int


# ─────────────────────────────────────────────────────────────────────────────
# RIAR Models
# ─────────────────────────────────────────────────────────────────────────────

AMBIGUITY_TYPES = ["CLEAR", "SEMANTIC", "CONTEXTUAL", "CROSS_DOMAIN"]
SUPPORTED_LANGUAGES = ["en", "kn", "hi"]
SUPPORTED_DOMAINS = [
    "admissions", "academics", "placements",
    "research", "student_services", "navigation", "general"
]


@dataclass
class ProbeChunk:
    chunk_id: str
    text: str
    score: float
    source: Optional[str] = None


@dataclass
class RIARResult:
    """Output of the RIAR pipeline. This is the contract Haseeb must maintain."""
    ambiguity_detected: bool
    ambiguity_score: float                    # 0.0 to 1.0
    ambiguity_type: str                       # From AMBIGUITY_TYPES
    clarification_question: Optional[str]
    refined_query: str
    domain: Optional[str]                     # From SUPPORTED_DOMAINS
    routing_confidence: float
    probe_chunks: List[ProbeChunk] = field(default_factory=list)

    def __post_init__(self):
        assert self.ambiguity_type in AMBIGUITY_TYPES, \
            f"Invalid ambiguity type: {self.ambiguity_type}"
        assert 0.0 <= self.ambiguity_score <= 1.0, \
            f"Ambiguity score must be in [0, 1]: {self.ambiguity_score}"
        if self.domain:
            assert self.domain in SUPPORTED_DOMAINS, \
                f"Invalid domain: {self.domain}"


@dataclass
class RefinedQuery:
    """Output of RIAR refinement step. Produced after user provides clarification."""
    refined_query: str
    domain: str
    routing_confidence: float
    ready_for_rag: bool

    def __post_init__(self):
        assert self.domain in SUPPORTED_DOMAINS, f"Invalid domain: {self.domain}"


# ─────────────────────────────────────────────────────────────────────────────
# Agent Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    """A retrieved knowledge chunk. This is the contract Gowtham must maintain."""
    chunk_id: str
    source: str
    text: str
    relevance_score: float
    page: Optional[int] = None
    domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainResponse:
    """Output of a domain agent. This is the contract Gowtham must maintain."""
    answer: str
    citations: List[str]
    confidence: float
    domain: str
    retrieved_chunks: List[Chunk] = field(default_factory=list)
    answer_language: str = "en"
    generation_model: Optional[str] = None
    tokens_used: int = 0

    def __post_init__(self):
        assert self.domain in SUPPORTED_DOMAINS, f"Invalid domain: {self.domain}"
        assert 0.0 <= self.confidence <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Session Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Turn:
    turn_id: int
    role: str                     # "user" | "assistant"
    text: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    raw_audio_path: Optional[str] = None
    language: Optional[str] = None


@dataclass
class SessionMetrics:
    asr_latency_ms: int = 0
    riar_latency_ms: int = 0
    rag_latency_ms: int = 0
    tts_latency_ms: int = 0
    total_latency_ms: int = 0


@dataclass
class SessionObject:
    """
    The canonical session object that flows through the entire pipeline.
    All modules read from and write to this object via the Session Manager.
    """
    session_id: str = field(default_factory=lambda: f"ses_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"                    # "active" | "closed" | "error"

    # Detection context
    person_detection: Optional[DetectionEvent] = None

    # Language
    detected_language: str = "en"
    preferred_language: str = "en"

    # Conversation history
    turns: List[Turn] = field(default_factory=list)

    # RIAR state (last turn)
    riar_result: Optional[RIARResult] = None
    rag_response: Optional[DomainResponse] = None

    # Avatar state
    avatar_state: str = "idle"                # "idle" | "greeting" | "listening" | "processing" | "speaking"

    # Performance metrics
    metrics: SessionMetrics = field(default_factory=SessionMetrics)

    def add_turn(self, role: str, text: str, **kwargs) -> Turn:
        turn = Turn(
            turn_id=len(self.turns) + 1,
            role=role,
            text=text,
            **kwargs
        )
        self.turns.append(turn)
        self.updated_at = datetime.utcnow()
        return turn

    def get_history_text(self, max_turns: int = 5) -> str:
        """Returns last N turns as a formatted string for LLM context."""
        recent = self.turns[-max_turns:]
        return "\n".join([f"{t.role.upper()}: {t.text}" for t in recent])

    def to_dict(self) -> dict:
        """Serialize for storage in Redis/SQLite."""
        import dataclasses
        return dataclasses.asdict(self)
