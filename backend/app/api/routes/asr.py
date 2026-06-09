"""Stub route files for ASR, RAG, TTS, Route, and Session endpoints."""

# asr.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/asr")
async def transcribe_audio():
    """
    Transcribe audio to text using Whisper.
    Owner: Harsha
    
    TODO Week 2:
    - Accept multipart/form-data with audio_file
    - Run Whisper ASR (real or mock based on USE_REAL_ASR)
    - Detect language
    - Return ASRResult
    """
    return {
        "session_id": "ses_stub",
        "turn_id": 1,
        "transcript": "[STUB] How do I apply for B.Tech admission?",
        "transcript_en": "[STUB] How do I apply for B.Tech admission?",
        "detected_language": "en",
        "confidence": 0.95,
        "duration_ms": 3000,
        "latency_ms": 480
    }
