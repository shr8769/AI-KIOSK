"""
RIAR Route — POST /riar & POST /riar/clarify
Owner: Harsha (Engineering Lead) — endpoint
       Haseeb (Project Lead) — pipeline logic
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../"))

from backend.app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class TurnModel(BaseModel):
    turn_id: int
    role: str
    text: str


class RIARRequest(BaseModel):
    session_id: str
    turn_id: int
    query: str
    language: str = "en"
    session_history: List[TurnModel] = []


class ClarifyRequest(BaseModel):
    session_id: str
    turn_id: int
    clarification_response: str
    original_query: str
    ambiguity_type: str


@router.post("/riar")
async def run_riar(request: RIARRequest):
    """
    Run RIAR pipeline on a transcript.
    Haseeb's pipeline is imported and called here.
    """
    logger.info(f"RIAR request | session={request.session_id} | query='{request.query}'")

    if settings.USE_REAL_RIAR:
        # Use Haseeb's real RIAR pipeline
        from riar.pipeline import RIARPipeline
        # pipeline = RIARPipeline(vector_store=..., llm_client=...)
        # result = pipeline.run(request.query, request.session_history, request.language)
        # TODO: Wire up real vector_store and llm_client via dependency injection
        raise NotImplementedError("Real RIAR not wired up yet — set USE_REAL_RIAR=false")
    else:
        from tests.mocks.mock_modules import MockRIARPipeline
        pipeline = MockRIARPipeline()
        from backend.app.models.shared_models import Turn
        history = [Turn(turn_id=t.turn_id, role=t.role, text=t.text) for t in request.session_history]
        result = pipeline.run(request.query, history, request.language)

    return {
        "session_id": request.session_id,
        "ambiguity_detected": result.ambiguity_detected,
        "ambiguity_score": result.ambiguity_score,
        "ambiguity_type": result.ambiguity_type,
        "clarification_question": result.clarification_question,
        "refined_query": result.refined_query,
        "domain": result.domain,
        "routing_confidence": result.routing_confidence,
        "requires_clarification": result.ambiguity_detected,
    }


@router.post("/riar/clarify")
async def submit_clarification(request: ClarifyRequest):
    """
    Accept user's clarification response and return refined query.
    """
    logger.info(f"Clarification received | session={request.session_id}")

    if settings.USE_REAL_RIAR:
        from riar.pipeline import RIARPipeline
        raise NotImplementedError("Real RIAR not wired up yet")
    else:
        from tests.mocks.mock_modules import MockRIARPipeline
        pipeline = MockRIARPipeline()
        result = pipeline.refine(
            request.original_query,
            request.clarification_response,
            request.ambiguity_type
        )

    return {
        "session_id": request.session_id,
        "refined_query": result.refined_query,
        "domain": result.domain,
        "routing_confidence": result.routing_confidence,
        "ready_for_rag": result.ready_for_rag
    }
