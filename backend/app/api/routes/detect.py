"""
Detection Route — POST /detect & DELETE /detect/{session_id}
Owner: Harsha (Engineering Lead) — endpoint
       Haseeb (Project Lead) — fires events from detection module
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class DetectRequest(BaseModel):
    camera_id: str = "cam_front_01"
    confidence: float
    bounding_box: dict
    detected_at: Optional[datetime] = None
    frame_width: int = 1920
    frame_height: int = 1080


class DetectResponse(BaseModel):
    session_id: str
    action: str
    greeting_text: str
    greeting_audio_url: str
    language_prompt: str


@router.post("/detect", response_model=DetectResponse)
async def create_session_on_detection(request: DetectRequest):
    """
    Called by Haseeb's detection module when a person is detected.
    Creates a new session and returns greeting payload.
    """
    logger.info(f"Person detected | camera={request.camera_id} | confidence={request.confidence:.2f}")

    session_id = f"ses_{uuid.uuid4().hex[:12]}"

    # TODO: Save session to Redis via SessionManager
    # TODO: Trigger avatar greeting state change via WebSocket

    return DetectResponse(
        session_id=session_id,
        action="session_created",
        greeting_text="Hello! Welcome to PES University. How can I help you today?",
        greeting_audio_url="/static/audio/greeting_en.mp3",
        language_prompt="Please speak in English, Kannada, or Hindi."
    )


@router.delete("/detect/{session_id}")
async def close_session_on_exit(session_id: str):
    """
    Called when person leaves the frame. Closes the session.
    """
    logger.info(f"Person left | session={session_id}")

    # TODO: Retrieve session, compute duration, close in Redis + write to SQLite

    return {
        "session_id": session_id,
        "action": "session_closed",
        "duration_seconds": 0,  # TODO: real duration
        "turns_completed": 0    # TODO: real count
    }
