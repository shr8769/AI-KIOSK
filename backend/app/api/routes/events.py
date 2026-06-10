"""
Event Ingestion Route — POST /api/v1/events
Owner: Harsha (Engineering Lead)
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class EventRequest(BaseModel):
    event_type: str
    camera_id: str
    timestamp: Optional[datetime] = None
    payload: Dict[str, Any] = {}


class EventResponse(BaseModel):
    status: str
    action_taken: str
    session_id: Optional[str] = None
    message: Optional[str] = None


@router.post("/events", response_model=EventResponse)
async def ingest_event(request: EventRequest):
    """
    Unified ingestion endpoint for all edge sensor events.
    The backend remains the Single Source of Truth for session management.
    """
    logger.info(f"Received Event: {request.event_type} | Camera: {request.camera_id}")

    if request.event_type == "PERSON_DETECTED":
        # Check if a session already exists for this camera (pseudo-code)
        # active_session = await redis.get(f"active_camera:{request.camera_id}")
        # if active_session:
        #    logger.info("Session already active, ignoring duplicate PERSON_DETECTED.")
        #    return EventResponse(status="success", action_taken="ignored_duplicate", session_id=active_session)

        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        logger.info(f"Creating new session {session_id} for camera {request.camera_id}")

        # TODO: Save session to Redis via SessionManager
        # TODO: Trigger avatar greeting state change via WebSocket

        return EventResponse(
            status="success",
            action_taken="session_created",
            session_id=session_id,
            message="Welcome to PES University.",
        )

    elif request.event_type == "PERSON_LEFT":
        # Check if session exists (pseudo-code)
        # active_session = await redis.get(f"active_camera:{request.camera_id}")
        # if not active_session:
        #    return EventResponse(status="success", action_taken="ignored_no_session")

        logger.info(f"Closing session for camera {request.camera_id}")
        # TODO: Retrieve session, compute duration, close in Redis + write to SQLite

        return EventResponse(status="success", action_taken="session_closed", session_id="dummy_id")

    elif request.event_type == "HEARTBEAT":
        logger.debug(f"Heartbeat from {request.camera_id}: {request.payload}")
        return EventResponse(status="success", action_taken="heartbeat_logged")

    else:
        logger.warning(f"Unknown event type: {request.event_type}")
        raise HTTPException(status_code=400, detail="Unknown event type")
