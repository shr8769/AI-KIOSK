"""
RIAR Route — POST /riar (Refined Intent and Refinement)
Owner: Harsha
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class RIARRequest(BaseModel):
    session_id: str
    turn_id: int
    query: str
    language: str = "en"
    session_history: List[dict] = []


class RIARResponse(BaseModel):
    session_id: str
    turn_id: int
    refined_query: str
    intent: str
    confidence: float = 0.9


@router.post("/riar", response_model=RIARResponse)
async def refine_intent_and_context(request: RIARRequest):
    """
    Refine user intent and add context awareness.
    
    TODO Week 2:
    - Use real RIAR model or LLM-based refinement
    - Process session_history for context
    - Extract intent and entities
    """
    return RIARResponse(
        session_id=request.session_id,
        turn_id=request.turn_id,
        refined_query="[MOCK REFINED] admissions for B.Tech",
        intent="admissions_inquiry",
        confidence=0.9
    )
