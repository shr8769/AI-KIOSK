# RISK_MANAGEMENT.md
## VidyaSahayak — Risk Register & Mitigation Plan
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)
**Review Frequency:** Updated every Monday during Weekly Sync

---

## Risk Matrix

| ID | Risk | Category | Probability | Severity | Score | Status |
|---|---|---|---|---|---|---|
| R01 | Whisper latency >3s for Kannada/Hindi | Technical | Medium | High | 🔴 HIGH | Open |
| R02 | University documents unavailable or poorly structured | Data | Medium | High | 🔴 HIGH | Open |
| R03 | Avatar lip sync integration failure | Technical | High | Medium | 🟡 MEDIUM | Open |
| R04 | RIAR classification quality below F1=0.75 | Research | Low | High | 🟡 MEDIUM | Open |
| R05 | Integration conflicts between modules in Week 5 | Process | Medium | High | 🔴 HIGH | Open |
| R06 | Timeline overrun — Week 5 integration takes 2 weeks | Timeline | Medium | High | 🔴 HIGH | Open |
| R07 | GPU hardware unavailable on kiosk machine | Hardware | Low | High | 🟡 MEDIUM | Open |
| R08 | LLM API costs exceed budget | Financial | Medium | Medium | 🟡 MEDIUM | Open |
| R09 | Poor retrieval quality degrading answer accuracy | Technical | Medium | High | 🔴 HIGH | Open |
| R10 | ChromaDB performance degradation on large KB | Technical | Low | Medium | 🟢 LOW | Open |
| R11 | Camera/microphone hardware failure at demo | Hardware | Low | High | 🟡 MEDIUM | Open |
| R12 | Kannada/Hindi TTS voice quality unacceptable | Technical | Medium | Medium | 🟡 MEDIUM | Open |
| R13 | Scope creep adding unplanned features | Process | High | Medium | 🟡 MEDIUM | Open |
| R14 | Team member unavailability (illness, exams) | People | Low | High | 🟡 MEDIUM | Open |
| R15 | Research paper contribution not novel enough | Research | Low | High | 🟡 MEDIUM | Open |

---

## Detailed Risk Register

---

### R01 — Whisper Latency >3s for Kannada/Hindi
**Category:** Technical
**Probability:** Medium | **Severity:** High | **Score:** 🔴 HIGH
**Owner:** Harsha

**Description:**
OpenAI Whisper large-v3 provides the best multilingual accuracy but is computationally expensive. On consumer-grade GPUs (e.g., RTX 3060), transcription of 10-second Kannada audio may take 3-5 seconds, breaking our <3s total E2E target.

**Mitigation Strategies:**
1. **Primary:** Use Whisper `medium` model for real-time use, `large-v3` for offline evaluation. Benchmark during Week 2.
2. **Secondary:** Implement faster-whisper (CTranslate2-based) for 2-4x speedup with same accuracy.
3. **Tertiary:** Use streaming/chunked ASR — process audio in 3-second segments while user is still speaking.
4. **Fallback:** Accept slightly higher E2E latency (4s) for Kannada/Hindi and communicate this in the research paper as a system limitation.

**Detection Signal:** If Week 2 benchmarks show latency >2s median for Kannada audio, escalate immediately.

**Contingency Trigger:** If latency > 2.5s on Week 2 hardware tests → switch to faster-whisper immediately.

---

### R02 — University Documents Unavailable or Poorly Structured
**Category:** Data
**Probability:** Medium | **Severity:** High | **Score:** 🔴 HIGH
**Owner:** Gowtham

**Description:**
The knowledge base quality directly determines answer quality. PES University may not provide official documents, or provided documents may be in poor formats (scanned PDFs, tables in images, etc.).

**Mitigation Strategies:**
1. **Immediate (Week 1):** Gowtham starts with publicly available information from PES University's official website via web scraping.
2. **Parallel:** Contact university admin/faculty advisor to formally request official documents (brochures, course catalogs, placement reports).
3. **Manual entry:** For critical knowledge gaps, write structured markdown files manually based on official website content.
4. **Scope reduction:** If specific domains are data-poor, reduce their scope in the demo and paper rather than hallucinating quality.

**Detection Signal:** By end of Week 1, Gowtham should have at least 15 documents. If <15 documents by Wednesday of Week 1, trigger escalation.

---

### R03 — Avatar Lip Sync Integration Failure
**Category:** Technical
**Probability:** High | **Severity:** Medium | **Score:** 🟡 MEDIUM
**Owner:** Haseeb

**Description:**
MuseTalk requires real-time audio-to-video generation. On local hardware, this may not achieve acceptable latency. Integration with the rest of the system may be complex.

**Mitigation Strategies:**
1. **Tiered approach:** Define 3 avatar quality tiers:
   - **Tier 1 (minimum viable):** Static avatar image with animated mouth overlay
   - **Tier 2 (target):** Pre-rendered lip sync segments triggered by phoneme detection
   - **Tier 3 (ideal):** Real-time MuseTalk lip sync
2. Start with Tier 1 in Week 1. Attempt Tier 3 in Week 5. Fall back to Tier 2 if Tier 3 fails.
3. Keep avatar system decoupled from the rest of the pipeline — the kiosk works fine without lip sync.

**Detection Signal:** If Tier 3 (MuseTalk real-time) is not working by end of Week 4 → commit to Tier 2 for demo.

---

### R04 — RIAR Classification Quality Below F1=0.75
**Category:** Research
**Probability:** Low | **Severity:** High | **Score:** 🟡 MEDIUM
**Owner:** Haseeb

**Description:**
The RIAR framework's ambiguity classifier may not achieve the required F1 score, weakening the research contribution.

**Mitigation Strategies:**
1. **Approach diversity:** Implement 3 different classification approaches in parallel (zero-shot LLM prompting, fine-tuned classifier, rule-based hybrid). Select the best by Week 3 evaluation.
2. **Training data:** Gowtham creates high-quality, labeled training examples for all 4 ambiguity types from Week 1.
3. **Fallback research angle:** If classification is difficult, reframe the contribution as "detection + routing" (binary ambiguous/clear) with qualitative analysis of types.
4. **Ablation study:** Compare RIAR vs. no-RIAR system — even if absolute F1 is moderate, improvement over baseline may be significant enough for publication.

---

### R05 — Integration Conflicts in Week 5
**Category:** Process
**Probability:** Medium | **Severity:** High | **Score:** 🔴 HIGH
**Owner:** Harsha

**Description:**
When all three modules come together in Week 5, interface mismatches, assumption differences, and unexpected dependencies may cause significant delays.

**Mitigation Strategies:**
1. **Prevention:** Follow INTEGRATION_STRATEGY.md strictly. Contract tests must pass before any integration.
2. **Early integration:** Merge partial implementations every Friday (not just Week 5). Catch conflicts early.
3. **Mock-first:** All modules must work with mocks of others from Day 1. The switch to real modules in Week 5 should be straightforward.
4. **Dedicated integration day:** Set aside Wednesday of Week 5 as an "integration day" — all three work together in real-time (video call + screen share).
5. **Buffer:** Week 5 has no new feature development. 100% of time is integration.

---

### R06 — Timeline Overrun (Week 5 Integration Takes 2 Weeks)
**Category:** Timeline
**Probability:** Medium | **Severity:** High | **Score:** 🔴 HIGH
**Owner:** Haseeb (Project Lead)

**Description:**
Integration typically takes longer than estimated, especially in research projects where module interfaces evolve.

**Mitigation Strategies:**
1. **Ruthless scope reduction:** If integration is delayed, reduce demo scope (e.g., demo only 3 domains instead of 6, English only instead of 3 languages).
2. **Parallel tracks:** Evaluation (Gowtham) and research paper writing (Haseeb) can progress independently even if integration is delayed.
3. **Demo-critical features first:** Prioritize the integration of person detection → ASR → RIAR → one domain agent → TTS as the minimum viable demo.
4. **Time box:** If a specific integration issue takes >4 hours without resolution, escalate immediately. Don't let one blocker consume a day.

**Contingency Plan:**
| Trigger | Response |
|---|---|
| Integration not working by Wednesday of Week 5 | Emergency sync, reduce scope, focus on demo-critical path |
| Integration not working by Friday of Week 5 | Push demo freeze to Week 6 midpoint, reduce evaluation scope |

---

### R07 — GPU Hardware Unavailable
**Category:** Hardware
**Probability:** Low | **Severity:** High | **Score:** 🟡 MEDIUM
**Owner:** Harsha

**Description:**
Whisper, YOLOv8, and MuseTalk all benefit significantly from GPU acceleration. If the kiosk machine lacks a GPU or CUDA setup fails, performance will be unacceptable.

**Mitigation Strategies:**
1. **Immediate:** Verify CUDA availability on kiosk machine in Week 1. Don't wait until Week 5.
2. **Cloud fallback:** If no local GPU, use OpenAI API for Whisper (cloud ASR) and LLM. More expensive but functional.
3. **Model downsizing:** Use Whisper `base` or `small` on CPU if needed. Accept lower accuracy.
4. **Quantized models:** Use int8-quantized Whisper and YOLOv8 models for CPU-acceptable performance.

---

### R08 — LLM API Costs Exceed Budget
**Category:** Financial
**Probability:** Medium | **Severity:** Medium | **Score:** 🟡 MEDIUM
**Owner:** Harsha (budget tracking)

**Description:**
GPT-4o costs approximately $5/1M input tokens and $15/1M output tokens. A 500-query evaluation run with 1000 tokens per query = ~$5-10. This is manageable but cumulative costs across development, testing, and evaluation may add up.

**Mitigation Strategies:**
1. Use `gpt-4o-mini` during development and testing ($0.15/1M input).
2. Switch to `gpt-4o` only for evaluation runs and demo.
3. Explore local LLM (Llama 3 8B via Ollama) as fallback for development — no API cost.
4. Track token usage weekly. If projected to exceed budget, optimize prompts or switch to local model.

**Budget estimate:** $30-50 for the entire project (manageable for a university research grant).

---

### R09 — Poor Retrieval Quality Degrading Answer Accuracy
**Category:** Technical
**Probability:** Medium | **Severity:** High | **Score:** 🔴 HIGH
**Owner:** Gowtham

**Description:**
If the vector store returns irrelevant chunks, the LLM will hallucinate or give wrong answers regardless of how good the generation model is.

**Mitigation Strategies:**
1. Invest in chunking strategy early (Week 1-2). Test chunk sizes 256, 512, 1024 tokens.
2. Enrich metadata — add domain, section, keywords, date to every chunk.
3. Use hybrid search (keyword + semantic) via ChromaDB's `where` filters for domain-scoped retrieval.
4. Implement re-ranking (cross-encoder) on top-10 retrieved chunks before passing top-5 to LLM.
5. Run retrieval evaluation (Precision@5, Recall@5, MRR) weekly from Week 2 onward.

---

### R11 — Camera/Microphone Hardware Failure at Demo
**Category:** Hardware
**Probability:** Low | **Severity:** High | **Score:** 🟡 MEDIUM
**Owner:** Haseeb

**Mitigation Strategies:**
1. Have backup hardware (second webcam, backup microphone) on demo day.
2. Record a full demo video in Week 6 as fallback for presentation.
3. Test hardware at demo venue 24 hours before demo.
4. All critical components have software mock alternatives (mock camera, pre-recorded audio).

---

### R13 — Scope Creep
**Category:** Process
**Probability:** High | **Severity:** Medium | **Score:** 🟡 MEDIUM
**Owner:** Haseeb (Project Lead)

**Description:**
Research projects are particularly susceptible to "one more feature" thinking, especially when demos are approaching.

**Mitigation Strategies:**
1. **Haseeb has final say on scope.** Any new feature must be explicitly accepted into scope by Haseeb.
2. Maintain a "Parking Lot" list in `docs/PARKING_LOT.md` for ideas that are explicitly deferred.
3. Apply the test: "Does this feature directly impact the research contribution or demo quality?" If no → parking lot.
4. Feature freeze at end of Week 6 (Demo Freeze milestone). After that: bug fixes only.

---

## Risk Update Protocol

At every Monday sync:
1. Review the risk register (5 minutes)
2. Update probability/severity if anything changed
3. Mark resolved risks as ✅ Resolved
4. Add new risks discovered during the previous week
5. Update the status column in this file and commit

---

## Risk History Log

| Date | Risk | Change | Action Taken |
|---|---|---|---|
| 2026-06-09 | All | Initial risk register created | — |
