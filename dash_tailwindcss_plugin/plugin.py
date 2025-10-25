import os
import subprocess
import warnings
from typing import Optional, Dict, Any
from dash import Dash, hooks
from .utils import (
    check_or_download_nodejs,
    clean_generated_files,
    create_default_input_tailwindcss,
    create_default_tailwindcss_config,
    get_build_tailwind_cmd,
    install_tailwindcss,
)


class _TailwindCSSPlugin:
    """Main class for the Dash Tailwind CSS Plugin."""

    def __init__(
        self,
        mode: str = 'offline',
        content_path: list = ['**/*.py'],
        input_css_path: str = 'tailwind_input.css',
        output_css_path: str = 'assets/tailwind.css',
        config_js_path: str = 'tailwind.config.js',
        cdn_url: str = 'https://cdn.tailwindcss.com',
        download_node: bool = False,
        node_version: str = '18.17.0',
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
        clean_after: bool = False,
    ):
        """
        Initialize Tailwind CSS plugin with specified configuration.

        Args:
            mode (str): "online" or "offline"
            content_path (list): Glob patterns for files to scan for Tailwind classes
            input_css_path (str): Path to input CSS file
            output_css_path (str): Path to output CSS file
            config_js_path (str): Path to Tailwind config file
            cdn_url (str): CDN URL for online mode
            download_node (bool): Whether to download Node.js if not found
            node_version (str): Node.js version to download if download_node is True
            tailwind_theme_config (Optional[Dict[Any, Any]]): Custom theme configuration for Tailwind CSS
            clean_after (bool): Whether to clean up generated files after build
        """
        self.mode = mode
        self.content_path = content_path
        self.input_css_path = input_css_path
        self.output_css_path = output_css_path
        self.config_js_path = config_js_path
        self.cdn_url = cdn_url
        self.download_node = download_node
        self.node_version = node_version
        self.tailwind_theme_config = tailwind_theme_config or {}
        self.clean_after = clean_after

    def setup_online_mode(self):
        """
        Setup TailwindCSS using CDN

        Returns:
            None
        """

        @hooks.index()
        def add_tailwindcss_cdn(index_string: str) -> str:
            # Insert Tailwind CSS CDN script into the head section
            tailwind_script = f'<script src="{self.cdn_url}"></script>\n'

            # Look for the closing head tag and insert the script before it
            if '</head>' in index_string:
                index_string = index_string.replace('</head>', f'{tailwind_script}</head>')
            # If no head tag, look for opening body tag and insert before it
            elif '<body>' in index_string:
                index_string = index_string.replace('<body>', f'<head>\n{tailwind_script}</head>\n<body>')
            # If neither head nor body tag, append to the beginning
            else:
                index_string = f'<head>\n{tailwind_script}</head>\n' + index_string

            return index_string

    def setup_offline_mode(self):
        """
        Setup TailwindCSS using offline build process

        Returns:
            None
        """

        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_css_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate Tailwind CSS on app startup
        @hooks.setup()
        def generate_tailwindcss(app: Dash):
            self._build_tailwindcss()

    def _build_tailwindcss(self):
        """
        Build Tailwind CSS using Tailwind CLI

        Returns:
            None
        """
        try:
            # Check if Node.js is available or download it if requested
            node_path = check_or_download_nodejs(
                download_node=self.download_node,
                node_version=self.node_version,
                is_cli=False,
            )

            # Check if Tailwind CSS is installed
            install_tailwindcss(node_path)

            # Create default config if it doesn't exist
            if not os.path.exists(self.config_js_path):
                create_default_tailwindcss_config(self.content_path, self.config_js_path, self.tailwind_theme_config)

            # Create default input Tailwind CSS file if it doesn't exist
            if not os.path.exists(self.input_css_path):
                create_default_input_tailwindcss(self.input_css_path)

            # Build CSS
            cmd = get_build_tailwind_cmd(
                node_path,
                self.input_css_path,
                self.output_css_path,
                self.config_js_path,
            )

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                warnings.warn(f'Tailwind CSS build failed: {result.stderr}')

            # Clean up generated files to keep directory clean if requested
            if self.clean_after:
                clean_generated_files(
                    input_css_path=self.input_css_path,
                    config_js_path=self.config_js_path,
                    is_cli=False,
                )

        except Exception as e:
            warnings.warn(f'Failed to build Tailwind CSS: {e}')


def setup_tailwindcss_plugin(
    mode: str = 'offline',
    content_path: list = ['**/*.py'],
    input_css_path: str = 'tailwind_input.css',
    output_css_path: str = 'assets/tailwind.css',
    config_js_path: str = 'tailwind.config.js',
    cdn_url: str = 'https://cdn.tailwindcss.com',
    download_node: bool = False,
    node_version: str = '18.17.0',
    tailwind_theme_config: Optional[Dict[Any, Any]] = None,
    clean_after: bool = True,
):
    """
    Initialize Tailwind CSS plugin with specified mode and configuration.

    Args:
        mode (str): "online" or "offline"
        content_path (list): Glob patterns for files to scan for Tailwind classes
        input_css_path (str): Path to input CSS file
        output_css_path (str): Path to output CSS file
        config_js_path (str): Path to Tailwind config file
        cdn_url (str): CDN URL for online mode
        download_node (bool): Whether to download Node.js if not found
        node_version (str): Node.js version to download if download_node is True
        tailwind_theme_config (Optional[Dict[Any, Any]]): Custom theme configuration for Tailwind CSS
        clean_after (bool): Whether to clean up generated files after build
    """
    plugin = _TailwindCSSPlugin(
        mode=mode,
        content_path=content_path,
        input_css_path=input_css_path,
        output_css_path=output_css_path,
        config_js_path=config_js_path,
        cdn_url=cdn_url,
        download_node=download_node,
        node_version=node_version,
        tailwind_theme_config=tailwind_theme_config,
        clean_after=clean_after,
    )

    if mode == 'online':
        plugin.setup_online_mode()
    else:
        plugin.setup_offline_mode()
