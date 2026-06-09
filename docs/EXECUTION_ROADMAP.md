# EXECUTION_ROADMAP.md
## VidyaSahayak — Senior Engineering Manager's Execution Handbook
**Version:** 1.0 | **Date:** June 2026
**Author:** Haseeb (Project Lead & Research Lead)

> This document is the project's operating system.
> Read this before writing any code. Share it with every team member on Day 1.
> If in doubt about a process, the answer is in this document.

---

## 1. Project at a Glance

| Item | Value |
|---|---|
| **Project Name** | VidyaSahayak — AI Avatar Kiosk |
| **Institution** | PES University |
| **Duration** | 7 weeks |
| **Team Size** | 3 engineers |
| **Research Contribution** | RIAR Framework (Retrieval-Informed Ambiguity Resolution) |
| **Primary Goal** | Working kiosk + research paper |
| **Repository** | github.com/PES-University/AI-KIOSK |

---

## 2. The Project Operating System

This project has the following operational documents. Bookmark them all.

| Document | Owner | Purpose | Update Frequency |
|---|---|---|---|
| [README.md](../README.md) | Haseeb | Project overview and quickstart | At milestones |
| [PROJECT_SCOPE.md](PROJECT_SCOPE.md) | Haseeb | What we are and are not building | Start of project |
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Harsha | How the system is designed | When architecture changes |
| [API_CONTRACT.md](API_CONTRACT.md) | Harsha | API specs — the integration law | Before any endpoint changes |
| [TEAM_OWNERSHIP.md](TEAM_OWNERSHIP.md) | Haseeb | Who owns what — RACI | Start of project |
| [SPRINT_PLAN.md](SPRINT_PLAN.md) | Haseeb | Week-by-week tasks | Every week |
| [MILESTONE_PLAN.md](MILESTONE_PLAN.md) | Haseeb | Acceptance criteria | At each milestone |
| [INTEGRATION_STRATEGY.md](INTEGRATION_STRATEGY.md) | Harsha | How to work in parallel safely | When integration patterns change |
| [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md) | Haseeb | Risk register | Every Monday |
| [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Haseeb | Branching and PR rules | When process changes |
| [MEETING_PROCESS.md](MEETING_PROCESS.md) | Haseeb | Meeting cadence and templates | Start of project |
| **This document** | Haseeb | The meta-guide | At major changes |

---

## 3. Engineering Principles

These principles govern how we make every technical decision.

### 3.1 Interface Before Implementation
**Rule:** Define the API/interface before writing the implementation.

Every module integration is agreed on paper (in `API_CONTRACT.md` or `INTEGRATION_STRATEGY.md`) before a line of code is written. The contract is the constitution.

**Why:** With 3 people working in parallel, interface mismatches cause the worst integration pain. Agreeing upfront eliminates 80% of integration bugs.

### 3.2 Mock First, Integrate Later
**Rule:** Every module works with mocks of all dependencies from Day 1.

Harsha's backend starts with mock detectors, mock RIAR, and mock agents. When the real modules are ready, they are swapped in with feature flags.

**Why:** No one is blocked waiting for another person's module.

### 3.3 Failing Loudly > Failing Silently
**Rule:** When something fails, return a clear error and log it. Never swallow exceptions.

The system must always tell the user something (even a fallback response). It must never crash silently.

### 3.4 Research Quality Over Code Quality (in the research modules)
**Rule:** In `riar/` and evaluation code, scientific correctness matters more than code elegance.

Keep the RIAR pipeline readable and documented. The algorithm must be reproducible by another researcher from the code alone.

### 3.5 Latency Is a First-Class Citizen
**Rule:** Measure latency at every integration point. Log it in every response.

We have a <3-second E2E target. If we don't measure, we can't optimize. Every API response includes a `latency_ms` field.

---

## 4. Critical Path

The following sequence is the minimum viable demo path. Everything else is enhancement.

```
Week 1:  Repo + all APIs responding (even mocks)
Week 2:  Person detected → mic captures → Whisper transcribes
Week 3:  Transcript → RIAR → domain agent → grounded answer
Week 4:  Full RIAR (with clarification) + all 6 domains
Week 5:  Detection → ASR → RIAR → Agent → TTS → Avatar (E2E)
Week 6:  Stable + evaluated
Week 7:  Paper + presentation
```

**If you must cut scope:** Cut in this order (last things first):
1. ~~Lip sync (use static avatar)~~ → Cut if MuseTalk fails
2. ~~Hindi language~~ → Keep EN + KN as minimum
3. ~~Placements, Research, Student Services domains~~ → Keep Admissions, Academics, Navigation
4. ~~Session memory across turns~~ → Keep single-turn functionality
5. **Never cut:** RIAR framework (it's the research contribution)
6. **Never cut:** English voice interaction (it's the core demo)
7. **Never cut:** At least 3 knowledge domains

---

## 5. Decision Log (Running)

Track major decisions here so we don't revisit them.

| # | Date | Decision | Made by | Rationale |
|---|---|---|---|---|
| D001 | 2026-06-09 | Use ChromaDB as vector store | Harsha + Gowtham | Local, persistent, easy API |
| D002 | 2026-06-09 | Use Whisper medium for dev, large-v3 for prod | Harsha | Latency vs. accuracy tradeoff |
| D003 | 2026-06-09 | Use GPT-4o as LLM, gpt-4o-mini for dev | Harsha | Cost management |
| D004 | 2026-06-09 | Mock-first development with feature flags | Harsha | Enable parallel development |
| D005 | 2026-06-09 | RIAR implemented in Python, called by FastAPI | Haseeb + Harsha | Minimize latency, simpler deployment |
| D006 | 2026-06-09 | Domain agents use same base class interface | Gowtham + Harsha | Coordinator can treat all agents uniformly |
| D007 | 2026-06-09 | English as base language for retrieval; answer translated | Gowtham | KB is primarily in English |

*Add new decisions with date, rationale, and decision maker.*

---

## 6. Week-by-Week Execution Checklist

### Before Week 1 Begins
- [ ] All team members have GitHub access to the repository
- [ ] All team members can run `git clone` and `docker compose up`
- [ ] `.env` file shared privately (not in repo)
- [ ] Communication channel established (WhatsApp / Slack)
- [ ] Monday Week 1 sync time agreed
- [ ] Faculty advisor informed of project start and communication plan

### Start of Each Week
- [ ] Previous week's branches merged to `develop`
- [ ] `develop` branch is passing CI
- [ ] Monday sync conducted, notes committed
- [ ] Risk register reviewed
- [ ] Sprint tasks assigned and tracked

### End of Each Week (Friday)
- [ ] All feature branches for the week merged to `develop`
- [ ] Integration tests pass on `develop`
- [ ] Meeting notes committed to `meeting_notes/`
- [ ] Risk register updated
- [ ] Blockers for next week identified

### At Each Milestone
- [ ] Acceptance criteria reviewed against milestone definition
- [ ] Team demo conducted
- [ ] Demo video recorded
- [ ] Milestone tagged in git
- [ ] Research notes updated

---

## 7. Communication Protocol

### Response Time Expectations

| Channel | Expected Response | Use for |
|---|---|---|
| Group Chat | Within 2 hours (working hours) | Daily communication, quick questions |
| GitHub PR | Within 24 hours | Code review |
| Async standup | By 10 AM daily | Daily status |
| Blocker escalation | Within 1 hour | "I'm completely blocked" situations |

### When to Call an Emergency Sync
(don't wait for Monday)

- A blocker will prevent an entire sprint from completing
- An integration conflict is discovered that affects multiple modules
- A risk has materialized (system is broken on `develop`)
- A scope change is proposed that affects another person's module

### Information Sharing
- Research findings go in `docs/` or as GitHub Discussion
- Bug reports go in GitHub Issues (use the template)
- Design decisions go in this document's Decision Log
- Meeting notes go in `meeting_notes/`
- Don't make important decisions in private DMs — use GitHub or the group chat

---

## 8. Quality Gates

These gates must be passed before merging to each branch.

### Gate: Merge to `develop`
- [ ] At least 1 PR approval
- [ ] CI passes (all tests green)
- [ ] No `print()` debug statements
- [ ] Contract tests pass for any modified interface
- [ ] API_CONTRACT.md updated if endpoints changed

### Gate: Merge to `main` (milestone)
- [ ] At least 2 PR approvals
- [ ] All integration tests pass
- [ ] Demo walkthrough recorded
- [ ] No P0 or P1 bugs open
- [ ] Relevant docs updated
- [ ] Milestone acceptance criteria met

---

## 9. The Research Paper Strategy

The research paper is a deliverable, not an afterthought.

### Target Contribution
**RIAR: Retrieval-Informed Ambiguity Resolution for Conversational AI Systems in Multilingual Academic Environments**

### Paper Structure (Target Journal: NLP/AI conference)

| Section | Owner | Target Words | Due |
|---|---|---|---|
| Abstract | Haseeb | 250 | Week 7 |
| Introduction | Haseeb | 600 | Week 6 |
| Related Work | Haseeb | 800 | Week 5 |
| Methodology (RIAR) | Haseeb | 1200 | Week 5 |
| System Architecture | Haseeb + Harsha | 600 | Week 5 |
| Experimental Setup | Gowtham | 500 | Week 6 |
| Results | Haseeb + Gowtham | 800 | Week 7 |
| Discussion | Haseeb | 400 | Week 7 |
| Conclusion | Haseeb | 200 | Week 7 |

### What Makes This Paper Novel
1. RIAR is a new pipeline concept — not just RAG, but retrieval-informed ambiguity detection first
2. Applied to multilingual academic domain (EN/KN/HI) — underrepresented in literature
3. Evaluation on real university queries with human annotations
4. Comparison: system without RIAR vs. with RIAR — measurable improvement

### Evaluation Metrics to Report
- RIAR Ambiguity Classification: F1, Precision, Recall (per type)
- RAG Quality: Faithfulness, Answer Relevance, Context Precision (RAGAS)
- ASR Quality: WER (per language)
- System Latency: Median and P90 E2E latency
- User Satisfaction: Pilot survey scores

---

## 10. Post-Project Checklist

When the project is complete:

- [ ] `v1.0.0` tagged on `main`
- [ ] Research paper submitted or ready for submission
- [ ] All evaluation data preserved in `evaluation/`
- [ ] Deployment guide written and tested
- [ ] System can be reproduced from README alone
- [ ] Acknowledgments: Faculty advisor, PES University
- [ ] All team members have their contributions documented
- [ ] Open-source consideration: Can the RIAR library be published separately?

---

## 11. Appendix: Useful Commands

### Daily Development

```bash
# Sync latest develop
git checkout develop && git pull origin develop

# Create feature branch
git checkout -b feature/haseeb/riar-ambiguity-detection

# Run backend tests
cd AI-KIOSK && pytest backend/tests/ -v

# Run RIAR tests
pytest riar/tests/ -v

# Run all tests
pytest backend/tests/ riar/tests/ agents/ -v

# Start backend
uvicorn backend.app.main:app --reload --port 8000

# Start with docker
docker compose up

# Check API docs
open http://localhost:8000/docs
```

### Integration Testing

```bash
# Run integration tests
pytest tests/integration/ -v --tb=short

# Run contract tests (before merging an interface change)
pytest riar/tests/test_riar_contract.py -v
pytest agents/tests/test_agent_contract.py -v
```

### RIAR Testing

```bash
# Run RIAR pipeline manually
python -c "
from riar.pipeline import RIARPipeline
from backend.app.models.shared_models import Turn

p = RIARPipeline(vector_store=None, llm_client=None)
result = p.run('How do I apply for admission?', [], 'en')
print(result)
"
```

---

*This is a living document. Update it when processes change. Never let it go stale.*
*Last updated: June 2026 by Haseeb*
