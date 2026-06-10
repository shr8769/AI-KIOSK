from fastapi import APIRouter
router = APIRouter()

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve session object.
    Owner: Harsha
    TODO: Implement Redis lookup.
    """
    return {
        "session_id": session_id,
        "status": "active",
        "turns": [],
        "message": "STUB: implement Redis session lookup"
    }


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get turn history for a session.
    Owner: Harsha
    """
    return {
        "session_id": session_id,
        "turns": [],
        "total_turns": 0,
        "session_duration_seconds": 0
    }
