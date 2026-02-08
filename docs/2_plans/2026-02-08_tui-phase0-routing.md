# Phase 0: TUI Routing & Scaffolding

## Date
2025-02-08

## Objective
Add `--tui` flag and basic routing logic to prepare for future Textual TUI implementation. No actual TUI functionality in this phase.

## Routing Rules
1. If `--mode` is provided → run existing non-interactive path
2. Else if `--tui` is passed → launch placeholder TUI entrypoint, then exit cleanly
3. Else → default to existing Questionary wizard

## Files to Modify

### 1. `src/codebase_extractor/cli.py`
- Add `--tui` flag (action='store_true', help="Launch Textual TUI interface (placeholder)")

### 2. `src/codebase_extractor/main_logic.py`
- Add routing logic after argument parsing
- Create placeholder function `_launch_tui_placeholder()`
- Preserve all existing behavior

## Verification Commands
- `codebase-extractor --dry-run --mode everything` (non-interactive path)
- `codebase-extractor` (wizard default)
- `codebase-extractor --tui` (placeholder)

## Constraints
- No changes to file_handler filtering/extraction logic
- No new third-party dependencies
- Keep wizard intact
- Minimal, reviewable changes
