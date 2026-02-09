---
type: plan
status: proposed
created: 2026-02-08
phase: 1
relatedresearch: docs/1_research/2026-02-08-1237-textual-tabs-progress.md
---

# Phase 1: Basic Textual App Structure

## Objective
Build a minimal functional Textual app with the tab structure. No real functionality yet - just scaffolding.

## Scope

### 1. Add `textual` dependency
- Add `textual` to `pyproject.toml` dependencies
- Version: latest stable (will check current version)

### 2. Create `tui.py` module
- New file: `src/codebase_extractor/tui.py`
- Basic Textual app with `TabbedContent` and three `TabPane` widgets
- Each tab has placeholder content describing its future purpose

### 3. Wire up routing in `main_logic.py`
- Replace `_launch_tui_placeholder()` with `_launch_textual_app()`
- Import and run the Textual app from `tui.py`

### 4. Confirm clean exit
- Ensure app exits gracefully on Ctrl+C
- Add a "Quit" button for clean exit

## Files to Modify
1. `pyproject.toml` - add textual dependency
2. `src/codebase_extractor/main_logic.py` - update routing
3. `src/codebase_extractor/tui.py` - NEW FILE

## Files NOT to Touch
- `file_handler.py` - no extraction logic changes
- `config.py` - no config changes
- `cli.py` - routing already done in Phase 0

## Verification Commands
- `./venv/bin/python -m src.codebase_extractor.main_logic --tui` - shows Textual app with 3 tabs
- Navigate between tabs (click or keyboard)
- Press `q` or Ctrl+C to exit cleanly

## What Phase 1 Does NOT Include
- No actual settings controls/functionality
- No real tree widget
- No progress bar
- No integration with extraction logic
- No multi-select behavior

## Success Criteria
- Textual app launches with `--tui` flag
- Three tabs are visible and navigable
- App exits cleanly without errors
- No changes to existing wizard or non-interactive behavior
