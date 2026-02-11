"""
Textual TUI for Codebase Extractor.

Phase 2: Settings and Extensions tabs with functional controls.
Phase 3 will add Tree selection and progress bar.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane, Static,
    Switch, Input, Label, Button, RadioSet, RadioButton, SelectionList
)

# Import from our modules
from . import config


@dataclass
class ExtractionSession:
    """Holds the extraction session configuration from TUI inputs."""
    exclude_large_files: bool = False
    max_file_size_mb: float = 1.0
    output_dir_name: str = config.OUTPUT_DIR_NAME
    dry_run: bool = False
    extension_preset: str = "General"
    selected_folders: Set[Path] = field(default_factory=set)
    include_root_files: bool = False

    # Excluded directories (user-configurable)
    # Default to all standard exclusions being selected
    excluded_dirs: Set[str] = field(default_factory=lambda: set([
        "node_modules", "vendor", "__pycache__", "dist", "build", ".git", "venv",
        ".dart_tool", ".gradle", "Pods", "DerivedData",
        ".next", "target", ".cache", "tsconfig.tsbuildinfo",
    ]))

    def get_excluded_dirs(self) -> Set[str]:
        """Get excluded directories based on user configuration."""
        return self.excluded_dirs


class CodebaseExtractorApp(App):
    """Main Textual app for Codebase Extractor."""

    TITLE = "Codebase Extractor"
    SUB_TITLE = "v1.2.0 - Textual TUI"
    BINDINGS = [
        Binding("ctrl+r", "run_extraction", "Run"),
        Binding("q", "app.quit", "Quit"),
    ]

    CSS = """
    #settings_container {
        layout: vertical;
    }

    .section-border {
        border: round cyan;
        padding: 1;
        margin: 1 0;
    }

    .info-text {
        text-style: dim;
        text-style: italic;
    }

    .hint-text {
        text-style: dim;
        margin: 1 2;
    }

    .button-row {
        align: center middle;
        height: 3;
    }

    .exclusions-container {
        padding: 0 2;
    }

    .exclusion-group {
        border: round cyan;
        padding: 1;
        margin: 1 0;
    }

    .group-header {
        text-style: bold;
    }

    Checkbox {
        margin: 0 0 0 0;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the app."""
        super().__init__(**kwargs)
        self.session = ExtractionSession()
        self.root_path = Path.cwd()

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        with TabbedContent(id="main_tabs"):
            # Settings Tab - Two-column layout
            yield TabPane("Settings", Vertical(
                Label("Extraction Settings", id="settings_header"),

                # Info section
                Static(f"Root directory: {self.root_path}", classes="info-text"),
                Static(),

                # Output Directory Section
                Vertical(
                    Static("Output will be saved to a subdirectory of the root above.", classes="info-text"),
                    Static(),
                    Static("Folder name:"),
                    Input(
                        value=config.OUTPUT_DIR_NAME,
                        placeholder="CODEBASE_EXTRACTS",
                        id="output_dir_input",
                    ),
                    id="output_dir_section",
                    classes="section-border",
                ),
                Static(),

                # File Size Exclusion Section
                Vertical(
                    Static("Exclude files larger than or equal (>=) to ... MB:"),
                    Horizontal(
                        Input(
                            value="1",
                            placeholder="1",
                            id="max_file_size_input",
                        ),
                        Static(" MB "),
                        Switch(value=False, id="exclude_large_switch"),
                    ),
                    id="large_file_section",
                    classes="section-border",
                ),
                Static(),

                # Dry Run Section
                Vertical(
                    RadioSet(
                        RadioButton("Enabled → No files will be written - only show what would be extracted", value=False, id="dry_run_enabled"),
                        RadioButton("Disabled → Files will be written to the output directory", value=True, id="dry_run_disabled"),
                        id="dry_run_radioset",
                    ),
                    id="dry_run_section",
                    classes="section-border",
                ),
                Static(),

                # Action Buttons
                Horizontal(
                    Button("Run Extraction", variant="primary", id="run_button"),
                    Button("Quit", id="quit_button"),
                    classes="button-row",
                ),
                Static(),
                Static(
                    "Press [b]Ctrl+R[/b] or click Run to start extraction.\n"
                    "Use the Tree tab to select specific folders (Phase 3).",
                    classes="hint-text"
                ),
                id="settings_container"
            ), id="settings_tab")

            # Exclusions Tab with SelectionLists
            yield TabPane("Exclusions", Vertical(
                Label("Folder Exclusions", classes="header"),
                Static(
                    "Select folders to exclude from extraction. "
                    "All items start as [bold]selected[/bold] (excluded). "
                    "Press Space to toggle selection.",
                    classes="hint"
                ),
                Static(),
                # Standard exclusions
                Label("Standard", classes="group-header"),
                SelectionList(
                    ("node_modules - JS/Node dependencies", "node_modules", True),
                    ("vendor - PHP/Composer dependencies", "vendor", True),
                    ("__pycache__ - Python bytecode cache", "__pycache__", True),
                    ("dist - Distribution/build output", "dist", True),
                    ("build - Build artifacts", "build", True),
                    (".git - Git repository data", ".git", True),
                    ("venv/.venv - Python virtual environments", "venv", True),
                    id="std_exclusions_list",
                ),
                Static(),
                # Flutter/Mobile exclusions
                Label("Flutter/Mobile", classes="group-header"),
                SelectionList(
                    (".dart_tool - Dart build configuration", ".dart_tool", True),
                    (".gradle - Android Gradle cache", ".gradle", True),
                    ("Pods - iOS CocoaPods dependencies", "Pods", True),
                    ("DerivedData - Xcode build artifacts", "DerivedData", True),
                    id="flutter_exclusions_list",
                ),
                Static(),
                # Build/Cache exclusions
                Label("Build/Cache", classes="group-header"),
                SelectionList(
                    (".next - Next.js build cache", ".next", True),
                    ("target - Rust/Cargo build output", "target", True),
                    (".cache - Generic cache directory", ".cache", True),
                    ("tsconfig.tsbuildinfo - TypeScript incremental build", "tsconfig.tsbuildinfo", True),
                    id="build_exclusions_list",
                ),
                Static(),
                Static(
                    "Use Space to select/deselect folders.\n"
                    "Selected folders will be excluded from extraction.",
                    classes="hint"
                ),
                id="exclusions_container"
            ), id="exclusions_tab")

            # Tree Tab (placeholder - Phase 3)
            yield TabPane("Tree", Vertical(
                Label("Folder Selection", classes="header"),
                Static(),
                Static(
                    "  ╔═══════════════════════════════════════════════════════════╗\n"
                    "  ║                      TREE TAB                              ║\n"
                    "  ║                      (PHASE 3)                             ║\n"
                    "  ╠═══════════════════════════════════════════════════════════╣\n"
                    "  ║                                                             ║\n"
                    "  ║  Coming in Phase 3:                                        ║\n"
                    "  ║  - Visual directory tree representation                     ║\n"
                    "  ║  - Multi-select folders for extraction                      ║\n"
                    "  ║  - Root files selection                                     ║\n"
                    "  ║  - Progress bar during extraction                           ║\n"
                    "  ║                                                             ║\n"
                    "  ║  For now, extraction will use 'everything' mode:            ║\n"
                    "  ║  all folders in the root directory will be extracted.       ║\n"
                    "  ║                                                             ║\n"
                    "  ╚═══════════════════════════════════════════════════════════╝\n",
                    classes="placeholder"
                ),
                id="tree_container"
            ), id="tree_tab")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the UI after mounting."""
        # Set border titles for Settings sections
        self.query_one("#output_dir_section").border_title = "Output Directory"
        self.query_one("#large_file_section").border_title = "Large File Exclusion"
        self.query_one("#dry_run_section").border_title = "Dry-run Execution Mode (design for testing purposes)"

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggle changes."""
        if event.switch.id == "exclude_large_switch":
            self.session.exclude_large_files = event.value
            self.log(f"Exclude large files: {event.value}")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "dry_run_radioset":
            # Enabled = dry run, Disabled = normal run
            self.session.dry_run = (event.radio_set.query_one("#dry_run_enabled").value)
            self.log(f"Dry run: {self.session.dry_run}")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes."""
        if event.input.id == "output_dir_input":
            self.session.output_dir_name = event.value or config.OUTPUT_DIR_NAME
            self.log(f"Output directory: {event.value}")
        elif event.input.id == "max_file_size_input":
            try:
                self.session.max_file_size_mb = float(event.value) if event.value else 1.0
                self.log(f"Max file size: {self.session.max_file_size_mb} MB")
            except ValueError:
                pass

    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Handle SelectionList selection changes (excluded folders)."""
        # The SelectionList.SelectedChanged message gives us access to the selection_list
        # We need to check which items are selected and update session.excluded_dirs
        selection_list = event.selection_list

        # Get all selected values (folder names) from this selection list
        selected_values = selection_list.selected

        # Map SelectionList IDs to folder prefixes for matching
        list_id = selection_list.id
        folder_map = {
            "std_exclusions_list": ["node_modules", "vendor", "__pycache__", "dist", "build", ".git", "venv"],
            "flutter_exclusions_list": [".dart_tool", ".gradle", "Pods", "DerivedData"],
            "build_exclusions_list": [".next", "target", ".cache", "tsconfig.tsbuildinfo"],
        }

        # Get the expected folder names for this list
        expected_folders = folder_map.get(list_id, [])

        # Update session.excluded_dirs: add selected items, remove unselected items
        for folder in expected_folders:
            if folder in selected_values:
                if folder not in self.session.excluded_dirs:
                    self.session.excluded_dirs.add(folder)
                    self.log(f"[red]Excluded:[/red] {folder}")
            else:
                if folder in self.session.excluded_dirs:
                    self.session.excluded_dirs.discard(folder)
                    self.log(f"[green]Included:[/green] {folder}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "run_button":
            self.action_run_extraction()
        elif event.button.id == "quit_button":
            self.exit()

    def action_run_extraction(self) -> None:
        """Handle the run extraction action."""
        # Update session from current UI values
        exclude_large = self.query_one("#exclude_large_switch", Switch).value
        dry_run_enabled = self.query_one("#dry_run_enabled", RadioButton).value
        output_dir = self.query_one("#output_dir_input", Input).value
        max_size_input = self.query_one("#max_file_size_input", Input).value

        self.session.exclude_large_files = exclude_large
        self.session.dry_run = dry_run_enabled
        self.session.output_dir_name = output_dir or config.OUTPUT_DIR_NAME

        try:
            self.session.max_file_size_mb = float(max_size_input) if max_size_input else 1.0
        except ValueError:
            self.session.max_file_size_mb = 1.0

        # Show session summary
        self.bell()
        self.exit(
            f"Session configured - would run with:\n"
            f"  Root: {self.root_path}\n"
            f"  Output dir: {self.root_path / self.session.output_dir_name}\n"
            f"  Exclude large files: {self.session.exclude_large_files} (>{self.session.max_file_size_mb}MB)\n"
            f"  Dry run: {self.session.dry_run}\n"
            f"  Excluded folders: {len(self.session.excluded_dirs)} selected\n"
            f"\n"
            f"(Extraction will be implemented in Phase 3)"
        )


def launch_tui() -> None:
    """Launch the Textual TUI application."""
    app = CodebaseExtractorApp()
    app.run()
