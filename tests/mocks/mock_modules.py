"""
Mock modules for development.
These allow Harsha to build and test the backend without waiting for
Haseeb's detection/RIAR or Gowtham's agents to be ready.

Usage in backend (controlled by .env flags):
    USE_REAL_DETECTOR=false  → MockPersonDetector is used
    USE_REAL_RIAR=false      → MockRIARPipeline is used
    USE_REAL_AGENTS=false    → Mock*Agent is used
"""

import time
import threading
import logging
from typing import List, Optional, Callable

# Add repo root to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from backend.app.models.shared_models import (
    DetectionEvent, BoundingBox, RIARResult, RefinedQuery,
    DomainResponse, Chunk, Turn
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Mock Person Detector
# ─────────────────────────────────────────────────────────────────────────────

class MockPersonDetector:
    """
    Simulates person detection. Triggers after 2 seconds.
    Used by Harsha and Gowtham during development (before Haseeb's module is ready).
    """

    def __init__(self, auto_trigger_seconds: float = 2.0):
        self.auto_trigger_seconds = auto_trigger_seconds
        self._on_detected_callback: Optional[Callable] = None
        self._on_left_callback: Optional[Callable] = None
        self._running = False

    def start_monitoring(self) -> None:
        """Start mock detection loop."""
        self._running = True
        logger.info("MockPersonDetector: starting (will trigger in %.1fs)", self.auto_trigger_seconds)
        threading.Thread(target=self._mock_loop, daemon=True).start()

    def stop_monitoring(self) -> None:
        self._running = False

    def on_person_detected(self, callback: Callable[[DetectionEvent], None]) -> None:
        self._on_detected_callback = callback

    def on_person_left(self, callback: Callable[[DetectionEvent], None]) -> None:
        self._on_left_callback = callback

    def _mock_loop(self):
        time.sleep(self.auto_trigger_seconds)
        if self._on_detected_callback and self._running:
            event = DetectionEvent(
                camera_id="cam_mock_01",
                confidence=0.95,
                bounding_box=BoundingBox(x=120, y=80, w=200, h=400)
            )
            logger.info("MockPersonDetector: PERSON_DETECTED event fired")
            self._on_detected_callback(event)

        time.sleep(30)  # Person stays for 30 seconds

        if self._on_left_callback and self._running:
            event = DetectionEvent(
                camera_id="cam_mock_01",
                confidence=0.0,
                bounding_box=BoundingBox(x=0, y=0, w=0, h=0)
            )
            logger.info("MockPersonDetector: PERSON_LEFT event fired")
            self._on_left_callback(event)


# ─────────────────────────────────────────────────────────────────────────────
# Mock RIAR Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class MockRIARPipeline:
    """
    Returns CLEAR ambiguity type for all queries.
    Used while Haseeb builds the real RIAR module.
    """

    def run(
        self,
        query: str,
        session_history: List[Turn],
        language: str = "en"
    ) -> RIARResult:
        logger.debug(f"MockRIARPipeline.run() called with query='{query}'")
        time.sleep(0.05)  # Simulate slight latency
        return RIARResult(
            ambiguity_detected=False,
            ambiguity_score=0.1,
            ambiguity_type="CLEAR",
            clarification_question=None,
            refined_query=query,
            domain="admissions",  # Default routing
            routing_confidence=0.8,
            probe_chunks=[]
        )

    def refine(
        self,
        original_query: str,
        clarification_response: str,
        ambiguity_type: str
    ) -> RefinedQuery:
        logger.debug("MockRIARPipeline.refine() called")
        return RefinedQuery(
            refined_query=f"{original_query} — specifically: {clarification_response}",
            domain="admissions",
            routing_confidence=0.85,
            ready_for_rag=True
        )


class MockAmbiguousRIARPipeline:
    """
    Always returns CONTEXTUAL ambiguity. Useful for testing clarification flow.
    """

    def run(self, query: str, session_history: List[Turn], language: str = "en") -> RIARResult:
        logger.debug("MockAmbiguousRIARPipeline.run(): returning CONTEXTUAL ambiguity")
        return RIARResult(
            ambiguity_detected=True,
            ambiguity_score=0.75,
            ambiguity_type="CONTEXTUAL",
            clarification_question="Are you asking about B.Tech or M.Tech admissions?",
            refined_query=query,
            domain=None,
            routing_confidence=0.0,
            probe_chunks=[]
        )


# ─────────────────────────────────────────────────────────────────────────────
# Mock Domain Agents
# ─────────────────────────────────────────────────────────────────────────────

class MockAdmissionsAgent:
    """Returns canned admissions response. Used while Gowtham builds real agent."""
    domain = "admissions"

    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        return [
            Chunk(
                chunk_id="mock_adm_001",
                source="mock/admissions.md",
                text="MOCK: PES University B.Tech admissions are via PESSAT exam...",
                relevance_score=0.75,
                domain="admissions"
            )
        ]

    def generate(self, query: str, context: List[Chunk], language: str = "en") -> DomainResponse:
        logger.debug(f"MockAdmissionsAgent.generate() called | language={language}")
        time.sleep(0.1)
        return DomainResponse(
            answer="[MOCK] PES University B.Tech admissions require PESSAT qualification. Apply at pessat.pes.edu.",
            citations=["mock/admissions.md"],
            confidence=0.5,
            domain="admissions",
            retrieved_chunks=context,
            answer_language=language
        )

    def answer(self, query: str, language: str = "en", top_k: int = 5) -> DomainResponse:
        chunks = self.retrieve(query, top_k)
        return self.generate(query, chunks, language)


class MockNavigationAgent:
    """Returns canned navigation response."""
    domain = "navigation"

    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        return [Chunk(
            chunk_id="mock_nav_001",
            source="mock/campus_map.md",
            text="MOCK: The Admin block is located at the main gate entrance.",
            relevance_score=0.8,
            domain="navigation"
        )]

    def generate(self, query: str, context: List[Chunk], language: str = "en") -> DomainResponse:
        return DomainResponse(
            answer="[MOCK] The Admin Block is on the ground floor, main building, near the main gate.",
            citations=["mock/campus_map.md"],
            confidence=0.6,
            domain="navigation",
            retrieved_chunks=context,
            answer_language=language
        )

    def answer(self, query: str, language: str = "en", top_k: int = 5) -> DomainResponse:
        chunks = self.retrieve(query, top_k)
        return self.generate(query, chunks, language)


# Registry of all mock agents
MOCK_AGENT_REGISTRY = {
    "admissions": MockAdmissionsAgent,
    "academics": MockAdmissionsAgent,      # Reuse for now
    "placements": MockAdmissionsAgent,
    "research": MockAdmissionsAgent,
    "student_services": MockAdmissionsAgent,
    "navigation": MockNavigationAgent,
    "general": MockAdmissionsAgent,
}


def get_mock_agent(domain: str):
    """Get the appropriate mock agent for a domain."""
    agent_class = MOCK_AGENT_REGISTRY.get(domain, MockAdmissionsAgent)
    return agent_class()
