# SYSTEM_ARCHITECTURE.md
## VidyaSahayak — System Architecture Document
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Harsha (Engineering Lead) | **Reviewed by:** Haseeb

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KIOSK HARDWARE                               │
│                                                                     │
│  ┌──────────┐    ┌──────────────────────────────────────────────┐  │
│  │  CAMERA  │    │              DISPLAY SCREEN                  │  │
│  │ (1080p)  │    │          (Avatar + Text Output)              │  │
│  └────┬─────┘    └──────────────────────────────────────────────┘  │
│       │                             ▲                               │
│  ┌────▼─────┐                       │                               │
│  │   MIC    │              ┌────────┴──────────┐                   │
│  │(USB/Array│              │   AVATAR ENGINE   │                   │
│  └────┬─────┘              │ (MuseTalk / D-ID) │                   │
│       │                    └────────▲──────────┘                   │
└───────┼─────────────────────────────┼───────────────────────────────┘
        │                             │
        ▼                             │
┌───────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                               │
│                                                                    │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────────────────┐   │
│  │   PERSON     │  │    ASR    │  │          RIAR            │   │
│  │  DETECTION   │→ │ (Whisper) │→ │  (Ambiguity Resolution)  │   │
│  │  (OpenCV +   │  │           │  │                          │   │
│  │   YOLOv8)    │  └───────────┘  └────────────┬─────────────┘   │
│  └──────────────┘                               │                  │
│                                                 ▼                  │
│                               ┌─────────────────────────────┐     │
│                               │    COORDINATOR AGENT        │     │
│                               │  (Query Router + Planner)   │     │
│                               └──────────┬──────────────────┘     │
│                                          │                         │
│              ┌───────────────────────────┼──────────────────┐     │
│              ▼                           ▼                   ▼     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  ADMISSIONS      │  │  ACADEMICS       │  │  NAVIGATION    │  │
│  │  AGENT           │  │  AGENT           │  │  AGENT         │  │
│  │  (RAG)           │  │  (RAG)           │  │  (Graph)       │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬─────────┘  │
│           │                     │                    │             │
│           └─────────────────────┴────────────────────┘             │
│                                 │                                   │
│                     ┌───────────▼────────────┐                     │
│                     │     VECTOR STORE       │                     │
│                     │  (ChromaDB / FAISS)    │                     │
│                     └────────────────────────┘                     │
│                                 │                                   │
│                     ┌───────────▼────────────┐                     │
│                     │          TTS           │                     │
│                     │  (Coqui / ElevenLabs)  │                     │
│                     └────────────────────────┘                     │
│                                 │                                   │
│                     ┌───────────▼────────────┐                     │
│                     │    SESSION STORE        │                     │
│                     │  (Redis + SQLite/PG)    │                     │
│                     └────────────────────────┘                     │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Person Detection Module
**Owner:** Haseeb | **Location:** `detection/`

```
detection/
├── detector.py           # Main detection class
├── presence_monitor.py   # Continuous presence monitoring loop
├── session_trigger.py    # Fires session creation event
├── models/
│   ├── yolov8n.pt        # YOLOv8 nano model weights
│   └── config.yaml       # Detection thresholds, ROI config
└── tests/
    └── test_detector.py
```

**Behavior:**
- Runs continuous loop at 10 FPS on camera feed
- Uses YOLOv8 for person class detection (class 0)
- Applies presence threshold: person detected in ROI for >1.5 seconds → trigger
- Publishes `PERSON_DETECTED` event via internal event bus / WebSocket to backend
- On person exit: publishes `PERSON_LEFT` → session cleanup

**Interface Contract:**
```python
class PersonDetector:
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def on_person_detected(self, callback: Callable[[DetectionEvent], None]) -> None
    def on_person_left(self, callback: Callable[[DetectionEvent], None]) -> None
```

---

### 2.2 Speech Pipeline
**Owner:** Harsha | **Location:** `backend/app/services/speech/`

```
speech/
├── asr_service.py        # Whisper ASR wrapper
├── tts_service.py        # TTS engine wrapper
├── language_detector.py  # Automatic language identification
└── audio_utils.py        # Audio capture, preprocessing
```

**ASR Flow:**
1. Audio captured from USB mic (16kHz, mono, WAV)
2. Voice Activity Detection (VAD) filters silence
3. Whisper medium/large model transcribes audio
4. Language auto-detected or forced per user preference
5. Returns transcript + detected language code

**TTS Flow:**
1. Receives text + language code
2. Selects voice model per language:
   - English: Coqui TTS (or ElevenLabs)
   - Kannada: Google Cloud TTS or Coqui KN model
   - Hindi: Coqui HI or Azure TTS
3. Returns audio bytes (MP3/WAV)
4. Audio played on kiosk speakers simultaneously with avatar animation

---

### 2.3 RIAR Framework
**Owner:** Haseeb | **Location:** `riar/`

```
riar/
├── pipeline.py           # Main RIAR pipeline orchestrator
├── classifiers/
│   ├── ambiguity_classifier.py    # Multi-label ambiguity classifier
│   └── domain_classifier.py       # Predicts relevant domains
├── retrievers/
│   ├── probe_retriever.py         # Initial broad retrieval
│   └── refined_retriever.py       # Post-clarification retrieval
├── generators/
│   ├── clarification_generator.py # Generates clarification questions
│   └── answer_generator.py        # Final grounded answer generation
└── tests/
    └── test_riar_pipeline.py
```

**RIAR Pipeline Steps:**

```
Query
  │
  ▼
Step 1: PROBE RETRIEVAL
  → Retrieve top-10 chunks from vector store without query refinement
  → Purpose: gather initial context signal
  │
  ▼
Step 2: AMBIGUITY DETECTION
  → Does the query + retrieved context contain sufficient signal?
  → Score: ambiguity_score ∈ [0.0, 1.0]
  → Threshold: ambiguity_score > 0.4 → ambiguous
  │
  ▼
Step 3: AMBIGUITY CLASSIFICATION (if ambiguous)
  → Classify into:
    ├── CLEAR       → Proceed to routing
    ├── SEMANTIC    → Multiple meanings (e.g., "library" → physical vs digital)
    ├── CONTEXTUAL  → Missing context (e.g., "my professor" → who?)
    └── CROSS_DOMAIN→ Spans multiple domains (e.g., "fee structure for PhD research")
  │
  ▼
Step 4: CLARIFICATION GENERATION (if not CLEAR)
  → Generate targeted clarification question in user's language
  → Example: "Do you mean the central library or the digital library portal?"
  → Await user response
  │
  ▼
Step 5: QUERY REFINEMENT
  → Merge original query + clarification response
  → Re-classify domain(s)
  │
  ▼
Step 6: DOMAIN ROUTING
  → Route to: [admissions | academics | placements | research | 
               student_services | navigation | general]
  │
  ▼
Step 7: GROUNDED ANSWER GENERATION
  → Domain agent retrieves top-5 relevant chunks
  → LLM generates answer grounded in retrieved context
  → Citations included in response metadata
```

---

### 2.4 Coordinator Agent
**Owner:** Haseeb (implementation & design) | `agents/coordinator/`

The Coordinator Agent is the **central orchestrator**. It:

1. Receives structured query from RIAR (post-disambiguation)
2. Determines if query requires single or multiple domain agents
3. Spawns sub-agent calls in parallel or sequence
4. Merges responses from domain agents
5. Formats final response for TTS

```python
class CoordinatorAgent:
    def route(self, session: SessionObject) -> AgentResponse
    def dispatch_to_domain(self, domain: str, query: str) -> DomainResponse
    def merge_responses(self, responses: List[DomainResponse]) -> str
```

---

### 2.5 Domain Agents
**Owner:** Gowtham | `agents/domain/`, `agents/navigation/`

Each domain agent follows the same interface:

```python
class BaseDomainAgent:
    domain: str
    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]
    def generate(self, query: str, context: List[Chunk]) -> DomainResponse
```

Domain agents available:
- `AdmissionsAgent`
- `AcademicsAgent`
- `PlacementsAgent`
- `ResearchAgent`
- `StudentServicesAgent`
- `NavigationAgent` *(graph-based, not RAG)*

---

### 2.6 Knowledge Base
**Owner:** Gowtham | `knowledge/`

```
knowledge/
├── sources/              # Raw documents (PDF, DOCX, TXT, MD)
│   ├── admissions/       # Fee structures, eligibility, process
│   ├── academics/        # Courses, departments, faculty, schedules
│   ├── placements/       # Companies, statistics, processes
│   ├── research/         # Labs, publications, funding
│   ├── student_services/ # Hostels, clubs, health, events
│   └── navigation/       # Campus maps, rooms, departments
├── vectorstore/          # ChromaDB persistent store
│   └── chroma.sqlite3
└── embeddings/
    ├── ingest.py         # Document ingestion pipeline
    ├── chunker.py        # Intelligent text chunking
    └── embedder.py       # Embedding model wrapper (text-embedding-3-small)
```

**Ingestion Pipeline:**
```
Raw Document (PDF/DOCX)
    → Document Loader (LangChain)
    → Chunker (512 tokens, 50 overlap)
    → Metadata Tagger (domain, source, date)
    → Embedder (OpenAI / Sentence Transformers)
    → ChromaDB Upsert
```

---

### 2.7 Avatar Layer
**Owner:** Haseeb | `avatar/`

```
avatar/
├── avatar_controller.py   # State machine: idle/greeting/speaking/listening
├── lip_sync/
│   ├── musetalk_client.py # MuseTalk API integration
│   └── audio_mapper.py    # Audio-to-phoneme mapping
└── animations/
    ├── idle.mp4
    ├── greeting.mp4
    └── speaking_base.mp4
```

**Avatar States:**
```
IDLE ──(person detected)──► GREETING
GREETING ──(complete)──► LISTENING
LISTENING ──(query received)──► PROCESSING
PROCESSING ──(response ready)──► SPEAKING
SPEAKING ──(complete)──► LISTENING
LISTENING ──(timeout 30s)──► IDLE
```

---

### 2.8 Session Management
**Owner:** Harsha | `backend/app/services/session/`

```python
# Redis: hot session store (active sessions)
# SQLite/Postgres: cold store (completed session logs)

class SessionManager:
    def create_session(self, person_event: DetectionEvent) -> SessionObject
    def get_session(self, session_id: str) -> SessionObject
    def update_session(self, session_id: str, update: dict) -> SessionObject
    def close_session(self, session_id: str) -> None
    def get_history(self, session_id: str) -> List[Turn]
```

---

## 3. Data Flow Architecture

### Complete Request Flow (Happy Path)

```
T+0ms    Camera detects person
T+500ms  PersonDetector confirms presence (1.5s threshold)
T+500ms  Backend creates SessionObject, Avatar switches to GREETING
T+1000ms Greeting audio plays, avatar animates
T+3000ms System enters LISTENING state, mic activates
T+3000ms User speaks query
T+5000ms VAD detects end of speech, audio segment captured
T+5500ms Whisper ASR processes audio → transcript
T+6000ms RIAR Step 1: Probe retrieval (top-10 chunks)
T+6200ms RIAR Step 2: Ambiguity detection
         [IF ambiguous]
T+6300ms RIAR Step 3: Classify ambiguity type
T+6500ms RIAR Step 4: Generate clarification question
T+7000ms TTS generates clarification audio
T+7500ms Avatar speaks clarification → waits for user response
T+9000ms User responds → ASR → RIAR Step 5: Query refinement
         [END ambiguity branch]
T+6500ms RIAR Step 6: Domain routing
T+6600ms Coordinator dispatches to domain agent(s)
T+7000ms Domain agent retrieves top-5 chunks
T+7500ms LLM generates grounded answer (500 token max)
T+7800ms TTS converts answer to audio
T+8000ms Avatar speaks response + lip sync
T+11000ms Response complete, return to LISTENING
```

### Error Flow

```
Any component failure
    → Log error to session store
    → Publish fallback response ("I'm sorry, I didn't catch that. Could you try again?")
    → Avatar returns to LISTENING
    → Do NOT crash the main loop
```

---

## 4. Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              KIOSK MACHINE (Local)               │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │          Docker Compose Stack           │   │
│  │                                         │   │
│  │  ┌──────────┐   ┌──────────────────┐  │   │
│  │  │  FastAPI │   │   Redis          │  │   │
│  │  │  :8000   │   │   :6379          │  │   │
│  │  └──────────┘   └──────────────────┘  │   │
│  │                                         │   │
│  │  ┌──────────┐   ┌──────────────────┐  │   │
│  │  │  React   │   │   ChromaDB       │  │   │
│  │  │  :3000   │   │   (volume)       │  │   │
│  │  └──────────┘   └──────────────────┘  │   │
│  │                                         │   │
│  │  ┌──────────┐   ┌──────────────────┐  │   │
│  │  │  Whisper │   │   SQLite/PG      │  │   │
│  │  │  (local) │   │   (volume)       │  │   │
│  │  └──────────┘   └──────────────────┘  │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  GPU: CUDA for Whisper + YOLOv8                 │
│  Camera: /dev/video0                            │
│  Mic: ALSA hw:1,0                               │
└─────────────────────────────────────────────────┘
         │
         │ (Optional: remote monitoring)
         ▼
┌──────────────────────┐
│  University Network  │
│  (Admin Dashboard)   │
└──────────────────────┘
```

---

## 5. Technology Stack Summary

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Backend Framework | FastAPI | 0.111+ | Async, fast, well-documented |
| ASR | OpenAI Whisper | large-v3 | Best multilingual accuracy |
| LLM | GPT-4o / Llama-3 | Latest | Reasoning quality |
| Embeddings | text-embedding-3-small | Latest | Cost-efficient, accurate |
| Vector DB | ChromaDB | 0.5+ | Local, persistent, simple API |
| Session Cache | Redis | 7.x | Low-latency hot store |
| Persistent DB | SQLite (dev) / PostgreSQL (prod) | — | Session logs |
| Person Detection | YOLOv8 + OpenCV | 8.x / 4.9 | Real-time, accurate |
| TTS | Coqui TTS / ElevenLabs | — | Multilingual support |
| Avatar | MuseTalk | Latest | Lip sync quality |
| Frontend | React + Vite | 18+ / 5+ | Fast, component-based |
| Containerization | Docker Compose | 3.9 | Reproducible deployment |
| Agent Framework | LangChain | 0.2+ | Agent + RAG tooling |
