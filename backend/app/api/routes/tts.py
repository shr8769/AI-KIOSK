"""
TTS Route — POST /tts (Text-To-Speech)
Owner: Harsha
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


from app.models.schemas import TTSRequest, TTSResponse
from app.services.speech.tts_service import tts_service


@router.post("/tts", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech using TTS engine.
    """
    return await tts_service.synthesize(request)
