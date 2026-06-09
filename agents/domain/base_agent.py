from abc import ABC, abstractmethod
from typing import List
import sys
import os

# Allow imports from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from backend.app.models.shared_models import DomainResponse, Chunk, SUPPORTED_DOMAINS


class BaseDomainAgent(ABC):
    """
    Abstract base class for all domain agents.

    CONTRACT (Gowtham):
    - All domain agents must implement `retrieve()` and `generate()`
    - `retrieve()` must return within 1 second
    - `generate()` must return within 2 seconds
    - This interface is frozen after Week 2
    - Any changes must be approved by Harsha (Engineering Lead)

    USAGE (Harsha):
        agent = AdmissionsAgent()
        chunks = agent.retrieve("PESSAT eligibility", top_k=5)
        response = agent.generate("PESSAT eligibility", chunks, language="en")
    """

    domain: str = "base"  # Override in subclass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        """
        Retrieve top_k relevant knowledge chunks for the query.

        Args:
            query: The (refined) user query in English
            top_k: Number of chunks to retrieve (default: 5)

        Returns:
            List of Chunk objects, ordered by relevance (highest first)

        Raises:
            RuntimeError: If vector store is unavailable
        """
        ...

    @abstractmethod
    def generate(
        self,
        query: str,
        context: List[Chunk],
        language: str = "en"
    ) -> DomainResponse:
        """
        Generate a grounded answer based on retrieved context.

        Args:
            query: The (refined) user query
            context: List of retrieved chunks to ground the answer
            language: Output language ("en" | "kn" | "hi")

        Returns:
            DomainResponse with answer, citations, and confidence

        Raises:
            RuntimeError: If LLM is unavailable
        """
        ...

    def answer(
        self,
        query: str,
        language: str = "en",
        top_k: int = 5
    ) -> DomainResponse:
        """
        Convenience method: retrieve then generate in one call.
        Harsha's coordinator uses this for simple routing.
        """
        chunks = self.retrieve(query, top_k=top_k)
        return self.generate(query, chunks, language=language)
