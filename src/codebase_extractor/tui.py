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
from textual.containers import Horizontal, Vertical, VerticalScroll, Container, Center
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
    # Default to all standard exclusions being selected (matching config.py)
    excluded_dirs: Set[str] = field(default_factory=lambda: set([
        # Standard exclusions
        "node_modules", "vendor", "__pycache__", "dist", "build", "target", ".next",
        ".git", ".svn", ".hg", ".vscode", ".idea", "venv", ".venv", ".dart_tool",
        # Flutter/Mobile exclusions
        ".gradle", "Pods", "DerivedData",
    ]))

    # Excluded filenames (lock files, config files)
    excluded_filenames: Set[str] = field(default_factory=lambda: set([
        "package-lock.json", "yarn.lock", "composer.lock", ".env", "Podfile.lock",
    ]))

    # Allowed extensions (for file filtering during extraction)
    allowed_extensions: Set[str] = field(default_factory=lambda: set(config.ALLOWED_EXTENSIONS))

    # Allowed filenames (specific files that are always allowed)
    allowed_filenames: Set[str] = field(default_factory=lambda: set(config.ALLOWED_FILENAMES))

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
            # Settings Tab
            yield TabPane("Settings", VerticalScroll(
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
            yield TabPane("Exclusions", VerticalScroll(
                Label("Folder Exclusions", classes="header"),
                Static(
                    "Select folders to exclude from extraction. "
                    "All items start as [bold]selected[/bold] (excluded). "
                    "Press Space to toggle selection.",
                    classes="hint"
                ),
                Static(),
                # Standard exclusions
                Label("Package Managers & Build Output", classes="group-header"),
                SelectionList(
                    ("node_modules - JS/Node dependencies", "node_modules", True),
                    ("vendor - PHP/Composer dependencies", "vendor", True),
                    ("__pycache__ - Python bytecode cache", "__pycache__", True),
                    ("dist - Distribution/build output", "dist", True),
                    ("build - Build artifacts", "build", True),
                    ("target - Rust/Cargo build output", "target", True),
                    (".next - Next.js build cache", ".next", True),
                    id="pkg_exclusions_list",
                ),
                Static(),
                # Version Control
                Label("Version Control", classes="group-header"),
                SelectionList(
                    (".git - Git repository data", ".git", True),
                    (".svn - Subversion repository data", ".svn", True),
                    (".hg - Mercurial repository data", ".hg", True),
                    id="vcs_exclusions_list",
                ),
                Static(),
                # Virtual Environments
                Label("Virtual Environments", classes="group-header"),
                SelectionList(
                    ("venv - Python virtual environment", "venv", True),
                    (".venv - Python virtual environment", ".venv", True),
                    id="venv_exclusions_list",
                ),
                Static(),
                # IDE & Editor
                Label("IDE & Editor", classes="group-header"),
                SelectionList(
                    (".vscode - VS Code settings", ".vscode", True),
                    (".idea - JetBrains IDE settings", ".idea", True),
                    id="ide_exclusions_list",
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
                # Lock Files
                Label("Lock Files", classes="group-header"),
                SelectionList(
                    ("package-lock.json - npm lock file", "package-lock.json", True),
                    ("yarn.lock - Yarn lock file", "yarn.lock", True),
                    ("composer.lock - PHP Composer lock file", "composer.lock", True),
                    ("Podfile.lock - CocoaPods lock file", "Podfile.lock", True),
                    id="lock_files_list",
                ),
                Static(),
                # Config Files
                Label("Config Files", classes="group-header"),
                SelectionList(
                    (".env - Environment variables", ".env", True),
                    id="config_files_list",
                ),
                Static(),
                Static(
                    "Use Space to select/deselect items.\n"
                    "Selected items will be excluded from extraction.",
                    classes="hint"
                ),
                id="exclusions_container"
            ), id="exclusions_tab")

            # Allowed Extensions & Folders Tab
            yield TabPane("Allowed Extensions & Folders", VerticalScroll(
                Label("Allowed Extensions & Files", classes="header"),
                Static(
                    "Select which file extensions and specific filenames to include in extraction. "
                    "All items start as [bold]selected[/bold] (allowed). "
                    "Press Space to toggle selection.",
                    classes="hint"
                ),
                Static(),
                # Web & General extensions
                Label("Web & General", classes="group-header"),
                SelectionList(
                    (".php - PHP", ".php", True),
                    (".html - HTML", ".html", True),
                    (".css - CSS", ".css", True),
                    (".js - JavaScript", ".js", True),
                    (".jsx - React JSX", ".jsx", True),
                    (".ts - TypeScript", ".ts", True),
                    (".tsx - TypeScript JSX", ".tsx", True),
                    (".vue - Vue.js", ".vue", True),
                    (".svelte - Svelte", ".svelte", True),
                    (".py - Python", ".py", True),
                    (".rb - Ruby", ".rb", True),
                    (".java - Java", ".java", True),
                    (".c - C", ".c", True),
                    (".cpp - C++", ".cpp", True),
                    (".cs - C#", ".cs", True),
                    (".go - Go", ".go", True),
                    (".rs - Rust", ".rs", True),
                    (".json - JSON", ".json", True),
                    (".xml - XML", ".xml", True),
                    (".yaml - YAML", ".yaml", True),
                    (".yml - YAML", ".yml", True),
                    (".toml - TOML", ".toml", True),
                    (".ini - INI config", ".ini", True),
                    (".conf - Config files", ".conf", True),
                    (".md - Markdown", ".md", True),
                    (".txt - Text", ".txt", True),
                    (".rst - reStructuredText", ".rst", True),
                    (".twig - Twig template", ".twig", True),
                    (".blade - Blade template", ".blade", True),
                    (".handlebars - Handlebars", ".handlebars", True),
                    (".mustache - Mustache", ".mustache", True),
                    (".ejs - EJS template", ".ejs", True),
                    (".sql - SQL", ".sql", True),
                    (".graphql - GraphQL", ".graphql", True),
                    (".gql - GraphQL", ".gql", True),
                    (".tf - Terraform", ".tf", True),
                    id="web_general_extensions_list",
                ),
                Static(),
                # Flutter/Mobile extensions
                Label("Flutter / Dart / Mobile", classes="group-header"),
                SelectionList(
                    (".dart - Dart", ".dart", True),
                    (".arb - ARB resource file", ".arb", True),
                    (".gradle - Gradle", ".gradle", True),
                    (".properties - Properties file", ".properties", True),
                    (".plist - Property list (iOS)", ".plist", True),
                    (".xcconfig - Xcode config", ".xcconfig", True),
                    id="mobile_extensions_list",
                ),
                Static(),
                # Script extensions
                Label("Scripts", classes="group-header"),
                SelectionList(
                    (".sh - Shell script", ".sh", True),
                    (".bat - Batch script", ".bat", True),
                    id="script_extensions_list",
                ),
                Static(),
                # Allowed filenames
                Label("Allowed Filenames", classes="group-header"),
                SelectionList(
                    ("dockerfile - Docker config", "dockerfile", True),
                    (".gitignore - Git ignore file", ".gitignore", True),
                    (".htaccess - Apache config", ".htaccess", True),
                    ("makefile - Make build file", "makefile", True),
                    (".dockerignore - Docker ignore", ".dockerignore", True),
                    (".env.example - Environment template", ".env.example", True),
                    ("podfile - CocoaPods config", "podfile", True),
                    ("gemfile - Ruby gems", "gemfile", True),
                    ("jenkinsfile - Jenkins config", "jenkinsfile", True),
                    ("gradlew - Gradle wrapper", "gradlew", True),
                    id="allowed_filenames_list",
                ),
                Static(),
                Static(
                    "Use Space to select/deselect items.\n"
                    "Selected items will be included in extraction.",
                    classes="hint"
                ),
                id="allowed_container"
            ), id="allowed_tab")

            # Tree Tab (placeholder - Phase 3)
            yield TabPane("Tree", VerticalScroll(
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
        """Handle SelectionList selection changes (excluded folders/files, allowed extensions)."""
        selection_list = event.selection_list
        selected_values = selection_list.selected

        # Map SelectionList IDs to their items
        list_id = selection_list.id
        item_map = {
            # Excluded Directories
            "pkg_exclusions_list": ("excluded_dirs", ["node_modules", "vendor", "__pycache__", "dist", "build", "target", ".next"]),
            "vcs_exclusions_list": ("excluded_dirs", [".git", ".svn", ".hg"]),
            "venv_exclusions_list": ("excluded_dirs", ["venv", ".venv"]),
            "ide_exclusions_list": ("excluded_dirs", [".vscode", ".idea"]),
            "flutter_exclusions_list": ("excluded_dirs", [".dart_tool", ".gradle", "Pods", "DerivedData"]),
            # Excluded Filenames
            "lock_files_list": ("excluded_filenames", ["package-lock.json", "yarn.lock", "composer.lock", "Podfile.lock"]),
            "config_files_list": ("excluded_filenames", [".env"]),
            # Allowed Extensions
            "web_general_extensions_list": ("allowed_extensions", [
                ".php", ".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
                ".py", ".rb", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".json", ".xml",
                ".yaml", ".yml", ".toml", ".ini", ".conf", ".md", ".txt", ".rst", ".twig",
                ".blade", ".handlebars", ".mustache", ".ejs", ".sql", ".graphql", ".gql", ".tf",
            ]),
            "mobile_extensions_list": ("allowed_extensions", [".dart", ".arb", ".gradle", ".properties", ".plist", ".xcconfig"]),
            "script_extensions_list": ("allowed_extensions", [".sh", ".bat"]),
            # Allowed Filenames
            "allowed_filenames_list": ("allowed_filenames", [
                "dockerfile", ".gitignore", ".htaccess", "makefile", ".dockerignore",
                ".env.example", "podfile", "gemfile", "jenkinsfile", "gradlew",
            ]),
        }

        if list_id not in item_map:
            return

        session_attr, expected_items = item_map[list_id]

        # Get the session set to update
        if session_attr == "excluded_dirs":
            session_set = self.session.excluded_dirs
            label_prefix = "Excluded dir"
        elif session_attr == "excluded_filenames":
            session_set = self.session.excluded_filenames
            label_prefix = "Excluded file"
        elif session_attr == "allowed_extensions":
            session_set = self.session.allowed_extensions
            label_prefix = "Allowed extension"
        else:  # allowed_filenames
            session_set = self.session.allowed_filenames
            label_prefix = "Allowed filename"

        # Update session based on selection
        for item in expected_items:
            is_selected = item in selected_values
            if is_selected:
                if item not in session_set:
                    session_set.add(item)
                    color = "red" if "excluded" in label_prefix else "green"
                    self.log(f"[{color}]{label_prefix}:[/{color}] {item}")
            else:
                if item in session_set:
                    session_set.discard(item)
                    color = "green" if "excluded" in label_prefix else "red"
                    self.log(f"[{color}]Not {label_prefix}:[/{color}] {item}")

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
