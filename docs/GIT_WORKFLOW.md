# GIT_WORKFLOW.md
## VidyaSahayak — Git Workflow & Branching Strategy
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Haseeb (Project Lead)

---

## Branch Model

We use a **GitFlow-inspired model** adapted for a 3-person academic research team.

```
main
 └── develop
       ├── feature/haseeb/riar-pipeline
       ├── feature/harsha/speech-pipeline
       ├── feature/gowtham/knowledge-ingestion
       └── hotfix/fix-session-crash
```

---

## Branch Reference

### `main`
- **Purpose:** Production-ready, demo-ready code only.
- **Who can merge to:** Any 2 team members via PR approval.
- **When to merge:** Only at milestones (Demo Freeze, Final Submission).
- **Protected:** Yes — direct push is blocked. PRs only.
- **Rule:** Code on `main` must always run without errors.

### `develop`
- **Purpose:** Integration branch. Latest working code from all modules.
- **Who can merge to:** Any team member after one PR approval.
- **When to merge:** At least every Friday. More frequent is better.
- **Protected:** Yes — direct push is blocked. PRs only.
- **Rule:** `develop` should always be in a runnable state. If your code breaks develop, fix it same day.

### `feature/*`
- **Purpose:** Individual feature or module development.
- **Naming convention:** `feature/<owner>/<short-description>`
  ```
  feature/haseeb/riar-ambiguity-classifier
  feature/harsha/websocket-session-handler
  feature/gowtham/admissions-knowledge-base
  feature/haseeb/avatar-state-machine
  feature/harsha/whisper-asr-service
  ```
- **Lifetime:** Created when work starts. Deleted after merge to `develop`.
- **Base branch:** Always branch from `develop`.
- **Merge target:** Always merge back to `develop`.

### `hotfix/*`
- **Purpose:** Critical bug fixes on `main` (demo breaking issues only).
- **Naming:** `hotfix/<short-description>`
  ```
  hotfix/fix-session-memory-leak
  hotfix/fix-avatar-crash-on-reconnect
  ```
- **Process:** Branch from `main` → fix → PR to `main` AND `develop`.
- **Requires:** Immediate team notification in group chat.

### `research/*`
- **Purpose:** Experimental research code not ready for integration.
- **Naming:** `research/haseeb/<experiment-name>`
- **Note:** Does NOT need PR approval. For exploration only.

---

## Commit Message Convention

Follow **Conventional Commits** format:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | Use for |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only changes |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build scripts, CI, config files |
| `research` | Experimental / research code |
| `perf` | Performance improvements |

### Scopes

| Scope | Module |
|---|---|
| `detection` | Person detection |
| `asr` | Speech recognition |
| `tts` | Text-to-speech |
| `riar` | RIAR framework |
| `rag` | RAG pipeline |
| `agents` | Domain agents |
| `kb` | Knowledge base |
| `session` | Session management |
| `avatar` | Avatar layer |
| `api` | API routes |
| `ws` | WebSocket handlers |
| `eval` | Evaluation |
| `db` | Database |
| `ci` | CI/CD |
| `docs` | Documentation |

### Examples

```bash
feat(riar): implement ambiguity classification using zero-shot LLM
fix(session): resolve Redis connection timeout on idle sessions
docs(api): add clarification endpoint schema to API_CONTRACT.md
test(riar): add unit tests for CONTEXTUAL ambiguity detection
feat(kb): ingest admissions documents into ChromaDB
refactor(agents): extract base class from domain agent implementations
chore(ci): add GitHub Actions workflow for backend tests
research(riar): experiment with BERT-based ambiguity scorer
```

---

## Pull Request Process

### PR Rules

1. **One PR per feature.** Don't combine unrelated changes.
2. **Maximum 400 lines changed per PR.** Break large features into smaller PRs.
3. **Must include tests** for any new logic (unless pure documentation).
4. **Self-review first** — read your own diff before requesting review.
5. **No draft PRs merged** — only ready-for-review PRs.

### PR Title Format

```
[scope] Short description of what this PR does
```

Examples:
```
[riar] Add ambiguity detection scoring with probe retrieval
[speech] Integrate Whisper large-v3 for multilingual ASR
[kb] Ingest and index admissions knowledge domain
[api] Add /detect endpoint with session creation logic
```

### PR Description Template

*(Saved in `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`)*

```markdown
## Summary
<!-- What does this PR do? Why? -->

## Changes
<!-- List key files changed and what changed -->
- `riar/classifiers/ambiguity_classifier.py` — Implements zero-shot ambiguity classification
- `riar/tests/test_ambiguity_classifier.py` — 12 test cases covering all ambiguity types

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] Research experiment

## Testing
<!-- How did you test this? -->
- [ ] Unit tests pass (`pytest riar/tests/`)
- [ ] Manual test performed (describe)
- [ ] Integration test (describe)

## API Contract Impact
- [ ] No API changes
- [ ] API changes (must update API_CONTRACT.md)

## Checklist
- [ ] Code follows project conventions
- [ ] Self-reviewed
- [ ] Tests added
- [ ] Documentation updated if needed
- [ ] No print statements / debug code left in
```

### Review Process

1. Author opens PR with description and assigns reviewer(s).
2. **Reviewer has 24 hours** to review or flag that they need more time.
3. Reviewer must:
   - Read the diff
   - Leave specific comments (not just "LGTM")
   - Approve or request changes
4. Author responds to all review comments before re-requesting review.
5. **One approval required** to merge to `develop`.
6. **Two approvals required** to merge to `main`.

### Review Comment Labels

```
[blocking]    Must be fixed before merge
[suggestion]  Optional improvement
[question]    Needs clarification
[nitpick]     Minor style issue, author's discretion
[praise]      Positive feedback
```

---

## Merge Strategy

| Target Branch | Strategy | Notes |
|---|---|---|
| `develop` | **Squash and Merge** | One clean commit per feature |
| `main` | **Merge Commit** | Preserve history of what went in |
| `hotfix/*` | **Merge Commit** | Preserve fix history |

**Never use `git push --force` on `develop` or `main`.**

---

## Daily Development Workflow

```bash
# Start of day — sync with latest
git checkout develop
git pull origin develop

# Create or switch to your feature branch
git checkout -b feature/haseeb/riar-probe-retrieval
# OR
git checkout feature/haseeb/riar-probe-retrieval

# Work, commit often
git add riar/retrievers/probe_retriever.py
git commit -m "feat(riar): implement probe retrieval with top-10 chunks"

# Before pushing — sync with develop to catch conflicts early
git fetch origin develop
git rebase origin/develop

# Push your branch
git push origin feature/haseeb/riar-probe-retrieval

# End of day — ensure your branch is pushed
git push origin feature/haseeb/riar-probe-retrieval
```

---

## Weekly Integration Cadence

| Day | Action |
|---|---|
| Monday | Sync meeting — review what's being integrated this week |
| Wednesday | Mid-week sync — raise blockers. Partial integration PR if ready. |
| Friday | All feature PRs for the week merged to `develop` by EOD |
| Friday | Run integration tests on `develop` as a team |

**Rule:** Never leave feature branches unmerged for more than 5 days. Stale branches create integration debt.

---

## Handling Conflicts

1. **Rebase, don't merge** when syncing your feature branch with `develop`.
2. If conflict is in a file you don't own, contact the owner.
3. Never resolve conflicts in someone else's core module without discussing first.
4. If conflicts are complex, pair-resolve in a shared screen session.

---

## Tags and Releases

```bash
# Tag milestones on main
git tag -a v0.1.0-skeleton -m "Milestone 1: Skeleton Demo"
git tag -a v0.2.0-voice -m "Milestone 2: Voice Pipeline"
git tag -a v0.3.0-riar -m "Milestone 3: RIAR Prototype"
git tag -a v1.0.0-demo -m "Milestone 6: Demo Freeze"
git push origin --tags
```

---

## Protected Branch Configuration

Configure in GitHub Settings → Branches:

**For `main`:**
- [x] Require a pull request before merging
- [x] Require 2 approvals
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require status checks to pass before merging (CI tests)
- [x] Do not allow bypassing the above settings

**For `develop`:**
- [x] Require a pull request before merging
- [x] Require 1 approval
- [x] Require status checks to pass before merging (CI tests)
