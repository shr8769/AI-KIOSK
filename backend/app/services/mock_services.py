"""
Mock implementations of every service.
Swap each class out for real implementations when ready.
All mocks return plausible data so the frontend can integrate immediately.
"""

import base64
import random
from app.models.schemas import (
    DetectResponse, ASRResponse, RIARResponse, RAGResponse,
    RAGSource, TTSResponse, AmbiguityLevel,
)


# ── Detection ─────────────────────────────────

class DetectionService:
    async def detect(self, frame_base64: str | None, source: str) -> DetectResponse:
        detected = random.random() > 0.3
        return DetectResponse(
            person_detected=detected,
            confidence=round(random.uniform(0.7, 0.99), 3) if detected else round(random.uniform(0.1, 0.4), 3),
            bounding_box={"x": 0.2, "y": 0.1, "w": 0.4, "h": 0.6} if detected else None,
        )


# ── ASR ──────────────────────────────────────

class ASRService:
    MOCK_TRANSCRIPTS = [
        "Where is the admissions office?",
        "What are the placement statistics for CSE?",
        "How do I apply for hostel accommodation?",
        "Tell me about research opportunities in AI.",
        "What is the fee structure for MBA?",
    ]

    async def transcribe(self, audio_base64: str, session_id: str, language: str) -> ASRResponse:
        return ASRResponse(
            transcript=random.choice(self.MOCK_TRANSCRIPTS),
            confidence=round(random.uniform(0.82, 0.98), 3),
            language_detected=language,
        )


# ── RIAR ─────────────────────────────────────

class RIARService:
    async def classify(self, session_id: str, transcript: str, language: str) -> RIARResponse:
        # Simple heuristic mock: short queries are ambiguous
        is_ambiguous = len(transcript.split()) < 5
        return RIARResponse(
            ambiguity=AmbiguityLevel.AMBIGUOUS if is_ambiguous else AmbiguityLevel.CLEAR,
            intent="information_query" if not is_ambiguous else None,
            clarification_probe="Could you please clarify what department you're asking about?" if is_ambiguous else None,
            ready_for_rag=not is_ambiguous,
        )


# ── RAG ──────────────────────────────────────

class RAGService:
    MOCK_ANSWERS = {
        "admissions": "The admissions office is located in Block A, Ground Floor. Timings: Mon–Sat 9 AM–5 PM.",
        "placements": "CSE placement rate is 94% with an average package of ₹8.2 LPA (2024 batch).",
        "hostel": "Hostel applications open every May. Visit the Student Services portal to apply.",
        "default": "Thank you for your query. Please visit the relevant department or check the college website for more information.",
    }

    async def retrieve_and_generate(self, session_id: str, query: str, intent: str | None, language: str, top_k: int) -> RAGResponse:
        query_lower = query.lower()
        if "admission" in query_lower:
            answer = self.MOCK_ANSWERS["admissions"]
        elif "placement" in query_lower or "cse" in query_lower:
            answer = self.MOCK_ANSWERS["placements"]
        elif "hostel" in query_lower:
            answer = self.MOCK_ANSWERS["hostel"]
        else:
            answer = self.MOCK_ANSWERS["default"]

        sources = [
            RAGSource(
                doc_id=f"doc_{i}",
                title=f"Mock Source {i}",
                snippet=f"Relevant excerpt {i} from knowledge base...",
                score=round(random.uniform(0.6, 0.95), 3),
            )
            for i in range(1, min(top_k, 3) + 1)
        ]
        return RAGResponse(answer=answer, sources=sources, language=language)


# ── TTS ──────────────────────────────────────

class TTSService:
    async def synthesise(self, session_id: str, text: str, language: str, voice_id: str) -> TTSResponse:
        # Return a tiny silent WAV as placeholder (44-byte minimal valid WAV header)
        silent_wav = bytes([
            0x52,0x49,0x46,0x46,0x24,0x00,0x00,0x00,0x57,0x41,0x56,0x45,
            0x66,0x6D,0x74,0x20,0x10,0x00,0x00,0x00,0x01,0x00,0x01,0x00,
            0x44,0xAC,0x00,0x00,0x88,0x58,0x01,0x00,0x02,0x00,0x10,0x00,
            0x64,0x61,0x74,0x61,0x00,0x00,0x00,0x00,
        ])
        audio_b64 = base64.b64encode(silent_wav).decode()
        words = len(text.split())
        duration = round(words * 0.4, 2)   # rough ~150 wpm estimate
        return TTSResponse(audio_base64=audio_b64, duration_seconds=duration)


# ── Singletons ────────────────────────────────
detection_service = DetectionService()
asr_service = ASRService()
riar_service = RIARService()
rag_service = RAGService()
tts_service = TTSService()
