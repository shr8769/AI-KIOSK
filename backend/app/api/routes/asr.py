"""
ASR Route — POST /asr
Owner: Harsha
"""

from fastapi import APIRouter
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ASRRequest(BaseModel):
    session_id: str
    audio_base64: str
    language_hint: str = "en"
    turn_id: int


class ASRResponse(BaseModel):
    session_id: str
    turn_id: int
    transcript: str
    transcript_en: str
    detected_language: str = "en"
    confidence: float = 0.95
    duration_ms: int
    latency_ms: int


@router.post("/asr", response_model=ASRResponse)
async def transcribe_audio(request: ASRRequest):
    """
    Transcribe audio to text using Whisper.
    
    TODO Week 2:
    - Accept multipart/form-data with audio_file
    - Run Whisper ASR (real or mock based on USE_REAL_ASR)
    - Detect language
    - Return ASRResult
    """
    return ASRResponse(
        session_id=request.session_id,
        turn_id=request.turn_id,
        transcript="[MOCK] How do I apply for B.Tech admission?",
        transcript_en="[MOCK] How do I apply for B.Tech admission?",
        detected_language="en",
        confidence=0.95,
        duration_ms=3000,
        latency_ms=480
    )
