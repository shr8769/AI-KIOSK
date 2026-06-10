"""
Session Management Route — GET/POST /session
Owner: Harsha
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SessionInfo(BaseModel):
    session_id: str
    status: str = "active"
    duration_seconds: int = 0
    turns_completed: int = 0
    language: str = "en"


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """
    Retrieve session information and history.
    
    TODO Week 2:
    - Query Redis for session data
    - Return session history and metadata
    """
    return SessionInfo(
        session_id=session_id,
        status="active",
        duration_seconds=120,
        turns_completed=3,
        language="en"
    )


@router.post("/session/{session_id}/close")
async def close_session(session_id: str):
    """
    Close a session and archive data.
    
    TODO Week 2:
    - Remove from Redis
    - Save to SQLite
    - Generate session summary
    """
    return {
        "session_id": session_id,
        "action": "session_closed",
        "duration_seconds": 120,
        "turns_completed": 3
    }
