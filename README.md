# Dash TailwindCSS Plugin

A plugin for integrating TailwindCSS with Plotly Dash applications using Dash 3.x hooks. Supports both Tailwind CSS v3 and v4.

[![Tests](https://github.com/HogaStack/dash-tailwindcss-plugin/workflows/Tests/badge.svg)](https://github.com/HogaStack/dash-tailwindcss-plugin/actions)
[![Coverage](https://codecov.io/gh/HogaStack/dash-tailwindcss-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/HogaStack/dash-tailwindcss-plugin)
[![Python Version](https://img.shields.io/pypi/pyversions/dash-tailwindcss-plugin)](https://pypi.org/project/dash-tailwindcss-plugin/)
[![PyPI](https://img.shields.io/pypi/v/dash-tailwindcss-plugin)](https://pypi.org/project/dash-tailwindcss-plugin/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub](https://shields.io/badge/license-MIT-informational)](https://github.com/HogaStack/dash-tailwindcss-plugin/blob/main/LICENSE)

English | [简体中文](./README-zh_CN.md)

## Features

1. **Online Mode**: Uses Tailwind CSS CDN for quick setup
2. **Offline Mode**: Builds optimized CSS using Tailwind CLI
3. **Automatic Build**: Automatically builds Tailwind CSS on app startup
4. **Flexible Configuration**: Customizable input/output paths and config files
5. **Automatic Cleanup**: Automatically removes generated files to keep directory clean
6. **Node.js Management**: Automatically download and use specific Node.js versions
7. **Class-based Architecture**: Clean, object-oriented design for better maintainability
8. **Comprehensive Testing**: Full test coverage including unit tests, integration tests, and Dash-specific tests
9. **Custom Theme Configuration**: Extend Tailwind's default theme with custom colors, spacing, and more
10. **Configurable Cleanup**: Control whether intermediate files are cleaned up after build
11. **Tailwind CSS v3 & v4 Support**: Supports both Tailwind CSS version 3 and 4

## Installation

```bash
pip install dash-tailwindcss-plugin
```

Or for development:

```bash
pip install -e .
```

For development with all dependencies (including test dependencies):

```bash
pip install -e .[dev]
```

## Usage

### Online Mode (CDN)

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Initialize with CDN mode (default is Tailwind CSS v3)
setup_tailwindcss_plugin(mode="online")

# Or specify Tailwind CSS version (v3 or v4)
# setup_tailwindcss_plugin(mode="online", tailwind_version="4")

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Hello, TailwindCSS!", className="text-3xl font-bold text-blue-600"),
    html.P("This is styled with Tailwind CSS CDN.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### Offline Mode (CLI)

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Initialize with offline mode (default)
setup_tailwindcss_plugin(
    mode="offline",
    tailwind_version="3",  # Specify Tailwind CSS version (v3 or v4)
    content_path=["**/*.py"],  # Files to scan for Tailwind classes
    plugin_tmp_dir="_tailwind",  # Temporary directory for plugin files
    output_css_path="_tailwind/tailwind.css",  # Output CSS file
    config_js_path="_tailwind/tailwind.config.js",  # Tailwind config file
    download_node=True,  # Download Node.js if not found
    node_version="18.17.0"  # Specify Node.js version to download
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Hello, TailwindCSS!", className="text-3xl font-bold text-blue-600"),
    html.P("This is styled with locally built Tailwind CSS.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### Custom Plugin Temporary Directory

You can specify a custom temporary directory for plugin files:

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Initialize with custom plugin temporary directory
setup_tailwindcss_plugin(
    mode="offline",
    plugin_tmp_dir="_my_tailwind",  # Custom temporary directory
    input_css_path="_my_tailwind/input.css",
    output_css_path="_my_tailwind/output.css",
    config_js_path="_my_tailwind/config.js"
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Custom Directory", className="text-3xl font-bold text-green-600"),
    html.P("This uses a custom temporary directory.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### Control Build Skip Behavior

You can control whether to skip rebuilding if CSS was recently generated:

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Initialize with custom skip build parameters
setup_tailwindcss_plugin(
    mode="offline",
    skip_build_if_recent=True,  # Skip build if CSS was recently generated
    skip_build_time_threshold=10  # Consider CSS recent if generated within 10 seconds
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Smart Rebuild", className="text-3xl font-bold text-purple-600"),
    html.P("This uses smart rebuild behavior.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### Custom Theme Configuration

You can extend Tailwind's default theme by providing a custom theme configuration:

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Define custom theme configuration
theme_config = {
    "colors": {
        "brand": {
            "50": "#eff6ff",
            "100": "#dbeafe",
            "200": "#bfdbfe",
            "300": "#93c5fd",
            "400": "#60a5fa",
            "500": "#3b82f6",
            "600": "#2563eb",
            "700": "#1d4ed8",
            "800": "#1e40af",
            "900": "#1e3a8a"
        }
    },
    "borderRadius": {
        "none": "0px",
        "sm": "0.125rem",
        "DEFAULT": "0.25rem",
        "md": "0.375rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        "full": "9999px"
    }
}

# Initialize with custom theme configuration
setup_tailwindcss_plugin(
    mode="offline",
    tailwind_theme_config=theme_config
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Custom Theme", className="text-3xl font-bold text-brand-500"),
    html.P("This uses a custom brand color.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### Control Cleanup Behavior

By default, the plugin cleans up intermediate files after building. You can disable this behavior:

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# Initialize with cleanup disabled
setup_tailwindcss_plugin(
    mode="offline",
    clean_after=False  # Keep intermediate files after build
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("No Cleanup", className="text-3xl font-bold text-blue-600"),
    html.P("Intermediate files will be kept after build.", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

## Project Structure

```bash
dash-tailwindcss-plugin/
├── .github/
│   └── workflows/
│       └── test.yml         # GitHub Actions workflow for testing
├── dash_tailwindcss_plugin/
│   ├── __init__.py          # Exports main plugin function
│   ├── plugin.py            # Main plugin implementation with _TailwindCSSPlugin class
│   ├── cli.py               # Command-line interface with _TailwindCLI class
│   └── utils.py             # Utility functions for Node.js management, file operations, etc.
├── tests/
│   ├── README.md            # English test documentation
│   ├── README-zh_CN.md      # Chinese test documentation
│   ├── conftest.py          # Pytest configuration fixtures
│   ├── test_cli.py          # Unit tests for CLI interface
│   ├── test_dash_integration.py  # Dash end-to-end integration tests
│   ├── test_plugin.py       # Unit tests for plugin core functionality
│   └── test_utils.py        # Unit tests for utility functions
├── example_app.py           # Example Dash application
├── requirements-dev.txt     # Development and test dependencies
├── pyproject.toml           # Build configuration
├── pytest.ini               # Pytest configuration
├── ruff.toml                # Ruff configuration (linting)
├── README.md                # English README file
└── README-zh_CN.md          # Chinese README file
```

## Requirements

- Python 3.8+
- Dash 3.0+
- Node.js 12+ (for offline mode, optional if using download_node feature)

## How It Works

### Online Mode

- Adds Tailwind CSS CDN script to the app's HTML head using `hooks.index()`
- No build process required
- Larger CSS file (includes all Tailwind classes)
- Supports both Tailwind CSS v3 (default CDN: <https://cdn.tailwindcss.com>) and v4 (default CDN: <https://registry.npmmirror.com/@tailwindcss/browser/4/files/dist/index.global.js>)

### Offline Mode

- Uses `hooks.setup(priority=3)` to build Tailwind CSS on app startup
- Uses `hooks.route(name=built_tailwindcss_link, methods=('GET',), priority=2)` to serve the generated CSS file
- Uses `hooks.index(priority=1)` to inject the CSS link into the HTML head
- Automatically installs Tailwind CLI if not present
- Scans specified files for Tailwind classes to create optimized CSS
- Automatically downloads Node.js if requested and not found in PATH
- Automatically cleans up temporary files after build (unless disabled)
- **Smart Rebuild**: Skips rebuilding if CSS file was generated within the last 5 seconds
- Supports both Tailwind CSS v3 and v4 with appropriate CLI packages

## Configuration

The plugin accepts the following parameters:

- `mode`: "online" or "offline" (default: "offline")
- `tailwind_version`: "3" or "4" (default: "3")
- `content_path`: Glob patterns for files to scan (default: ["**/*.py"])
- `plugin_tmp_dir`: Temporary directory for plugin files (default: "_tailwind")
- `input_css_path`: Path to input CSS file (default: "_tailwind/tailwind_input.css")
- `output_css_path`: Path to output CSS file (default: "_tailwind/tailwind.css")
- `config_js_path`: Path to Tailwind config file (default: "_tailwind/tailwind.config.js")
- `cdn_url`: CDN URL for online mode (default: "<https://cdn.tailwindcss.com>")
- `download_node`: Whether to download Node.js if not found (default: False)
- `node_version`: Node.js version to download if download_node is True (default: "18.17.0")
- `tailwind_theme_config`: Dictionary of custom theme configuration for Tailwind CSS (default: None)
- `clean_after`: Whether to clean up generated files after build (default: True)
- `skip_build_if_recent`: Whether to skip build if CSS file was recently generated (default: True)
- `skip_build_time_threshold`: Time threshold in seconds to consider CSS file as recent (default: 5)

## Development

1. Clone the repository
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Install in development mode: `pip install -e .`
4. Run example: `python example_app.py`

## Running Tests

```bash
# Install development dependencies (includes test dependencies)
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_plugin.py
python -m pytest tests/test_utils.py
python -m pytest tests/test_cli.py
python -m pytest tests/test_dash_integration.py

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ --cov=dash_tailwindcss_plugin --cov-report=html
```

See [tests/README.md](tests/README.md) for more detailed information about running tests.

## Building the Package

```bash
python -m build
```

This will create both source distribution and wheel files in the `dist/` directory.

## CLI Tool

The package includes a command-line interface:

```bash
dash-tailwindcss-plugin init              # Initialize Tailwind config
dash-tailwindcss-plugin build             # Build CSS manually
dash-tailwindcss-plugin watch             # Watch for changes
dash-tailwindcss-plugin clean             # Clean up generated files
```

### CLI Options

All commands support the following options:

- `--tailwind-version VERSION`: Version of Tailwind CSS to use (3 or 4) (default: "3")
- `--content-path INPUT`: Glob pattern for files to scan for Tailwind classes. Can be specified multiple times. (default: ["**/*.py"])
- `--plugin-tmp-dir PATH`: Temporary directory for plugin files (default: "./_tailwind")
- `--input-css-path PATH`: Path to input CSS file (default: "./_tailwind/tailwind_input.css")
- `--output-css-path OUTPUT`: Path to output CSS file (default: "./_tailwind/tailwind.css")
- `--config-js-path CONFIG`: Path to Tailwind config file (default: "./_tailwind/tailwind.config.js")
- `--tailwind-theme-config JSON`: JSON string of custom theme configuration for Tailwind CSS
- `--download-node`: Download Node.js if not found in PATH
- `--node-version VERSION`: Node.js version to download (if --download-node is used)
- `--clean-after`: Clean up generated files after build (only for build command)

Example:

```bash
dash-tailwindcss-plugin build --download-node --node-version 18.17.0
```

Example with multiple content paths:

```bash
dash-tailwindcss-plugin build --content-path "**/*.py" --content-path "**/*.js"
```

Example with custom theme configuration:

```bash
dash-tailwindcss-plugin build --tailwind-theme-config "{\"colors\":{\"brand\":{\"500\":\"#3b82f6\"}}}"
```

Example with Tailwind CSS v4:

```bash
dash-tailwindcss-plugin build --tailwind-version 4
```

Example with custom plugin temporary directory:

```bash
dash-tailwindcss-plugin build --plugin-tmp-dir "./my-tailwind" --input-css-path "./my-tailwind/input.css" --output-css-path "./my-tailwind/output.css" --config-js-path "./my-tailwind/config.js"
```

## Architecture

The plugin follows a clean, object-oriented architecture:

### Main Classes

1. **_TailwindCSSPlugin** ([plugin.py](./dash_tailwindcss_plugin/plugin.py)): Main plugin class that handles all Tailwind CSS integration
2. **_TailwindCLI** ([cli.py](./dash_tailwindcss_plugin/cli.py)): CLI tool class that provides command-line interface
3. **Utility Functions** ([utils.py](./dash_tailwindcss_plugin/utils.py)): Helper functions for Node.js management, file operations, etc.

### Entry Points

- `setup_tailwindcss_plugin()`: Main entry point for the plugin
- `main()`: Entry point for the CLI tool

This design ensures clean separation of concerns and makes the codebase easier to maintain and extend.
