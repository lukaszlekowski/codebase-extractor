# RPI Stages — Prompts + Outputs (Thou Art)

This file defines the standard **Research → Plan → Implement** workflow.
Goal: predictable artifacts, clean handoffs, and less manual copy/paste work.

## Golden rules
- Only **one** system edits code (Claude Code + GLM 4.7 during Implement).
- Research and Plan are **write-only**: they produce docs, not code changes.
- Every plan must include: phases, acceptance criteria, and verification commands.
- Implement runs verification after each phase and updates plan checkboxes.

---

## Stage 1 — Research (R)

### Purpose
Facts-only understanding of current code + constraints, and capture unknowns.

### Inputs
- Feature topic (1 line).
- Repo map (`tree -L 3`), plus 5–20 key files pasted or summarized.
- Any observed current behavior.

### Output file
Create: `docs/1_research/YYYY-MM-DD-HHmm-<topic>.md`

### Required sections in the output
- Goal
- Current behavior (facts only)
- Key files / directories
- Data flow (today)
- Constraints
- Options discovered (no decision yet)
- Unknowns / questions
- References

### Prompt (copy/paste)
> You are producing a **facts-only Research document** for an RPI workflow.
> Output must be a single Markdown document with the following sections:
> Goal; Current behavior (facts only); Key files/directories; Data flow (today);
> Constraints; Options discovered (no decision yet); Unknowns/questions; References.
>
> Rules:
> - Do NOT propose a solution.
> - Do NOT write code.
> - If information is missing, list it under Unknowns/questions.
>
> Topic: <TOPIC>
> Repo map: <PASTE tree -L 3>
> Key files/snippets: <PASTE>
> Notes/observations: <PASTE>

---

## Stage 2 — Plan (P)

### Purpose
Turn research + desired feature into an executable, phased implementation contract.

### Inputs
- Research doc from Stage 1.
- Feature request / PRD excerpt (what you want).
- Constraints: scope, timeline, non-goals.

### Output file
Create: `docs/2_plans/YYYY-MM-DD-HHmm-<feature>.md`

### Required sections in the output
- Summary
- Clarifying questions (max 5)
- Acceptance criteria (“done means” checklist)
- Verification commands (Flutter)
- Plan of record (phases with checkboxes)
- Risks & mitigations
- Notes / Deviations

### Prompt (copy/paste)
> You are producing an RPI **Plan document**.
>
> First: ask up to **5 clarifying questions** ONLY if needed.
> Then: output a complete plan in Markdown with:
> Summary; Acceptance criteria checklist; Verification commands;
> Phases (0..N) with checkboxes; Risks & mitigations.
>
> Requirements:
> - Each phase must list: objective, files to touch (if known), tests to add/update,
>   and how to verify.
> - Prefer small phases that can be committed independently.
>
> Research doc:
> <PASTE docs/1_research/...md>
>
> Feature request / spec excerpt:
> <PASTE>

---

## Stage 3 — Implement (I) — Claude Code + GLM 4.7

### Purpose
Execute the plan phase-by-phase, run verification each phase, and keep repo consistent.

### Inputs
- Path to the plan file produced in Stage 2.

### Output updates
- Modify code + tests.
- Update the plan file checkboxes as phases complete.
- Add notes to “Notes / Deviations” if the plan changes.

### Implement command prompt (copy/paste into Claude Code)
> Follow this plan **exactly phase-by-phase**: `<PATH_TO_PLAN_FILE>`.
>
> Rules:
> - Start with Phase 0. After each phase, run the plan’s verification commands.
> - Fix failures before proceeding.
> - Tick completed checkboxes in the plan file.
> - If the plan conflicts with the codebase reality, STOP and propose a minimal plan patch.
> - Keep changes incremental and commit-ready.
> - Add beginner-friendly comments to new/modified code where logic is non-obvious (per AI_GUIDE).
> - Before generating code, check the PLAN against the provided FILE TREE. If the plan references files that do not exist in the tree, STOP and ask for the file creation step.

---

## Optional Stage 4 — Review (R2)

### Purpose
Independent review of diff + tests + edge cases.

### Inputs
- Git diff/PR summary.
- Any failing output (tests/analyze/build logs).

### Output
- A bullet list of issues, each with severity and a concrete fix suggestion.

### Prompt (copy/paste)
> Review the following changes as a strict code reviewer.
> Output: a bullet list of issues grouped by severity (High/Med/Low).
> For each issue: explain impact + exact fix suggestion.
>
> Diff:
> <PASTE>
>
> Test/analyze output:
> <PASTE>

