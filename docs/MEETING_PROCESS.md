# MEETING_PROCESS.md
## VidyaSahayak — Meeting Process & Templates
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

---

## Meeting Cadence

| Meeting | Frequency | Duration | Participants | Format |
|---|---|---|---|---|
| Weekly Sync | Every Monday | 30 min | All 3 | Video call |
| Async Standup | Daily (Tue–Fri) | Text only | All 3 | Group chat |
| Integration Review | Every Friday | 20 min | All 3 | Video or in-person |
| Ad-hoc Pair Session | As needed | 45 min | 2 people | Screen share |

---

## Weekly Sync (Monday — 30 minutes)

### Purpose
Align on the week's priorities, unblock each other, review integration readiness.

### Agenda (Fixed)

```
00:00 — 05:00  Status from last week (each person: 1 min each)
05:00 — 15:00  This week's priorities (each person: 2 min each)
15:00 — 22:00  Blockers (open floor — raise blockers, assign resolution)
22:00 — 27:00  Integration review (What will be merged this week? Who reviews what?)
27:00 — 30:00  Risk check (any new risks this week?)
```

### Rules
- Meeting starts on time. If someone is late, we start without them.
- Every person must state their top 3 tasks for the week.
- Every blocker must have an owner and an expected resolution date.
- Meeting notes written during the meeting, committed to `meeting_notes/weekN/YYYY-MM-DD.md` by end of day.

---

## Weekly Meeting Notes Template

Save as: `meeting_notes/weekN/YYYY-MM-DD_weekly_sync.md`

```markdown
# Weekly Sync — [DATE]
**Attendees:** Haseeb, Harsha, Gowtham
**Facilitator:** Haseeb
**Notes by:** [Name]

---

## Status from Last Week

### Haseeb
- Completed: [What was finished]
- In Progress: [What is ongoing]
- Not completed: [What was planned but not done — and why]

### Harsha
- Completed:
- In Progress:
- Not completed:

### Gowtham
- Completed:
- In Progress:
- Not completed:

---

## This Week's Priorities

### Haseeb
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

### Harsha
1.
2.
3.

### Gowtham
1.
2.
3.

---

## Blockers

| Blocker | Who Raised | Impact | Owner | Resolution By |
|---|---|---|---|---|
| [Description] | [Name] | [High/Med/Low] | [Name] | [Date] |

---

## Integration Plan for This Week

| What will be merged | From | To | Who reviews | By when |
|---|---|---|---|---|
| [Feature name] | [feature branch] | develop | [Reviewer] | [Day] |

---

## Risk Check

| Risk | Status | Update |
|---|---|---|
| [Risk from risk register] | [Increased/Stable/Resolved] | [What changed] |

---

## Decisions Made

1. [Decision] — rationale: [why]
2.

---

## Action Items

| Action | Owner | Due |
|---|---|---|
| [Action] | [Name] | [Date] |

---

## Next Meeting
**Date:** [Next Monday]
**Focus:** [What this meeting will emphasize]
```

---

## Daily Async Standup (Tue–Fri)

Post in group chat by **10:00 AM** every day.

### Format

```
🔷 STANDUP — [Name] — [Date]

✅ DONE (yesterday):
- [What I completed]

🔜 TODAY:
- [What I'm working on today]

🚧 BLOCKERS:
- [Anything blocking me — or "None"]

🔗 NEEDS FROM TEAM:
- [Any dependency on another team member — or "None"]
```

### Example

```
🔷 STANDUP — Haseeb — June 10, 2026

✅ DONE (yesterday):
- Implemented probe retrieval (RIAR Step 1)
- Wrote 8 unit tests for probe retriever
- Reviewed Harsha's WebSocket PR

🔜 TODAY:
- Implement ambiguity detection scoring (RIAR Step 2)
- Start ambiguity classifier skeleton

🚧 BLOCKERS:
- None

🔗 NEEDS FROM TEAM:
- Harsha: Can you expose the ChromaDB client via dependency injection in `backend/app/core/dependencies.py`? Need it by tomorrow so RIAR can use it.
```

---

## Friday Integration Review (20 minutes)

### Purpose
Verify what was merged this week. Run integration tests together. Identify weekend risks.

### Agenda

```
00:00 — 05:00  What was merged this week? (Harsha reviews git log)
05:00 — 12:00  Run integration tests together (screen share)
12:00 — 17:00  Demo what's new (each person demos their week's work — 2 min each)
17:00 — 20:00  What's at risk heading into next week?
```

### Integration Review Template

Save as: `meeting_notes/weekN/YYYY-MM-DD_integration_review.md`

```markdown
# Integration Review — [DATE]

## Merged This Week

| PR | Author | Feature | Status |
|---|---|---|---|
| #[N] | [Name] | [Feature] | ✅ Merged / ⚠️ Pending |

## Integration Test Results

```bash
pytest tests/integration/ -v --tb=short
```

Result: [PASS ✅ / FAIL ❌]

Failures (if any):
- [Test name] — [Error] — Owner: [Name] — Fix by: [When]

## This Week's Demos
- Haseeb: [What was shown]
- Harsha: [What was shown]
- Gowtham: [What was shown]

## Risks Heading Into Next Week

| Risk | Severity | Mitigation |
|---|---|---|
| [Risk] | H/M/L | [Plan] |

## Next Week's Integration Target

By next Friday's integration review, the following should be merged:
- [Feature 1] — [Owner]
- [Feature 2] — [Owner]
```

---

## Ad-Hoc Pair Session Template

Save as: `meeting_notes/weekN/YYYY-MM-DD_pair_session_[topic].md`

```markdown
# Pair Session — [DATE]
**Participants:** [Names]
**Topic:** [What was worked on]
**Duration:** [Time]

## Problem Solved
[What issue or feature was addressed]

## Solution / Decision
[What was decided or implemented]

## Code Changes Made
- [File] — [What changed]

## Follow-up Actions
| Action | Owner | Due |
|---|---|---|
| [Action] | [Name] | [Date] |
```

---

## Escalation Protocol

| Situation | Action |
|---|---|
| One person blocked for >4 hours | Post in group chat, request pair session |
| Integration broken on `develop` | Alert team immediately, fix within 2 hours or revert |
| Scope creep proposed | Discuss in Monday sync, Haseeb decides in/out |
| Team disagreement on technical approach | Both options prototyped (time-boxed to 2 hours), team votes |
| Risk materializing | Update RISK_MANAGEMENT.md, raise in next sync |
| Hardware/infrastructure failure | Harsha leads resolution, others continue on unblocked tasks |
| Research direction change | Haseeb calls emergency sync within 24 hours |
