from fastapi import APIRouter

router = APIRouter()

@router.post("/route")
async def route_query():
    """
    Route refined query to appropriate domain agent.
    Owner: Harsha (coordinator dispatch)

    TODO Week 3:
    - Accept session_id, refined_query, domain
    - Call appropriate domain agent (real or mock based on USE_REAL_AGENTS)
    - Return retrieved chunks
    """
    return {
        "session_id": "ses_stub",
        "agent": "MockAdmissionsAgent",
        "domain": "admissions",
        "retrieved_chunks": [
            {
                "chunk_id": "stub_001",
                "source": "mock/admissions.md",
                "page": 1,
                "text": "[STUB] PES University B.Tech admissions via PESSAT...",
                "relevance_score": 0.85
            }
        ],
        "context_window": "[STUB] PES University B.Tech admissions...",
        "retrieval_latency_ms": 50
    }
