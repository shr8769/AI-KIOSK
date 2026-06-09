# PROJECT_SCOPE.md
## VidyaSahayak — Project Scope Document
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

---

## 1. Problem Statement

PES University has thousands of students, faculty members, and daily visitors who frequently need information about admissions, academics, campus navigation, research activities, placements, and student services. Currently this information is:

- **Fragmented** across websites, notice boards, departments, and WhatsApp groups
- **Inaccessible** in regional languages (Kannada, Hindi) to many users
- **Unavailable** outside office hours
- **Slow** — queries require human staff intervention

There is no single, intelligent, 24/7 accessible system that can handle the full breadth of university queries in multiple languages, with the ability to resolve ambiguous or incomplete questions intelligently.

### Research Gap

Existing conversational AI systems deployed in academic environments suffer from:

1. **Ambiguity blindness** — They attempt to answer unclear queries without detecting or resolving ambiguity, leading to hallucinated or irrelevant responses.
2. **Language rigidity** — Most systems operate only in English, excluding a large segment of users.
3. **Flat retrieval** — They use single-pass RAG without domain-aware routing, degrading answer quality for complex multi-domain queries.

---

## 2. Objectives

### Primary Objectives

| # | Objective | Success Measure |
|---|---|---|
| O1 | Deploy functional AI kiosk at PES University | Kiosk operates continuously during pilot |
| O2 | Support multilingual voice interaction | EN, KN, HI with >85% ASR accuracy |
| O3 | Implement and validate RIAR framework | Ambiguity classification F1 > 0.80 |
| O4 | Achieve accurate knowledge retrieval | RAG precision@5 > 0.75 |
| O5 | Enable campus navigation assistance | Navigation accuracy > 90% for mapped locations |
| O6 | Publish research findings | Conference/journal paper submission |

### Secondary Objectives

| # | Objective |
|---|---|
| S1 | Maintain <3 second end-to-end response latency |
| S2 | Achieve >80% user satisfaction in pilot survey |
| S3 | Build reusable RIAR library publishable as open-source |
| S4 | Create evaluation dataset of 500+ university queries |

---

## 3. Success Criteria

### Minimum Viable Success (Must Achieve)

- [ ] System operates without crash for 4+ continuous hours
- [ ] English voice interaction works end-to-end
- [ ] RIAR detects ambiguity with F1 > 0.75
- [ ] At least 3 knowledge domains functional (Admissions, Academics, Navigation)
- [ ] Pilot with 20 users conducted and documented

### Target Success (Should Achieve)

- [ ] All 3 languages functional
- [ ] All 6 knowledge domains populated and queryable
- [ ] RIAR classification F1 > 0.80
- [ ] End-to-end latency <3 seconds
- [ ] 50+ user pilot survey conducted

### Stretch Success (Nice to Have)

- [ ] Real-time avatar lip sync working
- [ ] Session memory across multi-turn conversations
- [ ] Research paper submitted to venue

---

## 4. Deliverables

| # | Deliverable | Owner | Target Week |
|---|---|---|---|
| D1 | Working codebase on GitHub | All | Week 1 |
| D2 | Person detection module | Haseeb | Week 2 |
| D3 | Speech pipeline (ASR + TTS) | Harsha | Week 2 |
| D4 | Knowledge base (3 domains) | Gowtham | Week 3 |
| D5 | RIAR prototype | Haseeb | Week 4 |
| D6 | Multi-agent RAG system | Harsha + Gowtham | Week 5 |
| D7 | Full integrated system | All | Week 6 |
| D8 | Evaluation report | Gowtham | Week 7 |
| D9 | Research paper draft | Haseeb | Week 7 |
| D10 | Final demo video | All | Week 7 |

---

## 5. In Scope

- Person detection via camera
- Wake trigger → voice interaction flow
- ASR in English, Kannada, Hindi
- RIAR ambiguity resolution pipeline
- Multi-agent architecture with coordinator
- RAG over PES University knowledge base (6 domains)
- Campus navigation assistance
- Text-to-speech response generation
- AI avatar display and basic lip sync
- Session context across multi-turn dialogue
- SQLite/Postgres session logging
- Evaluation framework and metrics
- Research paper

---

## 6. Non-Goals (Explicitly Out of Scope)

| Non-Goal | Reason |
|---|---|
| Mobile app | Out of scope for kiosk project |
| Student authentication / login | Privacy concerns, not required for MVP |
| Real-time database integration with university SIS | Requires IT department cooperation beyond project timeline |
| Emotion recognition | Stretch research area, not in core contribution |
| Multi-kiosk deployment | Single pilot kiosk for research validation |
| External user data storage (cloud) | GDPR / data privacy — local only |
| Support for Tamil, Telugu, or other languages | Constrained to EN, KN, HI for quality depth |
| Video output beyond avatar display | Hardware limitation |
| Payment or form submission | Not applicable |

---

## 7. Assumptions

1. PES University will provide access to official documents, brochures, course catalogs, and navigation maps.
2. A physical kiosk hardware unit will be available by Week 4 for integration testing.
3. A camera (1080p minimum) is available and mountable.
4. Internet access is available at the kiosk location (for LLM API calls if needed).
5. A dedicated GPU (minimum 8GB VRAM) is available for Whisper and detection models.
6. Faculty advisor will provide weekly feedback during the evaluation phase.

---

## 8. Constraints

| Constraint | Impact |
|---|---|
| 7-week timeline | Aggressive — requires strict prioritization |
| 3-person team | No slack capacity for major scope creep |
| University data availability | KB quality depends on document access |
| Hardware (GPU) | Latency targets depend on GPU availability |
| Academic privacy | No PII collection from users |

---

## 9. Risks Summary

*(Full detail in [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md))*

| Risk | Severity | Probability |
|---|---|---|
| Whisper latency >3s for Kannada/Hindi | High | Medium |
| University documents unavailable or unstructured | High | Medium |
| Avatar lip sync integration delays | Medium | High |
| RIAR classification quality below target | High | Low |
| Integration conflicts between modules | Medium | Medium |
| Timeline overrun on Week 5 integration | High | Medium |

---

## 10. Stakeholders

| Stakeholder | Role | Engagement |
|---|---|---|
| Haseeb | Project Lead | Daily |
| Harsha | Engineering Lead | Daily |
| Gowtham | Knowledge Systems Lead | Daily |
| Faculty Advisor | Research Supervisor | Weekly review |
| PES University Admin | Document Provider | As needed |
| Conference Reviewers | Research Audience | Paper submission |
