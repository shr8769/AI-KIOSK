"""
Mock implementations of every service mapping to our API contracts.
"""

from app.models.schemas import (
    ASRRequest,
    ASRResponse,
    ClarifyRequest,
    ClarifyResponse,
    DetectRequest,
    DetectResponse,
    RAGRequest,
    RAGResponse,
    RetrievedChunkModel,
    RIARRequest,
    RIARResponse,
    RouteRequest,
    RouteResponse,
    TTSRequest,
    TTSResponse,
)


class DetectionService:
    async def detect(self, session_id: str, request: DetectRequest) -> DetectResponse:
        return DetectResponse(
            session_id=session_id,
            action="session_created",
            greeting_text="Hello! Welcome to PES University. How can I help you today?",
            greeting_audio_url="/static/audio/greeting_en.mp3",
            language_prompt="Please speak in English, Kannada, or Hindi.",
        )


class ASRService:
    async def transcribe(self, request: ASRRequest) -> ASRResponse:
        return ASRResponse(
            session_id=request.session_id,
            turn_id=request.turn_id,
            transcript="Where is the admissions office?",
            detected_language="en",
            confidence=0.95,
            duration_ms=3000,
            latency_ms=480,
        )


class RIARService:
    async def classify(self, request: RIARRequest) -> RIARResponse:
        return RIARResponse(
            session_id=request.session_id,
            ambiguity_detected=False,
            ambiguity_score=0.1,
            ambiguity_type="CLEAR",
            refined_query=request.query,
            domain="admissions",
            routing_confidence=0.9,
            requires_clarification=False,
        )

    async def clarify(self, request: ClarifyRequest) -> ClarifyResponse:
        return ClarifyResponse(
            session_id=request.session_id,
            refined_query=f"{request.original_query} -> {request.clarification_response}",
            domain="admissions",
            routing_confidence=0.9,
            ready_for_rag=True,
        )


class RouteService:
    async def route(self, request: RouteRequest) -> RouteResponse:
        return RouteResponse(
            session_id=request.session_id,
            agent="MockAdmissionsAgent",
            domain=request.domain,
            retrieved_chunks=[
                RetrievedChunkModel(
                    chunk_id="mock_chunk_1",
                    source="mock_source.md",
                    text="Mock admission info",
                    relevance_score=0.9,
                )
            ],
            context_window="Mock admission info context",
            retrieval_latency_ms=100,
        )


class RAGService:
    async def generate(self, request: RAGRequest) -> RAGResponse:
        return RAGResponse(
            session_id=request.session_id,
            answer="This is a mock answer about admissions.",
            citations=["mock_source.md"],
            model_used="mock_model",
            tokens_used=100,
            generation_latency_ms=500,
            confidence_score=0.9,
        )


class TTSService:
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        return TTSResponse(
            session_id=request.session_id,
            audio_url="/static/mock_response.mp3",
            duration_seconds=5.0,
            format="mp3",
            latency_ms=300,
        )


detection_service = DetectionService()
asr_service = ASRService()
riar_service = RIARService()
route_service = RouteService()
rag_service = RAGService()
tts_service = TTSService()
