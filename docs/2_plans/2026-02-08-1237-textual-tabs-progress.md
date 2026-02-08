---
type: plan
status: draft
created: 2026-02-08
feature: Replace wizard prompts with Textual tabs + progress bar (wizard fallback retained)
relatedresearch: docs/research/2026-02-08-1237-textual-tabs-progress.md
relatedspec: docs/specs/optional.md
---

# Plan: Replace wizard prompts with Textual tabs + progress bar (wizard fallback retained)

## Summary

- User-visible: Add an optional Textual full-screen interface with tabs (Settings / Extensions / Tree) for configuring and selecting extraction targets.
- User-visible: Keep the existing Questionary wizard as a fallback for small terminal windows or users who prefer it.
- User-visible: Add a progress indicator that shows overall progress per folder/root unit during extraction.
- Error states handled: Permission errors and file read failures remain non-fatal (warn/log and continue), and Ctrl+C exits cleanly as today.
- No regressions: The underlying filtering and extraction output (YAML header fields, file inclusion rules, output directory behavior) remains consistent with current behavior for equivalent settings.

## Acceptance criteria (done means…)

- A user can run the tool and choose Textual UI or the wizard (explicit flag or documented fallback behavior), and both paths successfully complete extraction.
- The Textual UI provides three tabs:
  - Settings: controls for existing settings (at least exclude >1MB, root path, output directory, dry-run).
  - Extensions: include/exclude extension lists and group toggles (initially presets only is acceptable).
  - Tree: choose folders (and optionally root files) to extract.
- During extraction from the Textual UI path, the progress indicator updates at least once per completed folder/root unit.
- Non-interactive mode flags continue to work unchanged (no UI required).

## Verification commands (run each phase as relevant)

- Confirm baseline: `codebase-extractor --dry-run --mode everything` (ensures non-interactive path still functions).
- Run interactive wizard path and confirm behavior unchanged (folder selection, root sentinel handling, outputs).
- Run Textual path on a small project and compare:
  - Same number of output files for equivalent selections.
  - Same YAML header fields and filtering outcomes.

## Plan of record phases

## Phase 0: Prep

- Task: Define an internal “extraction session config” structure (in-memory) that can be populated from: (a) CLI args, (b) wizard prompts, (c) Textual UI.
- Task: Add a UI routing decision:
  - If `--mode` is provided, always run non-interactive mode (skip any UI).
  - Else if a new flag (e.g., `--tui`) is provided, run Textual.
  - Else default to wizard for now (safe rollout).
- Files: `src/codebaseextractor/cli.py`, `src/codebaseextractor/mainlogic.py`.
- Tests: manual smoke tests for entry paths (non-interactive, wizard, Textual).
- Verify: baseline non-interactive command still works.

## Phase 1: Textual shell (tabs)

- Task: Create a new module for Textual UI (e.g., `tui_app.py`) and implement top tabs using `TabbedContent` + `TabPane` for Settings / Extensions / Tree.
- Task: Add global keybindings for navigation and a visible “Run extraction” action/button.
- Files: new `src/codebaseextractor/tui_*.py` module(s), minimal integration in `mainlogic.py`.
- Tests: manual UI navigation test.
- Verify: can open UI, switch tabs, exit cleanly.

## Phase 2: Settings + Extensions state wiring

- Task: Map Settings tab controls to existing config behaviors (exclude large files, output dir name, root path selection, dry-run).
- Task: Implement Extensions tab as a state editor:
  - Start with presets (e.g., “Flutter preset”, “JavaScript preset”) that toggle known excluded directories and common patterns, without changing the core filter engine yet.
  - Ensure any changes are reflected in the extraction session config used by the run phase.
- Files: `config.py` (optional: add preset definitions), new Textual UI modules, `mainlogic.py` integration.
- Verify: toggling settings changes what will be extracted (dry-run preview is acceptable).

## Phase 3: Tree selection + progress bar (per-folder/root)

- Task: Implement Tree tab selection UI that can produce:
  - A set of folder paths to process (mirrors `folderstoprocess` today).
  - A boolean for “include root files only” (mirrors current ROOT sentinel behavior).
- Task: Implement extraction execution from Textual UI using the existing extraction functions (`extract_code_from_folder`, `extract_code_from_root`, `write_to_markdown_file`).
- Task: Progress bar:
  - Compute `total_units = len(selected_folders) + (1 if include_root_files else 0)`.
  - Update progress after each unit completes (folder/root).
- Verify: progress visibly increments per completed unit, and outputs are written (or dry-run behaves correctly).

## Risks / mitigations

- Risk: UI path diverges from wizard and breaks parity.
- Mitigation: Reuse existing `filehandler` extraction/filter functions unchanged; restrict Textual path to _collecting inputs_ and showing progress.
- Risk: Full-screen TUI may not work well in narrow terminals.
- Mitigation: Keep wizard fallback and make Textual opt-in initially.

## Notes / deviations

- Decision recorded: Keep current wizard as fallback; Textual UI is opt-in initially, with the option to flip the default later.
- Decision recorded: Progress bar scope is per-folder/root units first (no per-file progress refactor in this plan).
