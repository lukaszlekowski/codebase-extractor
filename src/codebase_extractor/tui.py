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
from textual.css.query import NoMatches
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane, Static,
    Switch, Input, Checkbox, Label, Tree, Button, RadioSet, RadioButton
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
    excluded_dirs: Set[str] = field(default_factory=lambda: set(config.EXCLUDED_DIRS))

    def get_excluded_dirs(self) -> Set[str]:
        """Get excluded directories based on user configuration."""
        return self.excluded_dirs


class ExclusionTree(Tree):
    """A tree widget for exclusion configuration."""

    def __init__(self, session: ExtractionSession, **kwargs):
        """Initialize the exclusion tree."""
        self.session = session
        super().__init__("Exclusions", **kwargs)
        self.show_root = False
        self.guide_depth = 2

    def on_mount(self) -> None:
        """Build the tree when mounted."""
        # Standard exclusions group
        standard_node = self.root.add("Standard Exclusions")
        standard_node.expand()
        self._add_exclusion_item(standard_node, "node_modules", "JS/Node dependencies")
        self._add_exclusion_item(standard_node, "vendor", "PHP/Composer dependencies")
        self._add_exclusion_item(standard_node, "__pycache__", "Python bytecode cache")
        self._add_exclusion_item(standard_node, "dist", "Distribution/build output")
        self._add_exclusion_item(standard_node, "build", "Build artifacts")
        self._add_exclusion_item(standard_node, ".git", "Git repository data")
        self._add_exclusion_item(standard_node, "venv/.venv", "Python virtual environments")

        # Flutter/Mobile exclusions group
        flutter_node = self.root.add("Flutter/Mobile")
        flutter_node.expand()
        self._add_exclusion_item(flutter_node, ".dart_tool", "Dart build configuration")
        self._add_exclusion_item(flutter_node, ".gradle", "Android Gradle cache")
        self._add_exclusion_item(flutter_node, "Pods", "iOS CocoaPods dependencies")
        self._add_exclusion_item(flutter_node, "DerivedData", "Xcode build artifacts")

        # Build/Cache exclusions group
        build_node = self.root.add("Build/Cache")
        build_node.expand()
        self._add_exclusion_item(build_node, ".next", "Next.js build cache")
        self._add_exclusion_item(build_node, "target", "Rust/Cargo build output")
        self._add_exclusion_item(build_node, ".cache", "Generic cache directory")
        self._add_exclusion_item(build_node, "tsconfig.tsbuildinfo", "TypeScript incremental build")

    def _add_exclusion_item(self, parent, folder: str, description: str) -> None:
        """Add an exclusion item as a tree node."""
        label = f"{folder}  [dim]{description}[/dim]" if description else folder
        parent.add_leaf(label, data=folder)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection - toggle exclusion status."""
        node = event.node
        if node.data:
            folder = node.data
            # Toggle exclusion status
            if folder in self.session.excluded_dirs:
                self.session.excluded_dirs.discard(folder)
                # Remove checkmark from label
                base_label = str(node.label).replace("[green]✓[/green] ", "")
                node.set_label(base_label)
            else:
                self.session.excluded_dirs.add(folder)
                # Add checkmark to label
                node.set_label(f"[green]✓[/green] {node.label}")
            self.log(f"{'Excluded' if folder in self.session.excluded_dirs else 'Included'}: {folder}")


class CodebaseExtractorApp(App):
    """Main Textual app for Codebase Extractor."""

    TITLE = "Codebase Extractor"
    SUB_TITLE = "v1.2.0 - Textual TUI"
    BINDINGS = [
        Binding("ctrl+r", "run_extraction", "Run"),
        Binding("q", "app.quit", "Quit"),
        Binding("space", "toggle_selection", "Toggle", show=False),
    ]

    CSS = """
    #settings_container {
        layout: vertical;
    }

    .section-border {
        border: solid cyan;
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
    """

    def __init__(self, **kwargs):
        """Initialize the app."""
        super().__init__(**kwargs)
        self.session = ExtractionSession()
        self.root_path = Path.cwd()

    def on_mount(self) -> None:
        """Set up the UI after mounting."""
        # Set border titles for sections
        self.query_one("#output_dir_section").border_title = "Output Directory"
        self.query_one("#large_file_section").border_title = "Large File Exclusion"
        self.query_one("#dry_run_section").border_title = "Dry-run Execution Mode (design for testing purposes)"

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

            # Extensions Tab with tree view
            yield TabPane("Extensions", Vertical(
                Label("Folders to Exclude", classes="header"),
                Static(
                    "Select folders to exclude from extraction. "
                    "[green]✓[/green] = excluded, click to toggle.",
                    classes="hint"
                ),
                ExclusionTree(self.session, id="exclusion_tree"),
                Static(),
                Static(
                    "Press [b]Space[/b] to toggle selection on highlighted item.\n"
                    "Press [b]Enter[/b] or [b]→/←[/b] to expand/collapse groups.",
                    classes="hint"
                ),
                id="extensions_container"
            ), id="extensions_tab")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "run_button":
            self.action_run_extraction()
        elif event.button.id == "quit_button":
            self.exit()

    def action_toggle_selection(self) -> None:
        """Toggle selection on the currently highlighted tree node."""
        tree = self.query_one("#exclusion_tree", ExclusionTree)
        if tree.cursor_node and tree.cursor_node.data:
            # Directly toggle the exclusion for the current node
            node = tree.cursor_node
            folder = node.data
            if folder in self.session.excluded_dirs:
                self.session.excluded_dirs.discard(folder)
                base_label = str(node.label).replace("[green]✓[/green] ", "")
                node.set_label(base_label)
            else:
                self.session.excluded_dirs.add(folder)
                node.set_label(f"[green]✓[/green] {node.label}")
            self.log(f"{'Excluded' if folder in self.session.excluded_dirs else 'Included'}: {folder}")

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
