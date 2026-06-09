# INTEGRATION_STRATEGY.md
## VidyaSahayak — Integration Strategy
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Harsha (Engineering Lead)

> This is the most operationally critical document in the project.
> Read this before you write a single line of code that touches another person's module.

---

## 1. Core Integration Philosophy

### Three Rules

1. **Own your interface, not your dependency.** Each module exposes a clean API. You own what you publish. You mock what you consume.
2. **Never break `develop`.** If your code merges on Friday and breaks `develop`, fix it within 2 hours or revert.
3. **Agree on contracts before coding, not after.** The `API_CONTRACT.md` is the constitution. Propose changes in writing before implementing.

---

## 2. Module Boundaries

```
┌─────────────────────────────────────────────────────────┐
│  Module Boundary Rules                                  │
│                                                         │
│  Haseeb's modules communicate via:                      │
│    → POST /detect        (to Harsha's backend)          │
│    → RIAR Python classes (called by Harsha's backend)   │
│    → Avatar state events (via WebSocket)                │
│                                                         │
│  Gowtham's modules communicate via:                     │
│    → Python agent classes (called by Harsha's backend)  │
│    → ChromaDB reads (shared volume)                     │
│    → Evaluation scripts (offline, no live dependency)   │
│                                                         │
│  Harsha's backend is the INTEGRATION LAYER:             │
│    → Calls into Haseeb's RIAR pipeline                  │
│    → Calls into Gowtham's domain agents                 │
│    → Exposes all APIs to frontend and detection         │
└─────────────────────────────────────────────────────────┘
```

**Key principle:** Haseeb and Gowtham's code is **imported as Python modules** by Harsha's backend — they are not separate services (in development). This keeps latency low and deployment simple.

---

## 3. How to Work Independently Without Breaking Each Other

### 3.1 The Mock-First Rule

Before Haseeb's real detection code exists, Harsha's backend uses a **mock detector**.
Before Gowtham's real agents exist, Harsha's backend uses **mock agents**.
This allows parallel development.

**Mock directory:** `tests/mocks/`

```python
# tests/mocks/mock_detector.py
class MockPersonDetector:
    """Mock detector that triggers after 2 seconds. Used by Harsha and Gowtham during development."""
    
    def start_monitoring(self):
        import threading
        def trigger():
            time.sleep(2)
            self._callback(DetectionEvent(confidence=0.95, bounding_box=BBox(120, 80, 200, 400)))
        threading.Thread(target=trigger, daemon=True).start()
    
    def on_person_detected(self, callback):
        self._callback = callback
```

```python
# tests/mocks/mock_agents.py
class MockAdmissionsAgent:
    """Returns canned response. Used while Gowtham builds real agent."""
    
    def generate(self, query: str, context: list) -> DomainResponse:
        return DomainResponse(
            answer="MOCK: PES University B.Tech admissions are via PESSAT.",
            citations=["MOCK_SOURCE"],
            confidence=0.5
        )
```

```python
# tests/mocks/mock_riar.py
class MockRIARPipeline:
    """Returns CLEAR ambiguity type. Used while Haseeb builds real RIAR."""
    
    def run(self, query: str, session: SessionObject) -> RIARResult:
        return RIARResult(
            ambiguity_detected=False,
            ambiguity_type="CLEAR",
            refined_query=query,
            domain="admissions"
        )
```

### 3.2 Feature Flags for Module Substitution

In `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Integration flags — set in .env to switch between real and mock modules
    USE_REAL_DETECTOR: bool = False     # Haseeb's module
    USE_REAL_RIAR: bool = False         # Haseeb's RIAR
    USE_REAL_AGENTS: bool = False       # Gowtham's agents
    USE_REAL_ASR: bool = False          # Real Whisper (slow to load)
    USE_REAL_TTS: bool = False          # Real TTS
```

This allows Harsha to test the full backend pipeline from Day 1 without waiting for Haseeb or Gowtham.

---

## 4. Integration Interfaces (Contracts)

### 4.1 RIAR Interface (Haseeb → Harsha)

Haseeb publishes this interface. Harsha calls it.

```python
# riar/pipeline.py  — THIS IS THE CONTRACT HASEEB MUST MAINTAIN

class RIARPipeline:
    """
    Contract: This class interface is frozen after Week 2.
    Any changes must be discussed with Harsha before implementation.
    """
    
    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        ...
    
    def run(
        self,
        query: str,
        session_history: List[Turn],
        language: str = "en"
    ) -> RIARResult:
        """
        Synchronous call. Must return within 2 seconds.
        Returns RIARResult dataclass (see models/riar_models.py).
        """
        ...
    
    def refine(
        self,
        original_query: str,
        clarification_response: str,
        ambiguity_type: str
    ) -> RefinedQuery:
        """
        Called after user provides clarification.
        Returns RefinedQuery with domain routing.
        """
        ...
```

```python
# backend/app/models/riar_models.py — SHARED DATA MODELS

@dataclass
class RIARResult:
    ambiguity_detected: bool
    ambiguity_score: float          # 0.0 to 1.0
    ambiguity_type: str             # CLEAR | SEMANTIC | CONTEXTUAL | CROSS_DOMAIN
    clarification_question: Optional[str]
    refined_query: str
    domain: Optional[str]
    routing_confidence: float
    probe_chunks: List[Chunk]

@dataclass
class RefinedQuery:
    refined_query: str
    domain: str
    routing_confidence: float
    ready_for_rag: bool
```

### 4.2 Domain Agent Interface (Gowtham → Harsha)

Gowtham publishes this interface. Harsha calls it.

```python
# agents/domain/base_agent.py — THIS IS THE CONTRACT GOWTHAM MUST MAINTAIN

from abc import ABC, abstractmethod
from typing import List
from backend.app.models.agent_models import DomainResponse, Chunk

class BaseDomainAgent(ABC):
    """
    Contract: All domain agents implement this interface.
    Frozen after Week 2. Changes must be discussed with Harsha.
    """
    
    domain: str  # Class variable: "admissions" | "academics" | etc.
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        """Retrieves top_k relevant chunks for query. Must return within 1 second."""
        ...
    
    @abstractmethod  
    def generate(
        self,
        query: str,
        context: List[Chunk],
        language: str = "en"
    ) -> DomainResponse:
        """Generates answer grounded in context. Must return within 2 seconds."""
        ...
```

```python
# backend/app/models/agent_models.py — SHARED DATA MODELS

@dataclass
class Chunk:
    chunk_id: str
    source: str
    page: Optional[int]
    text: str
    relevance_score: float

@dataclass
class DomainResponse:
    answer: str
    citations: List[str]
    confidence: float
    domain: str
    retrieved_chunks: List[Chunk]
```

### 4.3 Detection Event Interface (Haseeb → Harsha)

```python
# detection/session_trigger.py — HASEEB'S SIDE

import requests

class SessionTrigger:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
    
    def trigger_session_created(self, event: DetectionEvent):
        """Called when person detected. POSTs to backend."""
        response = requests.post(
            f"{self.backend_url}/api/v1/detect",
            json=event.to_dict()
        )
        return response.json()
    
    def trigger_session_closed(self, session_id: str):
        """Called when person leaves."""
        requests.delete(f"{self.backend_url}/api/v1/detect/{session_id}")
```

---

## 5. Shared Code Policy

### Where Shared Code Lives

```
backend/app/models/           # ALL shared Pydantic + dataclass models
├── session_models.py         # SessionObject, Turn, DetectionEvent
├── riar_models.py            # RIARResult, RefinedQuery
├── agent_models.py           # DomainResponse, Chunk
└── speech_models.py          # ASRResult, TTSResult
```

**Rule:** If two or more modules use the same data type, it lives in `backend/app/models/`. No duplicating models across modules.

### Import Convention

```python
# Correct — import from shared models
from backend.app.models.agent_models import DomainResponse, Chunk

# Wrong — redefine in your own module
class DomainResponse:  # DON'T DO THIS
    ...
```

---

## 6. Merge Frequency & Integration Cadence

### Merge Schedule

| Day | Expectation |
|---|---|
| Monday | Feature branches created from `develop` (post-Monday sync) |
| Wednesday | Mid-week "mini-merge" — at least partial work merged to `develop` |
| Friday | All feature work for the week merged to `develop` by 6pm |
| Saturday/Sunday | No required merges (unless hotfix) |

### Integration Test After Friday Merge

After Friday merge, one person (rotating) runs the integration test suite:

```bash
# Integration test command
pytest tests/integration/ -v --tb=short

# If anything fails, the author fixes it before EOD
```

---

## 7. How to Test Interfaces Before Integration

### Contract Tests

Each module owner writes **contract tests** that verify their implementation matches the interface:

```python
# riar/tests/test_riar_contract.py — HASEEB writes this

def test_riar_pipeline_returns_riar_result():
    """Verify RIAR returns the exact RIARResult dataclass Harsha expects."""
    pipeline = RIARPipeline(mock_vector_store, mock_llm)
    result = pipeline.run("How do I apply for B.Tech?", history=[], language="en")
    
    assert isinstance(result, RIARResult)
    assert isinstance(result.ambiguity_detected, bool)
    assert 0.0 <= result.ambiguity_score <= 1.0
    assert result.ambiguity_type in ["CLEAR", "SEMANTIC", "CONTEXTUAL", "CROSS_DOMAIN"]
    assert isinstance(result.refined_query, str)

def test_riar_refine_returns_refined_query():
    pipeline = RIARPipeline(mock_vector_store, mock_llm)
    result = pipeline.refine("How do I apply?", "B.Tech admission", "CONTEXTUAL")
    
    assert isinstance(result, RefinedQuery)
    assert result.domain in ["admissions", "academics", "placements", "research", "student_services", "navigation"]
    assert 0.0 <= result.routing_confidence <= 1.0
```

```python
# agents/tests/test_agent_contract.py — GOWTHAM writes this

def test_admissions_agent_interface():
    """Verify AdmissionsAgent matches BaseDomainAgent contract."""
    agent = AdmissionsAgent()
    
    # Test retrieve
    chunks = agent.retrieve("PESSAT eligibility criteria", top_k=5)
    assert isinstance(chunks, list)
    assert len(chunks) <= 5
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert isinstance(chunk.relevance_score, float)
    
    # Test generate
    response = agent.generate("PESSAT eligibility", chunks, language="en")
    assert isinstance(response, DomainResponse)
    assert len(response.answer) > 10
    assert len(response.citations) > 0
```

---

## 8. Avoiding Integration Conflicts

### File Ownership Rules

| Directory | Owner | Others need PR approval from |
|---|---|---|
| `riar/` | Haseeb | Haseeb |
| `detection/` | Haseeb | Haseeb |
| `avatar/` | Haseeb | Haseeb |
| `backend/` | Harsha | Harsha |
| `knowledge/` | Gowtham | Gowtham |
| `agents/` | Gowtham (domain), Harsha (coordinator) | Both must approve |
| `backend/app/models/` | Harsha (gatekeeper) | Harsha — any schema change |
| `tests/integration/` | All | Any 1 approval |
| `tests/mocks/` | All | Any 1 approval |
| `docs/` | Haseeb (gatekeeper for structure) | Haseeb |

### Conflict Prevention Rules

1. **Never edit another person's owned files without asking first.**
2. **The `models/` directory is Harsha's gatekeeper territory.** Any addition to shared models requires Harsha's review.
3. **If you need a new endpoint**, tell Harsha first. He adds the stub. You fill the implementation via his contract.
4. **Never change the function signature of a published interface without a grace period of 1 sprint** (with old signature deprecated but working).

---

## 9. Maintaining Backward Compatibility

### Deprecation Protocol

When you need to change an interface:

1. **Add the new version** alongside the old one.
2. **Mark the old version** with a deprecation comment.
3. **Notify the team** in the group chat.
4. **Give one sprint** before removing the old version.

```python
# Example: changing RIARPipeline.run() signature

def run(self, query: str, session_history: list, language: str = "en") -> RIARResult:
    """Current version. Use this."""
    ...

def process(self, query: str) -> RIARResult:
    """DEPRECATED: Use run() instead. Will be removed after Week 4."""
    import warnings
    warnings.warn("RIARPipeline.process() is deprecated. Use run().", DeprecationWarning)
    return self.run(query, session_history=[], language="en")
```

---

## 10. Environment Configuration

### `.env.example` (committed to repo)
### `.env` (gitignored — each person fills in their own)

```env
# ─── LLM ───────────────────────────────────────────────
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# ─── Backend ───────────────────────────────────────────
BACKEND_HOST=localhost
BACKEND_PORT=8000
SECRET_KEY=change-me-to-random-string

# ─── Database ──────────────────────────────────────────
DATABASE_URL=sqlite:///./vidyasahayak.db
REDIS_URL=redis://localhost:6379

# ─── Vector Store ──────────────────────────────────────
CHROMA_PERSIST_DIR=./knowledge/vectorstore
CHROMA_COLLECTION_NAME=vidyasahayak_kb

# ─── Speech ────────────────────────────────────────────
WHISPER_MODEL_SIZE=medium    # medium for dev, large-v3 for prod
TTS_ENGINE=coqui             # coqui | elevenlabs | azure

# ─── Camera / Detection ────────────────────────────────
CAMERA_INDEX=0
DETECTION_CONFIDENCE=0.6
PRESENCE_DURATION_SEC=1.5

# ─── Feature Flags ─────────────────────────────────────
USE_REAL_DETECTOR=false
USE_REAL_RIAR=false
USE_REAL_AGENTS=false
USE_REAL_ASR=false
USE_REAL_TTS=false

# ─── Debug ─────────────────────────────────────────────
DEBUG=true
LOG_LEVEL=INFO
```

**Rule:** Never commit real API keys. Use `.env` which is in `.gitignore`. Share keys via encrypted DM (WhatsApp voice note of key is fine for a university project).
