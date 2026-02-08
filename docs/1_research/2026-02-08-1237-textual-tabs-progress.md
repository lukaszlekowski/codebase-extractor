---
type: research
status: active
created: 2026-02-08
topic: Textual tabbed UI + progress bar for extraction
relatedspec: docs/specs/optional.md
relatedplan: docs/plan/2026-02-08-1237-textual-tabs-progress.md
---

# Research: Textual tabbed UI + progress bar for extraction

## Goal

Replace the current step-by-step Questionary wizard with a Textual full-screen TUI that uses top tabs (Settings / Extensions / Tree) and includes a progress indicator during extraction, while keeping the existing wizard as a fallback for small terminals.

## Current behavior (facts only)

- The app is orchestrated in `src/codebaseextractor/mainlogic.py` and uses `questionary` prompts (`select`, `text`, `checkbox`) to collect settings and folder selections.
- The “tree-like” folder selection is implemented by building a flattened list of `questionary.Choice` titles using connectors (`└──`, `├──`, `│   `) in `filehandler.get_folder_choices(rootpath, maxdepth)`.
- Extraction is executed after prompts; progress feedback is currently per-folder (and root-files) via `Halo` spinners (`with Halo(text=..., spinner="dots")`).
- Filtering is defined in `config.py` (`EXCLUDED_DIRS`, `ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE_MB`, etc.) and enforced in `filehandler.is_allowed_file(...)`.
- The extraction functions (`extract_code_from_folder`, `extract_code_from_root`) return aggregated results only after completing the scan, and the write step adds YAML front matter including run reference, timestamps, file count, char count, and word count.

## Key files / directories

- `src/codebaseextractor/mainlogic.py`: current wizard flow, selection modes, processing loop, Halo spinner usage.
- `src/codebaseextractor/filehandler.py`: tree choice generation, filter logic, extraction routines, markdown output writer.
- `src/codebaseextractor/config.py`: default exclusions / allowlists / thresholds.
- `src/codebaseextractor/ui.py`: banner/instructions/help text used by the wizard.

## Data flow today

- Inputs: CLI args (non-interactive mode) or interactive wizard prompts.
- State computed: `exclude_large` boolean, `selection_mode`, optional `scan_depth`, selected folder paths, and whether to process root files.
- Processing: iterate selected folders; for each folder (and optionally root files), run extraction, then write a timestamped markdown file to output directory.

## Constraints

- Must keep the existing Questionary wizard as a fallback, because it works well in small terminal windows.
- “Real progress bar” can be overall progress across folder/root units first (not per-file).
- Non-interactive mode already exists via arguments (`--mode`, `--select-folders`, `--select-root`, etc.) and should continue to work.

## Options discovered (no decision yet)

- Option A: Introduce a new Textual TUI path that uses `TabbedContent` / `TabPane` for top-level tabs, while leaving the wizard intact behind a fallback switch.
- Option B: Continue to use the wizard for all cases and only add a progress bar to the existing CLI output (lowest risk, but does not achieve the “tabs UI” goal).

## Unknowns / questions to resolve

- What determines whether we run Textual vs wizard by default (flag-driven, terminal-size heuristic, or explicit user choice).
- How to represent “Extensions” groups (Flutter/JS/etc.) in config: static presets, user-defined profiles, and how they translate into filtering logic.
- How to do multi-select in a tree UI (Textual provides selection messages; multi-select requires an explicit selection model and visual representation).

## References

- Existing codebase extractor flow and selection/tree generation.
- Textual `TabbedContent` documentation.
- Textual `DirectoryTree` documentation (filesystem tree concepts/events/filtering hooks to support a Tree tab).
