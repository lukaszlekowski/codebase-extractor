# CLAUDE.md — Codebase Extractor (AI Collaboration Guide)

This file tells Claude Code (and other coding agents) how to work in this repository.

## Project overview

**Codebase Extractor** is a Python CLI tool that scans a project directory and consolidates relevant source code into structured Markdown files (one per selected folder, plus optional root files).

The tool supports:

- Interactive wizard mode (Questionary prompts).
- Fully non-interactive automation via CLI flags (`--mode`, `--select-folders`, `--select-root`, etc.).
- Filtering rules for excluded directories, excluded filenames, allowed filenames, allowed extensions, and an optional “exclude files larger than 1MB” setting.

## Documentation system (RPI)

We use an RPI-style workflow:

- Research outputs live in `docs/1_research/` (date-stamped). (Create if missing.)
- Plans live in `docs/2_plans/` (date-stamped). (Create if missing.)
- Keep research factual; keep plans phase-based and checkable.

## Workflow requirements (non-negotiable)

1. **Plan-first for multi-file changes**
   - If a change touches multiple files or changes behavior, you must create or update a plan document before implementing.

2. **Phase-by-phase implementation**
   - Implement exactly one phase at a time.
   - After each phase: run verification commands and report results.
   - Do not skip ahead “because it’s easy.”

3. **Small, reviewable commits**
   - Keep commits scoped to one phase or one coherent change.
   - Avoid sweeping refactors unless explicitly approved.

4. **No unnecessary dependency changes**
   - Adding new dependencies requires a brief justification and approval first.

## Current architecture (where to look)

Core modules:

- `src/codebaseextractor/mainlogic.py`: the CLI entrypoint/orchestration, prompt flow, and the extraction loop.
- `src/codebaseextractor/filehandler.py`: folder-choice generation for the wizard, filtering, extraction, and markdown output writing.
- `src/codebaseextractor/config.py`: default allow/deny lists, extension-to-language map, thresholds.
- `src/codebaseextractor/cli.py`: argument parsing (interactive vs automated flags).
- `src/codebaseextractor/ui.py`: banner/instructions output for the wizard.

Important behavior to preserve:

- “Specific selection” wizard builds a visual tree list and supports a ROOT sentinel option for “root files only.”
- Non-interactive mode must remain stable for automation.

## Coding standards

- Prefer modifying existing functions/modules over replacing them wholesale.
- Keep changes backwards-compatible unless the plan explicitly calls out breaking changes.
- Keep logging behavior consistent (the project uses structured logging + `termcolor` for emphasis).

## Running the tool for testing

To run the tool (for testing or development), use the venv:

```bash
./venv/bin/python -m src.codebase_extractor.main_logic [args]
```

## Verification (run as relevant after each phase)

At minimum, verify:

- Non-interactive path still works:
  - `codebase-extractor --dry-run --mode everything`
- Interactive wizard still works (manual):
  - `codebase-extractor` and step through prompts.

If a phase touches filtering/extraction, also verify output structure:

- Output directory behavior remains consistent (`CODEBASEEXTRACTS` default, customizable via `--output-dir`).
- YAML header includes expected metadata fields (run reference, timestamp, folder name, file/char/word counts).

## Feature in progress: Textual TUI + progress bar

We are adding an **optional** Textual tabbed UI (Settings / Extensions / Tree) with a per-folder/root progress bar.

Key constraints:

- Keep the current Questionary wizard as a fallback (it works well in small terminals).
- Progress can be per-folder/root first (no per-file progress refactor initially).
- Non-interactive mode stays as-is.

Implementation guidance:

- Default behavior should remain the wizard unless a `--tui` flag is provided (safe rollout).
- Reuse existing filtering and extraction functions from `filehandler.py` to avoid regressions.

## How Claude should collaborate

When asked to implement a feature:

1. Identify which RPI docs apply (research/plan). If missing, draft them first.
2. Propose the next _single phase_ you will implement and the exact files you expect to touch.
3. Implement that phase only.
4. Run verification commands and report outcomes + next phase suggestion.

If anything is ambiguous (e.g., UX, defaults, config file format), stop and ask a question rather than guessing.
