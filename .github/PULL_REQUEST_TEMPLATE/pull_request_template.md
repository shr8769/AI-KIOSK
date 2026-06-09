## Summary
<!-- 
  What does this PR do? Write 2-3 sentences.
  Reference the issue: "Closes #N" or "Part of #N"
-->

Closes #

## What Changed
<!-- List the key files modified and what changed in each -->

| File | Change |
|---|---|
| `riar/pipeline.py` | Added ambiguity detection scoring |
| `riar/tests/test_pipeline.py` | 8 new tests |

## Type of Change
- [ ] 🚀 New feature
- [ ] 🐛 Bug fix
- [ ] ♻️ Refactor (no behavior change)
- [ ] 📚 Documentation only
- [ ] 🔬 Research / experimental
- [ ] 🔧 CI / build / config

## Module Affected
<!-- Which module does this touch? -->
- [ ] detection
- [ ] backend / api
- [ ] riar
- [ ] knowledge / kb
- [ ] agents
- [ ] avatar
- [ ] frontend
- [ ] evaluation
- [ ] database
- [ ] docs

## Testing
<!-- How was this tested? -->

```bash
# Command to run the tests
pytest riar/tests/ -v
```

- [ ] Unit tests pass
- [ ] Manual testing performed (describe below)
- [ ] Integration tests pass (`pytest tests/integration/`)

**Manual test description:**
> <!-- What did you manually test? What was the result? -->

## API Contract Impact
- [ ] No API changes
- [ ] API schema changed → `API_CONTRACT.md` updated in this PR
- [ ] New endpoint added → `API_CONTRACT.md` updated in this PR

## Interface Impact
- [ ] No interface changes (safe for other modules)
- [ ] RIAR interface changed → discussed with Harsha
- [ ] Agent interface changed → discussed with Harsha
- [ ] Detection interface changed → discussed with Harsha

## PR Checklist
- [ ] Code follows project style (no unused imports, no print statements)
- [ ] Self-reviewed (read your own diff before submitting)
- [ ] Tests added or updated for new logic
- [ ] Documentation updated if needed
- [ ] Branch is up-to-date with `develop`
- [ ] No secrets or API keys in code

## Screenshots / Evidence
<!-- If this is a UI change or has visual output, add a screenshot or terminal output -->

---

*Reviewer: Please use comment labels — `[blocking]`, `[suggestion]`, `[question]`, `[nitpick]`, `[praise]`*
