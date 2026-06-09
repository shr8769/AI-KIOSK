"""
RIAR Pipeline — Main Orchestrator
Owner: Haseeb (Research Lead)

This module implements the RIAR (Retrieval-Informed Ambiguity Resolution) framework.

CONTRACT (to Harsha):
    pipeline = RIARPipeline(vector_store, llm_client)
    result: RIARResult = pipeline.run(query, session_history, language)
    refined: RefinedQuery = pipeline.refine(original_query, clarification, ambiguity_type)

This interface is frozen after Week 2. Any signature changes must be
communicated to Harsha (Engineering Lead) with a 1-sprint deprecation period.
"""

import sys
import os
import time
import logging
from typing import List, Optional, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

from backend.app.models.shared_models import (
    RIARResult, RefinedQuery, ProbeChunk, Turn, AMBIGUITY_TYPES, SUPPORTED_DOMAINS
)

logger = logging.getLogger(__name__)


class RIARPipeline:
    """
    Main RIAR pipeline.

    Steps:
        1. Probe Retrieval      — Get initial context signal (top-10 chunks)
        2. Ambiguity Detection  — Score ambiguity 0.0–1.0
        3. Classification       — CLEAR | SEMANTIC | CONTEXTUAL | CROSS_DOMAIN
        4. Clarification Gen    — Generate targeted clarification question
        5. Query Refinement     — Merge original + clarification
        6. Domain Routing       — Route to domain agent
        7. Grounded Answer      — (Handled by coordinator/domain agent, not RIAR)
    """

    AMBIGUITY_THRESHOLD = 0.4       # Score above this → query is ambiguous
    MAX_PROBE_CHUNKS = 10
    MAX_LATENCY_MS = 2000           # RIAR must complete in 2 seconds

    def __init__(self, vector_store: Any, llm_client: Any):
        """
        Args:
            vector_store: ChromaDB client or compatible vector store
            llm_client: OpenAI client or compatible LLM client
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
        logger.info("RIAR Pipeline initialized")

    def run(
        self,
        query: str,
        session_history: List[Turn],
        language: str = "en"
    ) -> RIARResult:
        """
        Run the full RIAR pipeline on a query.

        Args:
            query: The user's query (in English, or auto-translated)
            session_history: Prior turns in the session (for context)
            language: The user's language ("en" | "kn" | "hi")

        Returns:
            RIARResult — Contains ambiguity type, clarification question (if any),
                         refined query, and domain routing.
        """
        start = time.time()
        logger.info(f"RIAR pipeline started | query='{query}' | language={language}")

        # ── Step 1: Probe Retrieval ────────────────────────────────────────────
        probe_chunks = self._probe_retrieval(query)
        logger.debug(f"Step 1 complete: {len(probe_chunks)} probe chunks retrieved")

        # ── Step 2: Ambiguity Detection ───────────────────────────────────────
        ambiguity_score = self._detect_ambiguity(query, probe_chunks, session_history)
        ambiguity_detected = ambiguity_score > self.AMBIGUITY_THRESHOLD
        logger.debug(f"Step 2 complete: ambiguity_score={ambiguity_score:.3f}, detected={ambiguity_detected}")

        # ── Step 3: Ambiguity Classification ──────────────────────────────────
        ambiguity_type = "CLEAR"
        if ambiguity_detected:
            ambiguity_type = self._classify_ambiguity(query, probe_chunks, session_history)
        logger.debug(f"Step 3 complete: ambiguity_type={ambiguity_type}")

        # ── Step 4: Clarification Generation ──────────────────────────────────
        clarification_question = None
        if ambiguity_type != "CLEAR":
            clarification_question = self._generate_clarification(
                query, ambiguity_type, probe_chunks, language
            )
        logger.debug(f"Step 4 complete: clarification={'yes' if clarification_question else 'no'}")

        # ── Step 5: Domain Routing (for CLEAR queries) ─────────────────────────
        domain = None
        routing_confidence = 0.0
        if ambiguity_type == "CLEAR":
            domain, routing_confidence = self._route_domain(query, probe_chunks)
        logger.debug(f"Step 5 complete: domain={domain}, confidence={routing_confidence:.3f}")

        elapsed_ms = int((time.time() - start) * 1000)
        if elapsed_ms > self.MAX_LATENCY_MS:
            logger.warning(f"RIAR latency exceeded limit: {elapsed_ms}ms > {self.MAX_LATENCY_MS}ms")

        result = RIARResult(
            ambiguity_detected=ambiguity_detected,
            ambiguity_score=ambiguity_score,
            ambiguity_type=ambiguity_type,
            clarification_question=clarification_question,
            refined_query=query,              # Refined after user clarification in refine()
            domain=domain,
            routing_confidence=routing_confidence,
            probe_chunks=probe_chunks
        )

        logger.info(f"RIAR complete in {elapsed_ms}ms | type={ambiguity_type} | domain={domain}")
        return result

    def refine(
        self,
        original_query: str,
        clarification_response: str,
        ambiguity_type: str
    ) -> RefinedQuery:
        """
        Refine the original query using the user's clarification response.
        Called via POST /riar/clarify endpoint.

        Args:
            original_query: The user's original query
            clarification_response: The user's answer to the clarification question
            ambiguity_type: The ambiguity type that was detected

        Returns:
            RefinedQuery with the resolved query and domain routing
        """
        logger.info(f"Refining query | original='{original_query}' | clarification='{clarification_response}'")

        refined_query = self._merge_query_clarification(
            original_query, clarification_response, ambiguity_type
        )
        domain, routing_confidence = self._route_domain(refined_query, [])

        return RefinedQuery(
            refined_query=refined_query,
            domain=domain,
            routing_confidence=routing_confidence,
            ready_for_rag=True
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Private Step Implementations
    # ──────────────────────────────────────────────────────────────────────────

    def _probe_retrieval(self, query: str) -> List[ProbeChunk]:
        """
        Step 1: Broad retrieval to gather context signal.
        Retrieve top-10 chunks without domain filtering.
        """
        # TODO: Implement with real ChromaDB query
        # results = self.vector_store.query(query_texts=[query], n_results=self.MAX_PROBE_CHUNKS)
        # return [ProbeChunk(chunk_id=..., text=..., score=...) for ...]

        # STUB: Returns empty list until real vector store is connected
        logger.debug("_probe_retrieval: STUB — returning empty probe chunks")
        return []

    def _detect_ambiguity(
        self,
        query: str,
        probe_chunks: List[ProbeChunk],
        session_history: List[Turn]
    ) -> float:
        """
        Step 2: Compute ambiguity score.
        Returns a float in [0.0, 1.0]. Higher = more ambiguous.

        Signals that indicate ambiguity:
        - Multiple interpretations of key terms (probe chunks cover multiple domains)
        - Query is short (<5 tokens) with no context
        - Missing subject/referent (pronouns without antecedent)
        - Probe chunk spread is high (low semantic coherence)
        """
        # TODO: Implement real ambiguity scoring
        # Approaches to try (in order of complexity):
        # 1. LLM zero-shot: "Score the ambiguity of this query on a scale 0-1"
        # 2. Probe chunk domain spread: if retrieved chunks span >2 domains → ambiguous
        # 3. Query length heuristic + entity detection
        # 4. Fine-tuned classifier (if time permits)

        # STUB: Always returns CLEAR (0.0) until implemented
        logger.debug("_detect_ambiguity: STUB — returning 0.0")
        return 0.0

    def _classify_ambiguity(
        self,
        query: str,
        probe_chunks: List[ProbeChunk],
        session_history: List[Turn]
    ) -> str:
        """
        Step 3: Classify ambiguity type.
        Returns one of: CLEAR, SEMANTIC, CONTEXTUAL, CROSS_DOMAIN

        SEMANTIC:    Multiple meanings of a word (e.g., "library" = physical or digital)
        CONTEXTUAL:  Missing context (e.g., "my course" — which course?)
        CROSS_DOMAIN: Query spans multiple domains (e.g., "PhD research fee structure")
        """
        # TODO: Implement real ambiguity classification
        # Approach: Use LLM with structured output:
        #   Prompt: "Classify the ambiguity in this query. Output JSON: {type: ..., reason: ...}"

        # STUB
        logger.debug("_classify_ambiguity: STUB — returning CLEAR")
        return "CLEAR"

    def _generate_clarification(
        self,
        query: str,
        ambiguity_type: str,
        probe_chunks: List[ProbeChunk],
        language: str
    ) -> str:
        """
        Step 4: Generate a targeted clarification question.
        The question should be:
        - Specific to the detected ambiguity type
        - Natural and conversational
        - In the user's language
        - Short (1 sentence max)
        """
        # TODO: Implement real clarification generation
        # Approach: LLM prompt with ambiguity type + query + context

        # STUB: Returns a generic clarification
        clarifications = {
            "SEMANTIC": f"Could you clarify what you mean by that? For example, are you asking about [option A] or [option B]?",
            "CONTEXTUAL": f"Could you provide more context? For example, which department or program are you referring to?",
            "CROSS_DOMAIN": f"Your question seems to touch multiple areas. Which is most important to you right now?",
        }
        return clarifications.get(ambiguity_type, "Could you please clarify your question?")

    def _merge_query_clarification(
        self,
        original_query: str,
        clarification_response: str,
        ambiguity_type: str
    ) -> str:
        """
        Step 5: Merge original query + clarification into a refined query.
        """
        # TODO: Implement via LLM:
        # "Given the original query and the user's clarification, write a refined, specific query."
        return f"{original_query} — specifically: {clarification_response}"

    def _route_domain(
        self,
        query: str,
        probe_chunks: List[ProbeChunk]
    ) -> tuple[Optional[str], float]:
        """
        Step 6: Route query to a domain.
        Returns (domain_name, confidence).
        """
        # TODO: Implement domain classification
        # Approach 1: LLM zero-shot classification
        # Approach 2: Use probe chunk domain metadata (majority vote)
        # Approach 3: Fine-tuned classifier

        # STUB: Routes everything to "general"
        return ("general", 0.5)
