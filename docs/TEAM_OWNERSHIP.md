# TEAM_OWNERSHIP.md
## VidyaSahayak — Team Ownership & RACI Matrix
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

---

## Team Directory

| Name | Role | Primary Expertise | GitHub Handle |
|---|---|---|---|
| **Haseeb** | Project Lead / Research Lead | Computer Vision, NLP Research, UX | @haseeb |
| **Harsha** | Engineering Lead | Backend, Systems, Integration | @harsha |
| **Gowtham** | Knowledge Systems Lead | NLP, Knowledge Engineering, Evaluation | @gowtham |

---

## RACI Legend

| Code | Meaning |
|---|---|
| **R** | **Responsible** — Does the work |
| **A** | **Accountable** — Owns the outcome, final decision maker |
| **C** | **Consulted** — Input required before decisions |
| **I** | **Informed** — Notified of decisions and progress |

---

## Module RACI Matrix

### Core Infrastructure

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Repository Setup | A/R | C | I | Haseeb creates repo structure |
| CI/CD Pipeline | I | A/R | I | GitHub Actions |
| Docker Compose | C | A/R | I | Harsha owns deployment config |
| Environment Config (.env) | C | A/R | C | Harsha manages secrets |
| Development Environment Docs | A/R | C | C | All must be able to onboard |

---

### Person Detection

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Camera Interface | A/R | C | I | OpenCV camera setup |
| YOLO11 Integration | A/R | I | I | Model config + inference |
| Presence Detection Logic | A/R | C | I | ROI + threshold tuning |
| Session Trigger Event | A/R | C | I | Haseeb fires event |
| Detection API `/detect` | C | A/R | I | Harsha implements endpoint |
| Detection Tests | A/R | I | I | Haseeb writes tests |

---

### Speech Pipeline

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Whisper ASR Integration | C | A/R | I | Model selection, serving |
| Audio Capture (Mic) | C | A/R | I | ALSA/PortAudio config |
| Voice Activity Detection | C | A/R | I | Silero VAD or WebRTC VAD |
| Language Detection | C | A/R | C | Integrated with Whisper |
| TTS Engine Integration | C | A/R | C | Coqui / ElevenLabs |
| Kannada TTS Quality | I | A/R | C | Gowtham provides test queries |
| Hindi TTS Quality | I | A/R | C | Gowtham provides test queries |
| ASR API `/asr` | I | A/R | I | Harsha owns |
| TTS API `/tts` | I | A/R | I | Harsha owns |
| Speech Tests | C | A/R | C | Gowtham provides multilingual test cases |

---

### RIAR Framework (Research Core)

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| RIAR Algorithm Design | A/R | C | C | Research contribution of Haseeb |
| Probe Retrieval | A/R | C | C | Uses vector store built by Gowtham |
| Ambiguity Detection | A/R | C | I | Scoring mechanism |
| Ambiguity Classification | A/R | C | C | Multi-class classifier |
| Clarification Generator | A/R | C | C | LLM prompt engineering |
| Query Refinement Logic | A/R | C | C | Merge strategy |
| RIAR API `/riar` | C | A/R | I | Haseeb designs, Harsha implements |
| RIAR API `/riar/clarify` | C | A/R | I | Harsha implements |
| RIAR Unit Tests | A/R | C | C | Haseeb writes |
| RIAR Evaluation | C | I | A/R | Gowtham runs eval |
| RIAR Research Paper | A/R | C | C | Haseeb writes, team reviews |

---

### Backend & API Layer

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| FastAPI Application Setup | I | A/R | I | Main app, routers, middleware |
| WebSocket Handler | C | A/R | I | Real-time session communication |
| Session Manager | C | A/R | I | Redis + SQLite session handling |
| Session API | I | A/R | I | Harsha owns all session endpoints |
| Coordinator Agent | A/R | C | C | Routing logic |
| Route API `/route` | A/R | C | C | Haseeb owns |
| RAG API `/rag` | C | A/R | C | Harsha implements, Gowtham provides logic |
| API Gateway / Rate Limiting | I | A/R | I | Harsha owns |
| API Documentation (OpenAPI) | C | A/R | I | Auto-generated via FastAPI |
| Backend Tests | C | A/R | C | Harsha writes; Haseeb + Gowtham provide test cases |

---

### Knowledge Base

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Document Collection (Admissions) | I | I | A/R | Raw documents from university |
| Document Collection (Academics) | I | I | A/R | — |
| Document Collection (Placements) | I | I | A/R | — |
| Document Collection (Research) | I | I | A/R | — |
| Document Collection (Student Services) | I | I | A/R | — |
| Document Collection (Navigation) | I | I | A/R | — |
| Ingestion Pipeline | I | C | A/R | Python ingestion scripts |
| Chunking Strategy | C | I | A/R | Chunk size + overlap decisions |
| Embedding Model Selection | C | C | A/R | Gowtham benchmarks options |
| ChromaDB Vector Store | I | C | A/R | Gowtham manages |
| Metadata Schema | C | C | A/R | Gowtham defines |
| Knowledge Base Tests | I | I | A/R | Retrieval quality tests |

---

### Domain Agents

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Agent Base Class / Interface | A/R | C | C | Haseeb defines interface |
| Admissions Agent | I | C | A/R | Gowtham implements |
| Academics Agent | I | C | A/R | — |
| Placements Agent | I | C | A/R | — |
| Research Agent | I | C | A/R | — |
| Student Services Agent | I | C | A/R | — |
| Navigation Agent | I | C | A/R | Graph-based, not RAG |
| Agent Prompt Templates | C | C | A/R | Gowtham writes prompts |
| Agent Tests | I | C | A/R | Gowtham writes |

---

### Multilingual Concierge

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| English Response Quality | C | C | A/R | Gowtham owns response quality |
| Kannada Translation / Response | C | C | A/R | — |
| Hindi Translation / Response | C | C | A/R | — |
| Multilingual Prompt Templates | C | I | A/R | — |
| Language Fallback Logic | I | C | A/R | If KN/HI fails, fall to EN |

---

### Avatar Layer

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Avatar State Machine | A/R | C | I | IDLE/GREETING/SPEAKING/LISTENING |
| Greeting Animation | A/R | I | I | — |
| Lip Sync Integration | A/R | C | I | MuseTalk integration |
| Avatar Frontend Component | A/R | C | I | React component |
| Avatar-Backend Communication | C | A/R | I | WebSocket message handling |
| Idle Animation | A/R | I | I | — |

---

### Evaluation

| Module | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| Query Dataset Creation | C | I | A/R | 500+ queries |
| Ground Truth Annotation | C | I | A/R | — |
| RIAR Evaluation Metrics | C | I | A/R | Gowtham designs metrics |
| RAG Evaluation (Faithfulness, Relevance) | C | I | A/R | RAGAS or custom |
| ASR Accuracy Evaluation | I | C | A/R | WER per language |
| Pilot User Testing | C | C | A/R | Gowtham runs pilot |
| Evaluation Dashboard | I | C | A/R | — |
| Research Results Analysis | A/R | I | C | Haseeb analyzes for paper |

---

### Documentation

| Document | Haseeb | Harsha | Gowtham | Notes |
|---|---|---|---|---|
| README.md | A/R | C | C | Haseeb maintains |
| PROJECT_SCOPE.md | A/R | C | C | — |
| SYSTEM_ARCHITECTURE.md | C | A/R | C | Harsha maintains |
| API_CONTRACT.md | I | A/R | I | Harsha owns |
| TEAM_OWNERSHIP.md | A/R | I | I | Haseeb maintains |
| SPRINT_PLAN.md | A/R | C | C | Haseeb maintains |
| INTEGRATION_STRATEGY.md | C | A/R | C | Harsha maintains |
| RISK_MANAGEMENT.md | A/R | C | C | Haseeb updates weekly |
| GIT_WORKFLOW.md | A/R | C | I | Haseeb maintains |
| Research Paper | A/R | C | C | Haseeb writes; team reviews |

---

## Decision Authority Matrix

Who has final say on key decisions:

| Decision Type | Authority | Must Consult |
|---|---|---|
| Research approach / RIAR design | Haseeb | Harsha, Gowtham |
| Backend architecture changes | Harsha | Haseeb |
| API contract changes | Harsha | Haseeb, Gowtham |
| Knowledge base domain decisions | Gowtham | Haseeb |
| LLM / model selection | Harsha (cost) + Haseeb (quality) | All |
| Sprint plan adjustments | Haseeb | All |
| Go/No-go for demo | Haseeb | All |
| Research paper content | Haseeb | All |
| Merge to `main` | Any 2 of 3 with PR approval | — |
| Architecture refactor | Harsha | All |

---

## Escalation Path

1. **Within module:** Owner resolves independently.
2. **Cross-module conflict:** Owners of affected modules discuss and resolve.
3. **Cannot resolve in 30 minutes:** Escalate to Monday standup for team decision.
4. **Blocks sprint delivery:** Haseeb (Project Lead) makes final call.

---

## Contribution Guidelines

- Every PR must be reviewed by at least **one other team member** before merge.
- No one merges their own PR to `develop` or `main`.
- If a module owner is blocked for more than **1 day**, they must raise a blocker in the group chat.
- Code in your owned modules is your responsibility — tests, documentation, and quality.
