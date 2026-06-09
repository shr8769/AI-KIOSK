# SPRINT_PLAN.md
## VidyaSahayak — 7-Week Sprint Plan
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

> **Sprint Rhythm:** Monday–Friday work weeks. Monday kickoff, Friday integration.
> **Daily Standups:** 15 minutes via group chat (async) — What did I do? What will I do? Blockers?
> **Weekly Sync:** Mondays, 30 minutes (video call).

---

## Sprint Overview

| Week | Theme | Primary Goal | Integration Point |
|---|---|---|---|
| Week 1 | Foundation | Repo, environment, skeleton APIs | Friday: Everyone can run the system |
| Week 2 | Core Pipelines | Detection + Speech working | Friday: Audio-in, text-out |
| Week 3 | Knowledge + RIAR Alpha | KB ingested + RIAR v0.1 | Friday: Query → KB → Answer (raw) |
| Week 4 | RIAR + Agents | Full RIAR + domain agents | Friday: RIAR → Routing → Answer |
| Week 5 | Integration | All modules connected | Friday: Full E2E demo (rough) |
| Week 6 | Polish & Evaluation | Quality, latency, user testing | Friday: Demo freeze |
| Week 7 | Finalization | Paper, video, presentation | Final demo day |

---

## Week 1 — Foundation & Setup
**Theme:** Everyone can work. Skeleton is running.
**Goal:** Repository up, environments configured, skeleton APIs responding.

### Monday Kickoff Goal
All three engineers have working dev environment and can run the skeleton backend.

### Tasks

#### Haseeb (Project Lead / Research Lead)
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Create and configure GitHub repository with full folder structure | 2h | Repo live |
| H1.2 | Write README, PROJECT_SCOPE, all docs (this sprint plan) | 4h | Docs committed |
| H1.3 | Define Session Object schema v1 | 2h | `docs/SESSION_SCHEMA.md` |
| H1.4 | Set up person detection development environment (camera, OpenCV, YOLO) | 3h | `detection/` running locally |
| H1.5 | Write detection module stub with event interface | 2h | `detection/detector.py` (stub) |
| H1.6 | Create avatar state machine skeleton | 2h | `avatar/avatar_controller.py` |

#### Harsha (Engineering Lead)
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Bootstrap FastAPI application (routers, middleware, config) | 3h | `backend/` running on :8000 |
| H2.2 | Implement skeleton endpoints: `/detect`, `/asr`, `/riar`, `/rag`, `/tts` | 4h | All endpoints return mock data |
| H2.3 | Set up Redis + SQLite session store | 2h | Session create/get/close working |
| H2.4 | Implement WebSocket skeleton `/ws/session/{id}` | 2h | WS connects, echoes messages |
| H2.5 | Write `docker-compose.yml` for local development | 2h | `docker compose up` works |
| H2.6 | Set up GitHub Actions CI (lint + basic test run) | 2h | CI green on every push |

#### Gowtham (Knowledge Systems Lead)
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Collect PES University documents (admissions, academics, navigation) | 4h | Docs in `knowledge/sources/` |
| G1.2 | Set up ChromaDB and write ingestion pipeline skeleton | 3h | `knowledge/embeddings/ingest.py` |
| G1.3 | Define agent base class interface | 2h | `agents/domain/base_agent.py` |
| G1.4 | Create evaluation dataset outline (query categories + 50 seed queries) | 3h | `evaluation/datasets/seed_queries.json` |
| G1.5 | Research and select TTS models for Kannada and Hindi | 2h | Decision logged in meeting notes |

### Deliverables by Friday
- [ ] GitHub repository live with full structure
- [ ] FastAPI backend running with skeleton responses on all endpoints
- [ ] Docker Compose works for all three engineers
- [ ] `develop` branch has everyone's Week 1 code merged
- [ ] 50+ seed evaluation queries created

### Dependencies
- GitHub repository must be created by Haseeb on Monday
- Harsha can't finalize endpoints without Session Object schema → Haseeb delivers H1.3 by Tuesday

### Risks
| Risk | Mitigation |
|---|---|
| Dev environment setup takes longer than expected | Harsha prepares setup script `scripts/setup/setup_env.sh` by Tuesday |
| University documents hard to obtain | Gowtham starts with publicly available information (website scraping) |

---

## Week 2 — Core Pipelines
**Theme:** Audio in → Text out. Camera sees a person.
**Goal:** Whisper ASR transcribing audio. Person detection triggering sessions.

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Implement real YOLOv8 person detection (not stub) | 4h | `detection/detector.py` (real) |
| H1.2 | Implement presence monitoring loop (ROI, threshold) | 3h | `detection/presence_monitor.py` |
| H1.3 | Connect detection → POST /detect → session created | 2h | End-to-end detection trigger |
| H1.4 | Avatar greeting animation + state transitions | 3h | IDLE → GREETING → LISTENING |
| H1.5 | Write detection tests (mock camera feed) | 2h | `detection/tests/test_detector.py` |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Integrate Whisper ASR (real model, not stub) | 4h | `/asr` returns real transcript |
| H2.2 | Implement audio capture service (mic → WAV) | 3h | `backend/app/services/speech/audio_capture.py` |
| H2.3 | Implement Voice Activity Detection | 2h | `asr_service.py` with VAD |
| H2.4 | Implement TTS (English first) | 3h | `/tts` returns audio file |
| H2.5 | Wire WebSocket: audio stream → ASR → transcript response | 3h | Real-time transcription |
| H2.6 | Write ASR + TTS unit tests | 2h | `backend/tests/test_speech.py` |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Complete document collection (all 6 domains) | 4h | Docs in `knowledge/sources/` |
| G1.2 | Implement and run full ingestion pipeline | 4h | ChromaDB populated |
| G1.3 | Implement admissions domain agent (real retrieval) | 3h | `agents/domain/admissions_agent.py` |
| G1.4 | Implement navigation agent (campus map data) | 3h | `agents/navigation/navigation_agent.py` |
| G1.5 | Write 150 more evaluation queries (reach 200 total) | 2h | `evaluation/datasets/` |

### Friday Integration Test
- Speak into mic → Whisper transcribes → transcript visible in console
- Walk in front of camera → Person detected → Session created → Avatar greets

### Deliverables by Friday
- [ ] Whisper ASR working with real audio input
- [ ] Person detection triggering real sessions
- [ ] ChromaDB populated with university documents
- [ ] Admissions agent can answer simple queries
- [ ] Navigation agent can return room locations

### Dependencies
- Harsha needs working mic/camera hardware access
- Gowtham needs document access from university — follow up if blocked

### Risks
| Risk | Mitigation |
|---|---|
| Whisper latency >3s on hardware | Test with Whisper medium model first; upgrade to large only if hardware supports it |
| Kannada/Hindi ASR quality poor | Collect test samples this week; adjust model choice next week |
| Camera driver issues on kiosk machine | Use USB webcam as backup; mock camera with test video for dev |

---

## Week 3 — Knowledge Base + RIAR Alpha
**Theme:** First version of RIAR. KB answering real questions.
**Goal:** RIAR detects ambiguity. RAG returns grounded answers for admissions/academics.

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Implement probe retrieval (RIAR Step 1) | 3h | `riar/retrievers/probe_retriever.py` |
| H1.2 | Implement ambiguity detection scoring (RIAR Step 2) | 4h | `riar/pipeline.py` Step 2 |
| H1.3 | Implement ambiguity classification (RIAR Step 3) | 4h | `riar/classifiers/ambiguity_classifier.py` |
| H1.4 | Write RIAR unit tests (all 4 ambiguity types) | 3h | `riar/tests/test_riar_pipeline.py` |
| H1.5 | Frontend: Display transcript + RIAR state to screen | 2h | Kiosk UI shows current state |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Implement `/riar` endpoint (calls Haseeb's pipeline) | 2h | Real RIAR responses |
| H2.2 | Implement coordinator agent routing logic | 4h | `agents/coordinator/coordinator.py` |
| H2.3 | Implement `/route` endpoint | 2h | Routes to correct domain agent |
| H2.4 | Implement `/rag` endpoint (calls domain agent + LLM) | 3h | Returns grounded answer |
| H2.5 | Add full session turn logging to DB | 2h | Every turn saved to SQLite |
| H2.6 | Kannada + Hindi TTS integration | 3h | Multilingual TTS working |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Implement remaining domain agents (placements, research, student services) | 5h | All 6 agents implemented |
| G1.2 | Write and test agent prompt templates for all domains | 3h | LLM returns domain-accurate answers |
| G1.3 | Implement language fallback (KN/HI → EN if needed) | 2h | `agents/concierge/language_fallback.py` |
| G1.4 | Run first evaluation pass on 100 queries | 3h | `evaluation/results/week3_baseline.json` |
| G1.5 | Reach 300 annotated evaluation queries | 3h | Evaluation dataset growing |

### Friday Integration Test
- Type/speak an admissions query → RIAR runs → returns ambiguity type → routes to agent → answers
- Deliberately ask ambiguous query → System asks clarification question

### Deliverables by Friday
- [ ] RIAR ambiguity detection and classification working
- [ ] Coordinator routing to correct domain agent
- [ ] All 6 domain agents implemented
- [ ] First baseline evaluation run completed

---

## Week 4 — Full RIAR + Multi-Agent Polish
**Theme:** RIAR is complete. Multi-agent system reliable.
**Goal:** Full RIAR pipeline including clarification + refinement. Answers are grounded and cited.

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Implement clarification generator (RIAR Step 4) | 4h | `riar/generators/clarification_generator.py` |
| H1.2 | Implement query refinement (RIAR Step 5) | 3h | `riar/pipeline.py` Step 5 |
| H1.3 | Implement `/riar/clarify` endpoint logic | 2h | Works with Harsha's endpoint |
| H1.4 | Multilingual clarification questions (KN, HI) | 2h | Clarification in user language |
| H1.5 | Avatar: show listening animation while waiting for clarification | 2h | UX polish |
| H1.6 | Session memory: RIAR uses prior turns as context | 3h | Multi-turn RIAR context |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Implement `/riar/clarify` endpoint | 2h | Accepts clarification response |
| H2.2 | Implement cross-domain agent dispatch (parallel calls) | 3h | Two agents queried simultaneously |
| H2.3 | Implement response merger for cross-domain queries | 2h | Coherent merged answer |
| H2.4 | Add latency monitoring to all endpoints | 2h | Metrics logged to DB |
| H2.5 | Add retry logic for LLM API failures | 2h | System degrades gracefully |
| H2.6 | Performance test: measure E2E latency on hardware | 3h | Latency report |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Improve prompt templates based on Week 3 eval results | 3h | Higher faithfulness scores |
| G1.2 | Add citation formatting to all agent responses | 2h | Every answer has source |
| G1.3 | Build Kannada query test set (100 queries) | 3h | `evaluation/datasets/kannada_queries.json` |
| G1.4 | Build Hindi query test set (100 queries) | 3h | `evaluation/datasets/hindi_queries.json` |
| G1.5 | Evaluate multilingual retrieval quality | 3h | `evaluation/results/week4_multilingual.json` |
| G1.6 | Implement evaluation metrics (RAGAS or custom) | 4h | `evaluation/metrics/` |

### Deliverables by Friday
- [ ] Complete RIAR pipeline (all 7 steps) functional
- [ ] Clarification → refinement → routing working end-to-end
- [ ] Citation in every answer
- [ ] Multilingual test sets ready
- [ ] Latency measurements taken

---

## Week 5 — Full System Integration
**Theme:** All modules connected. E2E flow working.
**Goal:** Person walks in → asks question → receives spoken answer with avatar.

> **This is the highest-risk week. Plan for blockers. Prioritize integration over new features.**

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Integrate detection → session → avatar greeting E2E | 3h | Physical kiosk flow working |
| H1.2 | Connect avatar to TTS audio output (lip sync attempt) | 4h | Avatar speaks (lip sync if possible) |
| H1.3 | Fix any RIAR bugs found during integration | 4h | RIAR stable in full flow |
| H1.4 | Integration test: 20 full-flow queries | 3h | Results logged |
| H1.5 | Frontend UI polish (kiosk display layout) | 3h | Clean, presentable UI |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Wire ALL endpoints into complete flow (orchestrator) | 4h | One request triggers all steps |
| H2.2 | Fix integration bugs from E2E testing | 5h | System stable |
| H2.3 | Load test: 10 consecutive sessions | 2h | No memory leaks / crashes |
| H2.4 | Session cleanup on person exit (DELETE /detect) | 2h | Clean session lifecycle |
| H2.5 | API documentation auto-generation check | 1h | Swagger UI accurate |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Run 200-query evaluation on integrated system | 4h | `evaluation/results/week5_integrated.json` |
| G1.2 | Fix retrieval quality issues found in evaluation | 3h | Improved chunking / metadata |
| G1.3 | Test navigation agent with real campus data | 3h | Navigation accurate for 10+ locations |
| G1.4 | Identify 3 weakest query types and improve | 3h | Targeted improvement |
| G1.5 | Prepare 20-user pilot test plan | 2h | `evaluation/scripts/pilot_plan.md` |

### Friday Integration Demo (Internal)
**Run a full demo for the team:**
- Haseeb stands in front of kiosk camera
- Person detected → greeting
- Asks 5 pre-planned queries (covering all domains)
- RIAR disambiguates 2 of them
- Avatar speaks all responses
- Record the demo video as `meeting_notes/week5/integration_demo.mp4`

---

## Week 6 — Polish, Evaluation & Demo Freeze
**Theme:** Quality, reliability, evaluation results.
**Goal:** Demo-ready system. Evaluation complete. Research results in hand.

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | RIAR evaluation analysis for paper | 4h | Results table for paper |
| H1.2 | Avatar polish (smooth transitions, consistent behavior) | 3h | Avatar feels professional |
| H1.3 | Fix any remaining UX issues | 3h | Kiosk is demo-ready |
| H1.4 | Record demo video (final) | 2h | `deployment/demo_final.mp4` |
| H1.5 | Start research paper draft (Introduction + Methodology) | 4h | 3+ pages written |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Latency optimizations (async parallelism) | 4h | E2E latency <3s achieved |
| H2.2 | System stability: 4-hour unattended run test | 2h | No crashes |
| H2.3 | Error handling polish (graceful degradation everywhere) | 3h | System recovers from all failures |
| H2.4 | Docker deployment packaging | 3h | `docker compose up` = fully working kiosk |
| H2.5 | System monitoring dashboard (basic) | 2h | Latency + session count visible |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Run 20-user pilot test | 4h | `evaluation/results/pilot_results.json` |
| G1.2 | Analyze pilot feedback | 2h | Actionable findings report |
| G1.3 | Final evaluation: 500-query benchmark | 4h | Complete benchmark results |
| G1.4 | Write evaluation section for research paper | 3h | 2+ pages written |
| G1.5 | KB quality improvements from pilot feedback | 3h | Specific missing information added |

### Demo Freeze Friday EOD
**After Friday EOD — no new features. Bug fixes only.**

---

## Week 7 — Finalization & Presentation
**Theme:** Submit. Present. Ship.
**Goal:** Research paper draft ready. Final presentation delivered. Repository clean.

### Tasks

#### Haseeb
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H1.1 | Complete research paper (all sections) | 6h | Full draft paper |
| H1.2 | Prepare conference/journal submission | 2h | Submission ready |
| H1.3 | Finalize project README and documentation | 2h | Polished repository |
| H1.4 | Final presentation slides | 3h | 15-slide deck |
| H1.5 | Tag `v1.0.0` on main | 1h | Final release |

#### Harsha
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| H2.1 | Final deployment on kiosk hardware | 3h | Physical kiosk deployed |
| H2.2 | System documentation (deployment guide) | 2h | `deployment/README.md` |
| H2.3 | Archive all session logs for research | 1h | Data preserved |
| H2.4 | Review and merge all final PRs | 2h | Clean repository |

#### Gowtham
| # | Task | Est. Hours | Deliverable |
|---|---|---|---|
| G1.1 | Complete evaluation report | 4h | Full evaluation report |
| G1.2 | Review research paper (esp. evaluation section) | 3h | Comments and revisions |
| G1.3 | Prepare evaluation section of presentation | 2h | Slides 10-13 |
| G1.4 | Archive all evaluation datasets | 1h | Data preserved in repo |

### Final Checklist
- [ ] System runs on kiosk hardware for 4+ hours without crash
- [ ] Research paper first draft complete
- [ ] All 12 documents in `docs/` finalized
- [ ] `v1.0.0` tagged on `main`
- [ ] Demo video recorded
- [ ] Presentation prepared
- [ ] Evaluation results documented
- [ ] Repository README reflects final state
