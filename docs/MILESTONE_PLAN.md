# MILESTONE_PLAN.md
## VidyaSahayak — Milestone Plan with Acceptance Criteria
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

---

## Milestone Overview

| # | Milestone | Target Date | Theme |
|---|---|---|---|
| M1 | Skeleton Demo | End of Week 1 | Repo + APIs running |
| M2 | Voice Pipeline | End of Week 2 | Speech + Detection working |
| M3 | RIAR Prototype | End of Week 3 | Ambiguity resolution working |
| M4 | Multi-Agent RAG | End of Week 4 | Full RIAR + grounded answers |
| M5 | Integration Complete | End of Week 5 | E2E pipeline working |
| M6 | Demo Freeze | End of Week 6 | Polished, evaluated, frozen |
| M7 | Final Presentation | End of Week 7 | Research submitted, demo delivered |

---

## M1 — Skeleton Demo
**Target:** End of Week 1 (Friday)
**Owner:** All (Harsha leads integration, Haseeb leads repo setup)
**Tag:** `v0.1.0-skeleton`

### Acceptance Criteria

**Repository:**
- [ ] GitHub repository is live and accessible to all team members
- [ ] Full folder structure created as per README
- [ ] All team members can clone and run the project
- [ ] CI pipeline is green (runs lint + placeholder tests)
- [ ] Docker Compose starts without errors

**Backend:**
- [ ] FastAPI server starts on port 8000
- [ ] All 7 endpoints respond (with mock data):
  - [ ] `POST /api/v1/detect` → returns mock `session_id`
  - [ ] `POST /api/v1/asr` → returns mock transcript
  - [ ] `POST /api/v1/riar` → returns mock CLEAR result
  - [ ] `POST /api/v1/riar/clarify` → returns mock refined query
  - [ ] `POST /api/v1/route` → returns mock chunks
  - [ ] `POST /api/v1/rag` → returns mock answer
  - [ ] `POST /api/v1/tts` → returns mock audio URL
- [ ] WebSocket `/ws/session/{id}` connects and echoes messages
- [ ] Swagger UI accessible at `http://localhost:8000/docs`

**Session Store:**
- [ ] `POST /detect` creates a session in Redis/SQLite
- [ ] `GET /session/{id}` returns session object
- [ ] `DELETE /detect/{id}` closes session

**Documentation:**
- [ ] README.md complete and accurate
- [ ] PROJECT_SCOPE.md written
- [ ] SYSTEM_ARCHITECTURE.md written
- [ ] API_CONTRACT.md complete with all schemas
- [ ] TEAM_OWNERSHIP.md with RACI matrix

**Definition of Done:**
> A team member opens a browser, navigates to `http://localhost:8000/docs`, calls `POST /detect` with a payload, and receives a session ID. No crashes. No 500 errors on documented endpoints.

---

## M2 — Voice Pipeline
**Target:** End of Week 2 (Friday)
**Owner:** Harsha (Speech), Haseeb (Detection, Avatar)
**Tag:** `v0.2.0-voice`

### Acceptance Criteria

**Person Detection:**
- [ ] Camera feed is captured from physical webcam
- [ ] YOLOv8 detects a person in the frame with confidence > 0.6
- [ ] Person must be present for 1.5+ seconds before trigger fires
- [ ] Detection event POSTs to backend and creates session
- [ ] Person leaving closes session within 5 seconds
- [ ] Detection runs at 10 FPS without crashing

**ASR (Whisper):**
- [ ] English audio from microphone is transcribed with WER < 15%
- [ ] Kannada audio is transcribed (WER < 25%)
- [ ] Hindi audio is transcribed (WER < 20%)
- [ ] VAD correctly identifies end of speech (no premature cutoffs)
- [ ] Transcription returns within 2 seconds for 10-second audio
- [ ] `POST /asr` returns correct transcript + detected language

**TTS:**
- [ ] English TTS generates audio file within 500ms for 100-word text
- [ ] Kannada TTS generates audio (voice sounds natural)
- [ ] Hindi TTS generates audio (voice sounds natural)
- [ ] Audio plays on kiosk speakers

**Avatar:**
- [ ] Avatar renders on display screen
- [ ] Avatar transitions: IDLE → GREETING → LISTENING → SPEAKING → IDLE
- [ ] Greeting audio plays when person detected
- [ ] Avatar enters LISTENING state after greeting

**End-to-End Test:**
- [ ] Walk in front of camera → avatar greets → speak a sentence → transcription displayed → text-to-speech response plays

**Definition of Done:**
> A real person stands in front of the kiosk. The camera detects them. The avatar greets them. They speak a question. Whisper transcribes it. The system speaks a response (even mock). This full loop runs without manual intervention.

---

## M3 — RIAR Prototype
**Target:** End of Week 3 (Friday)
**Owner:** Haseeb (RIAR), Gowtham (KB + Agents), Harsha (endpoints)
**Tag:** `v0.3.0-riar`

### Acceptance Criteria

**Knowledge Base:**
- [ ] At least 3 domains populated (Admissions, Academics, Navigation)
- [ ] Each domain has minimum 20 documents / chunks indexed
- [ ] ChromaDB returns relevant results for domain-appropriate queries
- [ ] Retrieval precision@5 > 0.6 for admissions queries
- [ ] Retrieval precision@5 > 0.6 for academics queries

**Domain Agents:**
- [ ] `AdmissionsAgent` returns correct answers for 10 test questions
- [ ] `AcademicsAgent` returns correct answers for 10 test questions
- [ ] `NavigationAgent` returns correct room/building for 10 queries

**RIAR Pipeline (Alpha):**
- [ ] Probe retrieval fetches top-10 chunks from vector store
- [ ] Ambiguity score is computed for all test queries
- [ ] Ambiguity type classification works for:
  - [ ] CLEAR queries (correctly classified ≥ 80% of the time)
  - [ ] SEMANTIC queries (correctly classified ≥ 70% of the time)
  - [ ] CONTEXTUAL queries (correctly classified ≥ 70% of the time)
  - [ ] CROSS_DOMAIN queries (correctly classified ≥ 65% of the time)
- [ ] Clarification question generated for non-CLEAR queries
- [ ] Clarification questions are linguistically appropriate (human judgment)

**Integration:**
- [ ] `POST /riar` returns real (not mock) RIAR result
- [ ] Coordinator routes to correct domain agent for CLEAR queries
- [ ] `POST /rag` returns grounded answer with citations

**Evaluation Checkpoint:**
- [ ] First formal evaluation run on 100-query dataset
- [ ] RIAR classification F1 > 0.70 on test set
- [ ] Results documented in `evaluation/results/week3_baseline.json`

**Definition of Done:**
> Ask the system "Can you tell me about the library?" → RIAR detects SEMANTIC ambiguity → system asks "Do you mean the physical library or the digital library portal?" → user clarifies → system routes to correct agent → returns cited answer.

---

## M4 — Multi-Agent RAG
**Target:** End of Week 4 (Friday)
**Owner:** Haseeb (RIAR complete), Gowtham (all agents), Harsha (orchestration)
**Tag:** `v0.4.0-multiagent`

### Acceptance Criteria

**RIAR — Complete Pipeline:**
- [ ] All 7 RIAR steps functional
- [ ] Clarification response integrated via `/riar/clarify`
- [ ] Query refinement produces measurably better retrieval (test with 20 query pairs)
- [ ] RIAR classification F1 > 0.78 on evaluation set
- [ ] RIAR handles multilingual queries (EN, KN, HI)
- [ ] RIAR runs within 500ms (excluding LLM calls)

**All Domain Agents:**
- [ ] All 6 domain agents implemented and tested
- [ ] Each agent passes its contract test
- [ ] Answers include citations (source + page number)
- [ ] Agent answers are grounded (not hallucinated — spot-checked by Gowtham)

**Cross-Domain Queries:**
- [ ] Coordinator correctly identifies cross-domain queries
- [ ] Parallel agent dispatch works for 2 simultaneous agents
- [ ] Merged response is coherent (human judgment)

**Multilingual:**
- [ ] Kannada responses generated correctly for 5 test queries
- [ ] Hindi responses generated correctly for 5 test queries
- [ ] Language of response matches language of query

**Latency:**
- [ ] RIAR step: <500ms
- [ ] Retrieval step: <500ms
- [ ] LLM generation step: <2000ms
- [ ] TTS step: <500ms
- [ ] Total E2E (non-GPU steps): <3500ms

**Definition of Done:**
> Submit 20 queries (mix of all domains, all languages, mix of CLEAR and AMBIGUOUS). All receive grounded, cited answers. Cross-domain queries receive merged responses. Kannada and Hindi queries receive responses in the correct language.

---

## M5 — Integration Complete
**Target:** End of Week 5 (Friday)
**Owner:** All — Harsha leads integration sprint
**Tag:** `v0.5.0-integrated`

### Acceptance Criteria

**Full E2E Flow:**
- [ ] Physical kiosk: Person detected → greeting → voice query → RIAR → domain agent → TTS → avatar speaks → listen again
- [ ] Flow works without any manual intervention
- [ ] No crashes during 30-minute continuous operation
- [ ] Session lifecycle (create → active → close) works correctly in all cases:
  - [ ] Normal exit (person leaves)
  - [ ] Timeout exit (person inactive for 30s)
  - [ ] Error recovery (component failure → graceful response)

**Avatar:**
- [ ] Avatar visually in sync with speech (lip sync or acceptable approximation)
- [ ] All 5 avatar states render correctly
- [ ] No video glitches or freezes during transitions

**Performance:**
- [ ] 90th percentile E2E latency < 4 seconds (measured over 20 queries)
- [ ] System handles 3 consecutive sessions without degradation

**Integration Tests:**
- [ ] `pytest tests/integration/` passes with 0 failures
- [ ] 20-query integration test suite runs and all produce valid responses

**Internal Demo:**
- [ ] Internal team demo conducted and recorded
- [ ] Demo video saved to `meeting_notes/week5/integration_demo.mp4`
- [ ] All team members have seen the full system working

**Definition of Done:**
> The team conducts a 15-minute demo of the complete system. A non-team-member interacts with the kiosk (asking at least 5 questions across 3 domains). The system works correctly without any developer intervention.

---

## M6 — Demo Freeze
**Target:** End of Week 6 (Friday EOD)
**Owner:** All — Haseeb makes final call
**Tag:** `v1.0.0-rc1` (Release Candidate)

> After this milestone: **Feature freeze.** Only bug fixes are allowed on `main`.

### Acceptance Criteria

**System Quality:**
- [ ] System runs continuously for 4 hours without crash
- [ ] E2E latency < 3 seconds (90th percentile, 50-query sample)
- [ ] All known blocking bugs fixed (P1 and P2 bugs = 0)
- [ ] Error recovery works for all component failures
- [ ] Avatar lip sync is demo-quality

**Evaluation:**
- [ ] 500-query evaluation benchmark completed
- [ ] RIAR classification F1 > 0.80 on evaluation set
- [ ] RAG faithfulness score > 0.75 (RAGAS or equivalent)
- [ ] ASR WER < 15% (English), < 25% (Kannada), < 22% (Hindi)
- [ ] 20-user pilot completed and results documented

**Research:**
- [ ] RIAR evaluation results table complete
- [ ] Comparison baseline (no-RIAR system) results available
- [ ] Research paper methodology section written

**Repository:**
- [ ] All `docs/` files accurate and final
- [ ] All modules have README files
- [ ] `tests/` coverage > 60% for backend + RIAR

**Definition of Done:**
> A faculty advisor (or any external reviewer) interacts with the kiosk for 20 minutes. They report the system is demo-ready. The evaluation results show RIAR F1 > 0.80. No crashes occurred.

---

## M7 — Final Presentation
**Target:** End of Week 7 (Demo Day)
**Owner:** All — Haseeb leads
**Tag:** `v1.0.0`

### Acceptance Criteria

**Research Output:**
- [ ] Research paper first complete draft written (all sections)
- [ ] Paper is formatted according to target venue guidelines
- [ ] Abstract clearly states RIAR contribution and results
- [ ] Paper is ready for advisor review / submission

**Repository:**
- [ ] `v1.0.0` tagged on `main`
- [ ] All documentation finalized
- [ ] Evaluation datasets committed to repo
- [ ] Demo video committed to repo
- [ ] Deployment guide written and tested

**Presentation:**
- [ ] 15-slide presentation deck complete
- [ ] Live demo works during presentation (or video backup ready)
- [ ] Each team member can explain their module
- [ ] Research contribution (RIAR) clearly articulated

**Evaluation Results Published:**
- [ ] Evaluation results in `evaluation/results/final/`
- [ ] Comparison table: with RIAR vs. without RIAR
- [ ] Per-language performance breakdown
- [ ] Per-domain performance breakdown

**Definition of Done:**
> Team delivers the final presentation. The kiosk demo works (or video backup plays). The research paper is submitted or ready for submission. The repository is clean and documented.
