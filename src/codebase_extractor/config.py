from pathlib import Path
import sys

# --- CONFIGURATION ---
GITHUB_URL = "https://github.com/lukaszlekowski/codebase-extractor"
LINKEDIN_URL = "https://www.linkedin.com/in/lukasz-lekowski"
PYPI_URL = "https://pypi.org/project/codebase-extractor/"
SCRIPT_FILENAME = Path(sys.argv[0]).name
OUTPUT_DIR_NAME = "CODEBASE_EXTRACTS"

# --- FILE/FOLDER LISTS ---
EXCLUDED_DIRS = {
    # Standard exclusions
    "node_modules", "vendor", "__pycache__", "dist", "build", "target", ".next",
    ".git", ".svn", ".hg", ".vscode", ".idea", "venv", ".venv", ".dart_tool",
    # Flutter & Mobile specific exclusions
    ".dart_tool",  # Critical: Contains noisy build config
    ".gradle",     # Internal Gradle cache
    "Pods",        # iOS external dependencies
    "DerivedData", # iOS build artifacts
}
EXCLUDED_FILENAMES = {
    "package-lock.json", "yarn.lock", "composer.lock", ".env", "Podfile.lock",
}
ALLOWED_FILENAMES = {
# General
    "dockerfile", ".gitignore", ".htaccess", "makefile", ".dockerignore", ".env.example",
    # Mobile
    "podfile", "gemfile", "jenkinsfile", "gradlew",
}
ALLOWED_EXTENSIONS = {
# Web & General
    ".php", ".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
    ".py", ".rb", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".json", ".xml",
    ".yaml", ".yml", ".toml", ".ini", ".conf", ".md", ".txt", ".rst", ".twig",
    ".blade", ".handlebars", ".mustache", ".ejs", ".sql", ".graphql", ".gql", ".tf",
    
    # Flutter / Dart
    ".dart", ".arb",
    
    # Android
    ".gradle", ".properties",
    
    # iOS
    ".plist", ".xcconfig",
    
    # Scripts
    ".sh", ".bat",
}

# --- MAPPINGS & CONSTANTS ---
EXTENSION_LANG_MAP = {
    # Web & General
    ".js": "javascript", ".ts": "typescript", ".tsx": "tsx", ".py": "python",
    ".html": "html", ".css": "css", ".json": "json", ".md": "markdown", ".txt": "",
    ".sh": "bash", ".yml": "yaml", ".yaml": "yaml", ".php": "php", ".rb": "ruby",
    ".java": "java", ".c": "c", ".cpp": "cpp", ".cs": "csharp", ".go": "go",
    ".rs": "rust", ".vue": "vue", ".svelte": "svelte", ".sql": "sql",
    ".graphql": "graphql", ".gql": "graphql",
    
    # Mobile Specific
    ".dart": "dart",
    ".gradle": "groovy",
    ".plist": "xml",
    ".xcconfig": "properties",
    ".properties": "properties",
    ".arb": "json",
    ".bat": "batch",
}
MAX_FILE_SIZE_MB = 1
FILE_COUNT_WARNING_THRESHOLD = 1000
LOGO_BREAKPOINT = 144