"""
Textual TUI for Codebase Extractor.

Phase 2: Settings and Extensions tabs with functional controls.
Phase 3: Tree selection and progress bar.
"""

import logging
import datetime
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll, Container, Center
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane, Static,
    Switch, Input, Label, Button, RadioSet, RadioButton, SelectionList,
    ProgressBar, Checkbox
)
from textual import on
from textual.events import Click

# Import from our modules
from . import config
from . import file_handler

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

    # Internal progress tracking (private fields)
    _completed_units: int = field(default=0, init=False, repr=False)

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

    @property
    def total_units(self) -> int:
        """Total number of extraction units (folders + optional root)."""
        return len(self.selected_folders) + (1 if self.include_root_files else 0)

    @property
    def completed_units(self) -> int:
        """Number of completed extraction units."""
        return self._completed_units

    @completed_units.setter
    def completed_units(self, value: int):
        """Set completed units, ensuring it never exceeds total."""
        self._completed_units = min(value, self.total_units)

    def get_excluded_dirs(self) -> Set[str]:
        """Get excluded directories based on user configuration."""
        return self.excluded_dirs

    def progress_fraction(self) -> float:
        """Get progress as a fraction (0.0 to 1.0)."""
        if self.total_units == 0:
            return 0.0
        return self.completed_units / self.total_units


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

    #tree_selection {
        height: 1fr;
    }

    #tree_container {
        
    }

    ProgressBar {
        margin: 1 2;
    }

    #progress_container {
        padding: 1 2;
    }

    .progress-text {
        text-align: center;
        margin: 1 0;
    }

    .status-box {
        border: round cyan;
        padding: 1;
        margin: 1 0;
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
                        RadioButton("Disabled → Files will be written to the output directory", value=True, id="dry_run_disabled"),
                        RadioButton("Enabled → No files will be written - only show what would be extracted", value=False, id="dry_run_enabled"),
                        id="dry_run_radioset",
                    ),
                    id="dry_run_section",
                    classes="section-border",
                ),
                Static(),
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
            yield TabPane("Excluded: Folders & Files", VerticalScroll(
                Label("Excluded Folders & Files", classes="header"),
                Static(
                    "Select folders and files to exclude from extraction. "
                    "All items start as [bold]selected[/bold] (excluded). "
                    "Press Space to toggle selection.",
                    classes="hint"
                ),
                Static(),
                # Standard exclusions
                Label("Package Managers & Build Output", classes="group-header"),
                SelectionList(
                    ("node_modules          - (FOLDER) JS/Node dependencies", "node_modules", True),
                    ("vendor                - (FOLDER) PHP/Composer dependencies", "vendor", True),
                    ("__pycache__           - (FOLDER) Python bytecode cache", "__pycache__", True),
                    ("dist                  - (FOLDER) Distribution/build output", "dist", True),
                    ("build                 - (FOLDER) Build artifacts", "build", True),
                    ("target                - (FOLDER) Rust/Cargo build output", "target", True),
                    (".next                 - (FOLDER) Next.js build cache", ".next", True),
                    id="pkg_exclusions_list",
                ),
                Static(),
                # Version Control
                Label("Version Control", classes="group-header"),
                SelectionList(
                    (".git                  - (FOLDER) Git repository data", ".git", True),
                    (".svn                  - (FOLDER) Subversion repository data", ".svn", True),
                    (".hg                   - (FOLDER) Mercurial repository data", ".hg", True),
                    id="vcs_exclusions_list",
                ),
                Static(),
                # Virtual Environments
                Label("Virtual Environments", classes="group-header"),
                SelectionList(
                    ("venv                  - (FOLDER) Python virtual environment", "venv", True),
                    (".venv                 - (FOLDER) Python virtual environment", ".venv", True),
                    id="venv_exclusions_list",
                ),
                Static(),
                # IDE & Editor
                Label("IDE & Editor", classes="group-header"),
                SelectionList(
                    (".vscode               - (FOLDER) VS Code settings", ".vscode", True),
                    (".idea                 - (FOLDER) JetBrains IDE settings", ".idea", True),
                    id="ide_exclusions_list",
                ),
                Static(),
                # Flutter/Mobile exclusions
                Label("Flutter/Mobile", classes="group-header"),
                SelectionList(
                    (".dart_tool            - (FOLDER) Dart build configuration", ".dart_tool", True),
                    (".gradle               - (FOLDER) Android Gradle cache", ".gradle", True),
                    ("Pods                  - (FOLDER) iOS CocoaPods dependencies", "Pods", True),
                    ("DerivedData           - (FOLDER) Xcode build artifacts", "DerivedData", True),
                    id="flutter_exclusions_list",
                ),
                Static(),
                # Lock Files
                Label("Lock Files", classes="group-header"),
                SelectionList(
                    ("package-lock.json     - (FILE) npm lock file", "package-lock.json", True),
                    ("yarn.lock             - (FILE) Yarn lock file", "yarn.lock", True),
                    ("composer.lock         - (FILE) PHP Composer lock file", "composer.lock", True),
                    ("Podfile.lock          - (FILE) CocoaPods lock file", "Podfile.lock", True),
                    id="lock_files_list",
                ),
                Static(),
                # Config Files
                Label("Config Files", classes="group-header"),
                SelectionList(
                    (".env                  - (FILE) Environment variables", ".env", True),
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

            # Allowed Extensions & Files Tab
            yield TabPane("Allowed: Extensions & Specific Files", VerticalScroll(
                Label("Allowed Extensions & Specific Files", classes="header"),
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
                    (".php                  - (EXTENSION) PHP server-side scripting", ".php", True),
                    (".html                 - (EXTENSION) HTML web markup", ".html", True),
                    (".css                  - (EXTENSION) CSS stylesheet", ".css", True),
                    (".js                   - (EXTENSION) JavaScript client-side scripting", ".js", True),
                    (".jsx                  - (EXTENSION) React JSX JavaScript", ".jsx", True),
                    (".ts                   - (EXTENSION) TypeScript typed JavaScript", ".ts", True),
                    (".tsx                  - (EXTENSION) TypeScript React JSX", ".tsx", True),
                    (".vue                  - (EXTENSION) Vue.js component", ".vue", True),
                    (".svelte               - (EXTENSION) Svelte component", ".svelte", True),
                    (".py                   - (EXTENSION) Python scripting language", ".py", True),
                    (".rb                   - (EXTENSION) Ruby scripting language", ".rb", True),
                    (".java                 - (EXTENSION) Java programming language", ".java", True),
                    (".c                    - (EXTENSION) C programming language", ".c", True),
                    (".cpp                  - (EXTENSION) C++ programming language", ".cpp", True),
                    (".cs                   - (EXTENSION) C# programming language", ".cs", True),
                    (".go                   - (EXTENSION) Go programming language", ".go", True),
                    (".rs                   - (EXTENSION) Rust programming language", ".rs", True),
                    (".json                 - (EXTENSION) JSON data format", ".json", True),
                    (".xml                  - (EXTENSION) XML markup language", ".xml", True),
                    (".yaml                 - (EXTENSION) YAML configuration format", ".yaml", True),
                    (".yml                  - (EXTENSION) YAML configuration format", ".yml", True),
                    (".toml                 - (EXTENSION) TOML configuration format", ".toml", True),
                    (".ini                  - (EXTENSION) INI configuration file", ".ini", True),
                    (".conf                 - (EXTENSION) Generic configuration file", ".conf", True),
                    (".md                   - (EXTENSION) Markdown documentation", ".md", True),
                    (".txt                  - (EXTENSION) Plain text file", ".txt", True),
                    (".rst                  - (EXTENSION) reStructuredText documentation", ".rst", True),
                    (".twig                 - (EXTENSION) Twig PHP template", ".twig", True),
                    (".blade                - (EXTENSION) Laravel Blade template", ".blade", True),
                    (".handlebars           - (EXTENSION) Handlebars template", ".handlebars", True),
                    (".mustache             - (EXTENSION) Mustache template", ".mustache", True),
                    (".ejs                  - (EXTENSION) Embedded JavaScript template", ".ejs", True),
                    (".sql                  - (EXTENSION) SQL database query", ".sql", True),
                    (".graphql              - (EXTENSION) GraphQL query language", ".graphql", True),
                    (".gql                  - (EXTENSION) GraphQL query language", ".gql", True),
                    (".tf                   - (EXTENSION) Terraform infrastructure", ".tf", True),
                    id="web_general_extensions_list",
                ),
                Static(),
                # Flutter/Mobile extensions
                Label("Flutter / Dart / Mobile", classes="group-header"),
                SelectionList(
                    (".dart                 - (EXTENSION) Dart Flutter language", ".dart", True),
                    (".arb                  - (EXTENSION) Flutter localization resource", ".arb", True),
                    (".gradle               - (EXTENSION) Android Gradle build script", ".gradle", True),
                    (".properties           - (EXTENSION) Java properties file", ".properties", True),
                    (".plist                - (EXTENSION) iOS property list", ".plist", True),
                    (".xcconfig             - (EXTENSION) Xcode build configuration", ".xcconfig", True),
                    id="mobile_extensions_list",
                ),
                Static(),
                # Script extensions
                Label("Scripts", classes="group-header"),
                SelectionList(
                    (".sh                   - (EXTENSION) Unix/Linux shell script", ".sh", True),
                    (".bat                  - (EXTENSION) Windows batch script", ".bat", True),
                    id="script_extensions_list",
                ),
                Static(),
                # Allowed filenames
                Label("Allowed Filenames", classes="group-header"),
                SelectionList(
                    ("dockerfile            - (FILE) Docker container configuration", "dockerfile", True),
                    (".gitignore            - (FILE) Git ignore patterns", ".gitignore", True),
                    (".htaccess             - (FILE) Apache web server config", ".htaccess", True),
                    ("makefile              - (FILE) Make build automation", "makefile", True),
                    (".dockerignore         - (FILE) Docker ignore patterns", ".dockerignore", True),
                    (".env.example          - (FILE) Environment variables template", ".env.example", True),
                    ("podfile               - (FILE) iOS CocoaPods dependencies", "podfile", True),
                    ("gemfile               - (FILE) Ruby gem dependencies", "gemfile", True),
                    ("jenkinsfile           - (FILE) Jenkins CI/CD pipeline", "jenkinsfile", True),
                    ("gradlew               - (FILE) Gradle wrapper executable", "gradlew", True),
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

            # Tree Tab (Phase 3)
            yield TabPane("Tree", Vertical(
                Label("Folder Selection", classes="header"),
                Static(
                    "Select folders to extract from. Navigate folders with Arrow keys. "
                    "Press Space to select/deselect a folder.",
                    classes="hint-text"
                ),
                Static(),

                # Root files checkbox
                Horizontal(
                    Checkbox(
                        label="Include root files (files in root directory only)",
                        id="root_files_checkbox",
                        value=False,
                    ),
                    classes="status-box",
                ),
                Static(),

                # Folder tree (built dynamically on mount)
                VerticalScroll(id="tree_selection"),
                Static(),

                # Progress bar (hidden initially)
                Vertical(id="progress_container", classes="progress_container"),
                Static(),

                # Status text for extraction
                Static("", id="extraction_status"),
                Static(),

                # Action buttons
                Horizontal(
                    Button("Run Extraction", variant="primary", id="tree_run_button"),
                    Button("Back to Settings", id="tree_back_button"),
                    classes="button-row",
                ),
                id="tree_container"
            ), id="tree_tab")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the UI after mounting."""
        # Set border titles for Settings sections
        self.query_one("#output_dir_section").border_title = "Output Directory"
        self.query_one("#large_file_section").border_title = "Large File Exclusion"
        self.query_one("#dry_run_section").border_title = "Dry-run Execution Mode (designed for testing purposes)"

        # Clear initial highlight from all SelectionLists
        self.call_after_refresh(self._clear_selection_list_highlights)
        # Clear initial focus from Settings controls (e.g. Dry-run RadioSet)
        self.call_after_refresh(self._clear_focus)

        # Build the folder tree for the Tree tab
        self.call_after_refresh(self._build_folder_tree)

    def _build_folder_tree(self) -> None:
        """Build the folder tree in the Tree tab."""
        tree_container = self.query_one("#tree_selection", VerticalScroll)
        tree_container.remove_children()

        # Get immediate subdirectories of root (non-recursive for simplicity)
        # We only show directories that are not excluded
        subdirs = sorted([
            p for p in self.root_path.iterdir()
            if p.is_dir() and p.name not in config.EXCLUDED_DIRS
        ])

        if not subdirs:
            tree_container.mount(Static("[dim]No folders found in root directory.[/dim]"))
            return

        # Add a select all checkbox at the top
        tree_container.mount(
            Horizontal(
                Checkbox(label="Select All Folders", id="select_all_checkbox", value=False),
                classes="status-box",
            )
        )
        tree_container.mount(Static())

        # Add checkboxes for each folder
        for subdir in subdirs:
            # Sanitize folder name for ID (replace . with _ to satisfy Textual ID rules)
            safe_id = f"folder_{subdir.name.replace('.', '_')}"
            tree_container.mount(
                Checkbox(label=f"📁 {subdir.name}", value=False, id=safe_id)
            )

        # Clear focus from all checkboxes
        self.call_after_refresh(self._clear_focus)

    def _clear_selection_list_highlights(self) -> None:
        """Clear the initial highlight from all SelectionLists."""
        for selection_list in self.query(SelectionList):
            selection_list.highlighted = None

    def _clear_selection_list_highlights_in_pane(self, pane_id: str) -> None:
        """Clear SelectionList highlight only within a specific tab pane."""
        pane = self.query_one(f"#{pane_id}")
        for selection_list in pane.query(SelectionList):
            selection_list.highlighted = None

    def _clear_focus(self) -> None:
        """Remove keyboard focus from all widgets."""
        self.set_focus(None)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Clear focus when entering Settings so Dry-run does not auto-highlight."""
        if event.pane.id == "settings_tab":
            self.call_after_refresh(self._clear_focus)
        elif event.pane.id in {"exclusions_tab", "allowed_tab"}:
            pane_id = event.pane.id
            self.call_after_refresh(lambda: self._clear_selection_list_highlights_in_pane(pane_id))
            self.call_after_refresh(self._clear_focus)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggle changes."""
        if event.switch.id == "exclude_large_switch":
            self.session.exclude_large_files = event.value
            self.log(f"Exclude large files: {event.value}")

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes."""
        # Handle root files checkbox
        if event.checkbox.id == "root_files_checkbox":
            self.session.include_root_files = event.value
            self.log(f"Include root files: {event.value}")

        # Handle select all checkbox
        elif event.checkbox.id == "select_all_checkbox":
            select_all = event.value
            # Update all folder checkboxes
            # Update all folder checkboxes
            children = self.query_one("#tree_selection", VerticalScroll).children
            for child in children:
                if isinstance(child, Checkbox) and child.id and child.id.startswith("folder_"):
                    child.value = select_all
                    # Update session - relying on label for name recovery
                    folder_name = str(child.label).replace("📁 ", "")
                    folder_path = self.root_path / folder_name
                    if select_all:
                        self.session.selected_folders.add(folder_path)
                    else:
                        self.session.selected_folders.discard(folder_path)

        # Handle individual folder checkbox
        elif event.checkbox.id and event.checkbox.id.startswith("folder_"):
            # We can't easily reconstruction original name from sanitized ID if there are collisions,
            # but for this fix we assume simple . -> _ replacement.
            # Ideally we would map IDs to paths, but let's try to recover the name from the label?
            # The label is "📁 {subdir.name}".
            folder_name = str(event.checkbox.label).replace("📁 ", "")
            folder_path = self.root_path / folder_name
            if event.value:
                self.session.selected_folders.add(folder_path)
            else:
                self.session.selected_folders.discard(folder_path)
                # Also deselect "Select All" if a folder is deselected
                select_all = self.query_one("#select_all_checkbox", Checkbox)
                if select_all.value:
                    select_all.value = False

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
        elif event.button.id == "tree_run_button":
            self._run_extraction_from_tree()
        elif event.button.id == "tree_back_button":
            self.query_one(TabbedContent).active = "settings_tab"

    def action_run_extraction(self) -> None:
        """Handle run extraction action from Settings tab."""
        # Switch to Tree tab to select folders
        self.query_one(TabbedContent).active = "tree_tab"

    def _run_extraction_from_tree(self) -> None:
        """
        Run extraction from the Tree tab.

        Handles edge cases:
        - No folders selected and include_root_files=False -> block run
        - Root-files-only selection -> one unit flow works
        - Unit extraction exception -> log/warn and continue
        - Cancellation -> clean exit
        - Progress never exceeds total_units
        """
        # Edge case: No folders selected and root files not included
        if not self.session.selected_folders and not self.session.include_root_files:
            self.bell()
            status = self.query_one("#extraction_status", Static)
            status.update("[bold red]Please select at least one folder or enable 'Include root files'.[/bold red]")
            return

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

        # Prepare progress UI
        progress_container = self.query_one("#progress_container", Vertical)
        progress_container.remove_children()

        # Add progress bar
        progress_bar = ProgressBar(total=100, show_percentage=True, show_eta=False)
        progress_container.mount(progress_bar)

        # Add progress text
        progress_text = Static("", classes="progress-text")
        progress_container.mount(progress_text)

        # Update status
        status = self.query_one("#extraction_status", Static)
        status.update("[bold cyan]Starting extraction...[/bold cyan]")

        # Run extraction
        self._execute_extraction(progress_bar, progress_text, status)

    def _execute_extraction(
        self,
        progress_bar: ProgressBar,
        progress_text: Static,
        status: Static
    ) -> None:
        """
        Execute the extraction with progress updates.

        Args:
            progress_bar: The progress bar widget to update
            progress_text: The progress text widget to update
            status: The status widget to update
        """
        # Reset progress
        self.session._completed_units = 0
        run_ref = str(uuid.uuid4())
        run_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        total_files_extracted = 0

        # Disable the Run button during extraction
        run_button = self.query_one("#tree_run_button", Button)
        run_button.disabled = True

        def update_progress():
            """Update the progress bar and text."""
            progress = self.session.progress_fraction()
            progress_bar.advance(progress * 100 - progress_bar.progress)
            progress_text.update(
                f"[cyan]Processing: {self.session.completed_units}/{self.session.total_units} units[/cyan]"
            )

        try:
            # Process folders
            for folder_path in sorted(list(self.session.selected_folders)):
                try:
                    folder_md, folder_count, char_count, word_count = file_handler.extract_code_from_folder(
                        folder_path,
                        self.session.exclude_large_files,
                        self.session.excluded_dirs,
                        self.session.max_file_size_mb,
                        self.session.excluded_filenames,
                        self.session.allowed_filenames,
                        self.session.allowed_extensions,
                    )

                    if folder_count > 0:
                        metadata = {
                            "run_ref": run_ref,
                            "run_timestamp": run_timestamp,
                            "folder_name": str(folder_path.relative_to(self.root_path)),
                            "file_count": folder_count,
                            "char_count": char_count,
                            "word_count": word_count,
                        }
                        if not self.session.dry_run:
                            file_handler.write_to_markdown_file(
                                folder_md, metadata, self.root_path, self.session.output_dir_name
                            )
                        total_files_extracted += folder_count

                        status.update(
                            f"[green]✓ Extracted {folder_count} file(s) from: "
                            f"{folder_path.relative_to(self.root_path)}[/green]"
                        )
                    else:
                        status.update(
                            f"[yellow]⚠ No extractable files in: {folder_path.relative_to(self.root_path)}[/yellow]"
                        )

                except Exception as e:
                    logging.warning(f"Could not extract from {folder_path}: {e}")
                    status.update(
                        f"[red]⚠ Error extracting {folder_path.relative_to(self.root_path)}: {e}[/red]"
                    )
                finally:
                    self.session.completed_units += 1
                    update_progress()

            # Process root files if selected
            if self.session.include_root_files:
                try:
                    root_display_name = f"root [{self.root_path.name}]"
                    root_md, root_count, char_count, word_count = file_handler.extract_code_from_root(
                        self.root_path,
                        self.session.exclude_large_files,
                        self.session.max_file_size_mb,
                        self.session.excluded_filenames,
                        self.session.allowed_filenames,
                        self.session.allowed_extensions,
                    )

                    if root_count > 0:
                        metadata = {
                            "run_ref": run_ref,
                            "run_timestamp": run_timestamp,
                            "folder_name": root_display_name,
                            "file_count": root_count,
                            "char_count": char_count,
                            "word_count": word_count,
                        }
                        if not self.session.dry_run:
                            file_handler.write_to_markdown_file(
                                root_md, metadata, self.root_path, self.session.output_dir_name
                            )
                        total_files_extracted += root_count

                        status.update(
                            f"[green]✓ Extracted {root_count} file(s) from root directory[/green]"
                        )
                    else:
                        status.update("[yellow]⚠ No extractable files in root directory[/yellow]")

                except Exception as e:
                    logging.warning(f"Could not extract from root: {e}")
                    status.update(f"[red]⚠ Error extracting root files: {e}[/red]")
                finally:
                    self.session.completed_units += 1
                    update_progress()

            # Final summary
            dry_run_suffix = " (dry-run preview)" if self.session.dry_run else ""
            if total_files_extracted > 0:
                status.update(
                    f"[bold green]✓ Extraction complete!{dry_run_suffix} "
                    f"Extracted {total_files_extracted} file(s) total.[/bold green]"
                )
                progress_text.update(
                    f"[green]Complete: {self.session.completed_units}/{self.session.total_units} units[/green]"
                )
            else:
                status.update(
                    f"[bold yellow]⚠ Extraction complete but no files matched criteria.{dry_run_suffix}[/bold yellow]"
                )

        except KeyboardInterrupt:
            # Handle cancellation
            status.update("[bold red]Extraction cancelled by user.[/bold red]")
        finally:
            # Re-enable the Run button
            run_button.disabled = False


def launch_tui() -> None:
    """Launch the Textual TUI application."""
    app = CodebaseExtractorApp()
    app.run()
