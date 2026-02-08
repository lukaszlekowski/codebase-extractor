---
type: plan
status: ready     # draft | ready | implementing | blocked | done | archived
created: YYYY-MM-DD
feature: "<feature name>"
related_research: "docs/research/YYYY-MM-DD-HHmm-topic.md"
related_spec: "docs/specs/<optional>.md"
---

# Plan: <feature name>

## Summary
1–3 sentences describing what will change.

## Acceptance criteria ("done means")
- [ ] User-visible: ...
- [ ] Error states handled: ...
- [ ] Tests added/updated: ...
- [ ] No regressions: ...

## Verification commands (run each phase as relevant)
- `flutter analyze`
- `flutter test`
- `dart format .` (or `dart format --set-exit-if-changed .`)
- (Add platform builds when needed) `flutter build apk --debug` / `flutter build ios --debug`

## Plan of record (phases)
### Phase 0 — Prep
- [ ] Confirm baseline passes verification commands.
- [ ] Create/confirm feature branch.
- [ ] **Environment & Config:**
    - [ ] Base URL strategy defined (e.g., `Platform.isAndroid ? 'http://10.0.2.2:4000' : 'http://localhost:4000'`)?
    - [ ] Secrets/Keys required for this feature checked?
- Notes:

### Phase 1 — Data / API layer
- [ ] Task:
- [ ] Files:
- [ ] Tests:
- [ ] Verify:

### Phase 2 — UI + state
- [ ] Task:
- [ ] Files:
- [ ] Tests:
- [ ] Verify:

### Phase 3 — Edge cases + polish
- [ ] Loading/empty/error states
- [ ] Accessibility considerations (basic)
- [ ] Verify:


## Risks & mitigations
- Risk:
- Mitigation:

## Notes / Deviations
Track any plan changes (and why).
