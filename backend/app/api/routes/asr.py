"""
ASR Route — POST /asr
Owner: Harsha
"""

import logging

from fastapi import APIRouter

from app.models.schemas import ASRRequest, ASRResponse
from app.services.speech.asr_service import asr_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/asr", response_model=ASRResponse)
async def transcribe_audio(request: ASRRequest):
    """
    Transcribe audio to text using Whisper.
    """
    return await asr_service.transcribe(request)
