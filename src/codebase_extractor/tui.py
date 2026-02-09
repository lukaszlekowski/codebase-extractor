"""
Textual TUI for Codebase Extractor.

Phase 1: Basic app structure with three tabs (Settings, Extensions, Tree).
This is a placeholder implementation - actual functionality will be added in later phases.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static, Button


class CodebaseExtractorApp(App):
    """Main Textual app for Codebase Extractor."""

    TITLE = "Codebase Extractor"
    SUB_TITLE = "v1.2.0 - Textual TUI"

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        yield TabbedContent(
            TabPane("Settings", Static(
                "\n\n"
                "  ╔═══════════════════════════════════════════════════════════╗\n"
                "  ║                    SETTINGS TAB                            ║\n"
                "  ║                      (PHASE 1)                             ║\n"
                "  ╠═══════════════════════════════════════════════════════════╣\n"
                "  ║                                                             ║\n"
                "  ║  Coming in later phases:                                    ║\n"
                "  ║  - Output directory configuration                           ║\n"
                "  ║  - Exclude large files toggle                               ║\n"
                "  ║  - Extraction mode selection (everything/specific)          ║\n"
                "  ║  - Depth settings for folder scanning                       ║\n"
                "  ║  - Instructions toggle                                      ║\n"
                "  ║                                                             ║\n"
                "  ╚═══════════════════════════════════════════════════════════╝\n"
            ), id="settings_tab"),
            TabPane("Extensions", Static(
                "\n\n"
                "  ╔═══════════════════════════════════════════════════════════╗\n"
                "  ║                   EXTENSIONS TAB                          ║\n"
                "  ║                      (PHASE 1)                             ║\n"
                "  ╠═══════════════════════════════════════════════════════════╣\n"
                "  ║                                                             ║\n"
                "  ║  Coming in later phases:                                    ║\n"
                "  ║  - Language/extension group selection (Flutter, JS, etc.)    ║\n"
                "  ║  - Custom extension allow/deny lists                        ║\n"
                "  ║  - Preset profiles for different project types              ║\n"
                "  ║                                                             ║\n"
                "  ╚═══════════════════════════════════════════════════════════╝\n"
            ), id="extensions_tab"),
            TabPane("Tree", Static(
                "\n\n"
                "  ╔═══════════════════════════════════════════════════════════╗\n"
                "  ║                      TREE TAB                              ║\n"
                "  ║                      (PHASE 1)                             ║\n"
                "  ╠═══════════════════════════════════════════════════════════╣\n"
                "  ║                                                             ║\n"
                "  ║  Coming in later phases:                                    ║\n"
                "  ║  - Visual directory tree representation                     ║\n"
                "  ║  - Multi-select folders for extraction                      ║\n"
                "  ║  - Root files selection                                     ║\n"
                "  ║  - Progress bar during extraction                           ║\n"
                "  ║                                                             ║\n"
                "  ╚═══════════════════════════════════════════════════════════╝\n"
            ), id="tree_tab"),
            id="main_tabs",
        )
        yield Footer()


def launch_tui() -> None:
    """Launch the Textual TUI application."""
    app = CodebaseExtractorApp()
    app.run()
