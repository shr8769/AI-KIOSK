"""
Route Classification Route — POST /route
Owner: Harsha
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class RouteRequest(BaseModel):
    session_id: str
    refined_query: str
    domain: str = "admissions"
    language: str = "en"
    top_k: int = 5


class RouteResponse(BaseModel):
    session_id: str
    domain: str
    confidence: float
    context_window: Optional[str] = None
    top_k_results: List[dict] = []


@router.post("/route", response_model=RouteResponse)
async def route_to_domain(request: RouteRequest):
    """
    Route query to appropriate domain (admissions, placements, academics, etc).
    
    TODO Week 2:
    - Use domain classifier model
    - Return top-k matching documents
    - Generate context window for RAG
    """
    return RouteResponse(
        session_id=request.session_id,
        domain=request.domain,
        confidence=0.92,
        context_window="[MOCK] B.Tech admissions requirement documents",
        top_k_results=[]
    )
