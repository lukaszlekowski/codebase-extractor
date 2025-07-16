# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-16

### Features

### Added

- **Non-Interactive Mode**: Full application control via command-line arguments (`--mode`, `--depth`, `--select-folders`, etc.) for automation.
- **`--root` Argument**: Ability to specify a target directory to run the extractor on.
- **`--output-dir` Argument**: Ability to set a custom name for the output folder.
- **`--dry-run` Mode**: Added a flag to simulate an extraction and show a summary without writing any files.
- **Structured Logging**: Replaced `print` statements with a robust logging system, controllable via `--verbose` and `--log-file` flags.

## [1.0.1] - 2025-07-15

### Fixed

- Corrected multiple `AttributeError`, `TypeError`, and `NameError` bugs that occurred after the initial refactoring.
- Fixed an unhandled `KeyboardInterrupt` crash that could happen during the startup instruction sequence.
- Ensured the package version is correctly imported and displayed from `__init__.py` across all modules.

## [1.0.0] - 2025-07-15

### Added

- **Initial Release**: First version published to PyPI.
- **Project Refactoring**: Converted the single script into a professional, modular package with a `src` layout (`config.py`, `ui.py`, `file_handler.py`, `main_logic.py`).
- **YAML Metadata**: Output files are now prepended with a YAML header containing a unique run reference, timestamp, and file count.
- **Advanced UI**: Implemented numerous UI and UX enhancements, including a responsive banner, step counters, clearer instructions, and graceful exit handling.
- **Nested Folder Selection**: Users can now select specific sub-folders from a tree-like view with configurable scan depth.
