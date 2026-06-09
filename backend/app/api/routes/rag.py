from fastapi import APIRouter
router = APIRouter()

@router.post("/rag")
async def generate_answer():
    """
    Generate grounded answer from retrieved context.
    Owner: Harsha (endpoint), Gowtham (domain agent logic)
    
    TODO Week 3:
    - Accept session_id, query, context, domain, language
    - Call LLM with context to generate grounded answer
    - Return answer with citations
    """
    return {
        "session_id": "ses_stub",
        "answer": "[STUB] PES University B.Tech admissions are conducted via PESSAT. Please visit pessat.pes.edu to apply.",
        "answer_en": "[STUB] PES University B.Tech admissions are conducted via PESSAT.",
        "citations": ["mock/admissions.md:p1"],
        "model_used": "mock",
        "tokens_used": 0,
        "generation_latency_ms": 100,
        "confidence_score": 0.5
    }
