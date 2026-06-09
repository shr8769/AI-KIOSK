# VidyaSahayak 🎓
### AI Avatar Kiosk for Intelligent Multilingual Student Support and Administrative Assistance
**PES University Research Project — 2026**

---

[![Status](https://img.shields.io/badge/Status-Active%20Development-green)](https://github.com)
[![Research](https://img.shields.io/badge/Research-RIAR%20Framework-blue)](docs/SYSTEM_ARCHITECTURE.md)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Kannada%20%7C%20Hindi-orange)](docs/PROJECT_SCOPE.md)
[![Team](https://img.shields.io/badge/Team-3%20Engineers-purple)](docs/TEAM_OWNERSHIP.md)

---

## What is VidyaSahayak?

VidyaSahayak (*"Knowledge Helper"* in Sanskrit) is an **AI-powered, multilingual kiosk system** deployed at PES University. It assists students, faculty, administrative staff, and visitors through natural voice interactions — combining computer vision, speech processing, multi-agent AI, and retrieval-augmented generation.

The system's core research contribution is the **RIAR Framework** (Retrieval-Informed Ambiguity Resolution) — a novel pipeline that detects and resolves query ambiguity before routing to domain-specific knowledge agents.

---

## Core Capabilities

| Capability | Technology | Owner |
|---|---|---|
| Person Detection | OpenCV + YOLOv8 | Haseeb |
| Voice Interaction | Whisper ASR + TTS | Harsha |
| Multilingual Support | EN / KN / HI | Gowtham |
| Ambiguity Resolution | RIAR Framework | Haseeb |
| Multi-Agent RAG | LangChain / LlamaIndex | Harsha + Gowtham |
| Session Memory | Redis / SQLite | Harsha |
| Campus Navigation | Graph-based Agent | Gowtham |
| Avatar Interaction | MuseTalk / D-ID | Haseeb |

---

## Repository Structure

```
AI-KIOSK/
│
├── docs/                        # All project documentation
│   ├── README.md                # This file
│   ├── PROJECT_SCOPE.md         # Goals, risks, non-goals
│   ├── SYSTEM_ARCHITECTURE.md   # Architecture diagrams and specs
│   ├── API_CONTRACT.md          # All API endpoint contracts
│   ├── TEAM_OWNERSHIP.md        # RACI matrix and ownership
│   ├── SPRINT_PLAN.md           # 7-week sprint breakdown
│   ├── MILESTONE_PLAN.md        # Milestone acceptance criteria
│   ├── INTEGRATION_STRATEGY.md  # How modules communicate
│   ├── RISK_MANAGEMENT.md       # Risk register and mitigations
│   ├── GIT_WORKFLOW.md          # Branching and PR process
│   └── MEETING_PROCESS.md       # Weekly cadence and templates
│
├── backend/                     # FastAPI backend (Harsha)
│   ├── app/
│   │   ├── api/routes/          # Route handlers per module
│   │   ├── core/                # Config, auth, middleware
│   │   ├── services/            # Business logic layer
│   │   ├── models/              # Pydantic + DB models
│   │   └── websockets/          # Real-time WebSocket handlers
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                    # Kiosk UI (Haseeb)
│   ├── src/
│   │   ├── components/          # Avatar, mic, display components
│   │   ├── pages/               # Main kiosk screen
│   │   └── hooks/               # WebSocket and state hooks
│   └── public/
│
├── avatar/                      # Avatar layer (Haseeb)
│   ├── assets/                  # Video/image assets
│   ├── lip_sync/                # MuseTalk integration
│   └── animations/              # Idle / greeting / speaking states
│
├── detection/                   # Person detection (Haseeb)
│   ├── models/                  # YOLO / OpenCV model configs
│   └── tests/
│
├── riar/                        # RIAR Framework (Haseeb)
│   ├── classifiers/             # Ambiguity classifiers
│   ├── retrievers/              # Probe retrieval logic
│   ├── generators/              # Clarification + answer generation
│   └── tests/
│
├── knowledge/                   # Knowledge base (Gowtham)
│   ├── sources/                 # Raw documents per domain
│   │   ├── admissions/
│   │   ├── academics/
│   │   ├── placements/
│   │   ├── research/
│   │   ├── student_services/
│   │   └── navigation/
│   ├── vectorstore/             # Embedded vector DB
│   └── embeddings/              # Embedding scripts + configs
│
├── agents/                      # Multi-agent system (Gowtham + Harsha)
│   ├── coordinator/             # Coordinator agent
│   ├── domain/                  # Domain-specific agents
│   ├── concierge/               # Multilingual concierge
│   └── navigation/              # Campus navigation agent
│
├── evaluation/                  # Evaluation suite (Gowtham)
│   ├── datasets/                # Query datasets + ground truth
│   ├── metrics/                 # Evaluation metric scripts
│   ├── results/                 # Evaluation run results
│   └── scripts/                 # Benchmark runner scripts
│
├── database/                    # DB layer (Harsha)
│   ├── migrations/
│   ├── schemas/
│   └── seeds/
│
├── scripts/                     # Utility scripts (shared)
│   ├── setup/                   # Environment setup
│   ├── data_ingestion/          # KB ingestion pipeline
│   └── deployment/              # Deploy scripts
│
├── tests/                       # Cross-module testing
│   ├── integration/             # Integration test suites
│   ├── e2e/                     # End-to-end tests
│   └── mocks/                   # Mock services for dev
│
├── deployment/                  # Deployment configs
│   ├── docker/
│   ├── nginx/
│   └── systemd/
│
├── meeting_notes/               # Weekly meeting records
│   ├── templates/
│   └── week1/
│
└── .github/                     # GitHub automation
    ├── ISSUE_TEMPLATE/
    ├── workflows/               # CI/CD pipelines
    └── PULL_REQUEST_TEMPLATE/
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional for deployment)
- CUDA GPU recommended for Whisper + Detection

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/PES-University/AI-KIOSK.git
cd AI-KIOSK

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Fill in API keys, DB connection, model paths

# 4. Initialize database
python scripts/setup/init_db.py

# 5. Ingest knowledge base
python scripts/data_ingestion/ingest_all.py

# 6. Start backend
cd backend && uvicorn app.main:app --reload

# 7. Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

---

## Team

| Name | Role | Primary Ownership |
|---|---|---|
| **Haseeb** | Project Lead / Research Lead | RIAR, Detection, Avatar, Frontend UX |
| **Harsha** | Engineering Lead | Backend, Speech Pipeline, DB, Integration |
| **Gowtham** | Knowledge Systems Lead | Knowledge Base, Agents, Navigation, Evaluation |

---

## Documentation Index

| Document | Purpose |
|---|---|
| [PROJECT_SCOPE.md](docs/PROJECT_SCOPE.md) | Problem statement, objectives, risks |
| [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | Full system design |
| [API_CONTRACT.md](docs/API_CONTRACT.md) | All API specifications |
| [TEAM_OWNERSHIP.md](docs/TEAM_OWNERSHIP.md) | RACI matrix |
| [SPRINT_PLAN.md](docs/SPRINT_PLAN.md) | Week-by-week plan |
| [MILESTONE_PLAN.md](docs/MILESTONE_PLAN.md) | Milestone acceptance criteria |
| [INTEGRATION_STRATEGY.md](docs/INTEGRATION_STRATEGY.md) | Integration guide |
| [RISK_MANAGEMENT.md](docs/RISK_MANAGEMENT.md) | Risk register |
| [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) | Git branching & PR rules |
| [MEETING_PROCESS.md](docs/MEETING_PROCESS.md) | Weekly cadence |

---

## Research Output

This project produces a conference/journal paper on:

**"RIAR: Retrieval-Informed Ambiguity Resolution for Conversational AI Systems in Multilingual Academic Environments"**

Principal Researcher: Haseeb
Research Team: Harsha, Gowtham

---

*VidyaSahayak — Making university knowledge accessible to everyone, in every language.*
