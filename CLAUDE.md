# CLAUDE.md — Codebase Extractor (AI Collaboration Guide)

This file tells Claude Code (and other coding agents) how to work in this repository.

## Project overview

**Codebase Extractor** is a Python CLI tool that scans a project directory and consolidates relevant source code into structured Markdown files (one per selected folder, plus optional root files).

The tool supports:

- Interactive wizard mode (Questionary prompts).
- Fully non-interactive automation via CLI flags (`--mode`, `--select-folders`, `--select-root`, etc.).
- Filtering rules for excluded directories, excluded filenames, allowed filenames, allowed extensions, and an optional "exclude files larger than 1MB" setting.

## Workflow & Protocols (Authoritative)

**CRITICAL:** Before starting any task, read **`docs/00_prompts/00-stages-rpi.md`**.

This directory contains the strict protocols for:
1.  **Stage Selection**: When to use Research vs Spec vs Plan.
2.  **Execution**: How to run the Implementation -> Review loop.
3.  **Handoff**: How to switch agents/models safely (`docs/00_prompts/50-handoff-model-switch.md`).

## Workflow requirements (non-negotiable)

1. **Plan-first for multi-file changes**
   - If a change touches multiple files or changes behavior, you must create or update a plan document before implementing.

2. **Phase-by-phase implementation**
   - Implement exactly one phase at a time.
   - After each phase: run verification commands and report results.
   - Do not skip ahead "because it’s easy."

3. **Small, reviewable commits**
   - Keep commits scoped to one phase or one coherent change.
   - Avoid sweeping refactors unless explicitly approved.

4. **No unnecessary dependency changes**
   - Adding new dependencies requires a brief justification and approval first.

## Template usage requirements

When creating or updating project docs, follow the stage guides in `docs/00_prompts/` to determine which templates are required.

Canonical templates:

- Research: `docs/10_research/_research-template.md`
- Plan: `docs/20_plans/_plan-template.md`
- MVP spec: `docs/15_specs/_mvp-template.md` (Optional; see `15-spec-stage.md` for skip logic)
- ADR: `docs/25_adr/_adr-template.md`

Required quality bar:

- Frontmatter keys use snake_case.
- Cross-doc links use canonical paths (`docs/10_research`, `docs/20_plans`, `docs/15_specs`, `docs/25_adr`).
- Plans must be decision-complete before implementation (no high-impact TBDs).
- Each phase in a plan must include executable verification commands and expected outcomes.

## Current architecture (where to look)

Core modules:

- `src/codebase_extractor/main_logic.py`: the CLI entrypoint/orchestration, prompt flow, and the extraction loop.
- `src/codebase_extractor/file_handler.py`: folder-choice generation for the wizard, filtering, extraction, and markdown output writing.
- `src/codebase_extractor/config.py`: default allow/deny lists, extension-to-language map, thresholds.
- `src/codebase_extractor/cli.py`: argument parsing (interactive vs automated flags).
- `src/codebase_extractor/ui.py`: banner/instructions output for the wizard.

Important behavior to preserve:

- "Specific selection" wizard builds a visual tree list and supports a ROOT sentinel option for "root files only."
- Non-interactive mode must remain stable for automation.

## Coding standards

- Prefer modifying existing functions/modules over replacing them wholesale.
- Keep changes backwards-compatible unless the plan explicitly calls out breaking changes.
- Keep logging behavior consistent (the project uses structured logging + `termcolor` for emphasis).

## Running the tool for testing

To run the tool (for testing or development), use the venv:

```bash
./venv/bin/python -m codebase_extractor.main_logic [args]
```

## Verification (run as relevant after each phase)

At minimum, verify:

- Non-interactive path still works:
  - `codebase-extractor --dry-run --mode everything`
- Interactive wizard still works (manual):
  - `codebase-extractor` and step through prompts.

If a phase touches filtering/extraction, also verify output structure:

- Output directory behavior remains consistent (`CODEBASE_EXTRACTS` default, customizable via `--output-dir`).
- YAML header includes expected metadata fields (run reference, timestamp, folder name, file/char/word counts).

**Closeout**: At the end of a task, you MUST update the status of all active Research/Plan/Spec docs (e.g., to `implemented` or `done`).

## Feature in progress: Textual TUI + progress bar

We are adding an **optional** Textual tabbed UI (Settings / Extensions / Tree) with a per-folder/root progress bar.

Key constraints:

- Keep the current Questionary wizard as a fallback (it works well in small terminals).
- Progress can be per-folder/root first (no per-file progress refactor initially).
- Non-interactive mode stays as-is.

Implementation guidance:

- Default behavior should remain the wizard unless a `--tui` flag is provided (safe rollout).
- Reuse existing filtering and extraction functions from `file_handler.py` to avoid regressions.

## How Claude should collaborate

When asked to implement a feature:

1.  **Read `docs/00_prompts/00-stages-rpi.md` first.**
2.  Follow the flow described there (Research -> Plan -> Implement -> Review).
3.  Use `50-handoff-model-switch.md` if you need to stop before completion.

If anything is ambiguous (e.g., UX, defaults, config file format), stop and ask a question rather than guessing.
