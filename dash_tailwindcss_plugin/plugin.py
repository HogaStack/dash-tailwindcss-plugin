import logging
import os
import time
import uuid
from dash import Dash, hooks
from flask import Response, send_file
from typing import Any, Dict, List, Literal, Optional
from py_node_manager import get_logger
from .utils import dict_to_js_object, TailwindCommand


logger = get_logger(logging.getLogger(__name__))


class _TailwindCSSPlugin:
    """Main class for the Dash Tailwind CSS Plugin."""

    def __init__(
        self,
        mode: Literal['offline', 'online'] = 'offline',
        tailwind_version: Literal['3', '4'] = '3',
        content_path: List[str] = ['**/*.py'],
        plugin_tmp_dir: str = '_tailwind',
        input_css_path: str = '_tailwind/tailwind_input.css',
        output_css_path: str = '_tailwind/tailwind.css',
        config_js_path: str = '_tailwind/tailwind.config.js',
        cdn_url: str = 'https://cdn.tailwindcss.com',
        download_node: bool = False,
        node_version: str = '18.17.0',
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
        clean_after: bool = True,
        skip_build_if_recent: bool = True,
        skip_build_time_threshold: int = 5,
    ) -> None:
        """
        Initialize Tailwind CSS plugin with specified configuration.

        Args:
            mode (Literal['offline', 'online']): Mode of operation ('offline' or 'online')
            tailwind_version (Literal['3', '4']): Version of Tailwind CSS
            content_path (List[str]): Glob patterns for files to scan for Tailwind classes
            plugin_tmp_dir (str): Temporary directory for plugin files
            input_css_path (str): Path to input CSS file
            output_css_path (str): Path to output CSS file
            config_js_path (str): Path to Tailwind config file
            cdn_url (str): CDN URL for online mode, need to correspond with tailwind_version
            download_node (bool): Whether to download Node.js if not found
            node_version (str): Node.js version to download if download_node is True
            tailwind_theme_config (Optional[Dict[Any, Any]]): Custom theme configuration for Tailwind CSS
            clean_after (bool): Whether to clean up generated files after build
            skip_build_if_recent (bool): Whether to skip build if CSS file was recently generated
            skip_build_time_threshold (int): Time threshold in seconds to consider CSS file as recent

        Returns:
            None
        """
        if mode == 'offline':
            self.tailwind_command = TailwindCommand(
                tailwind_version=tailwind_version,
                content_path=content_path,
                plugin_tmp_dir=plugin_tmp_dir,
                input_css_path=input_css_path,
                output_css_path=output_css_path,
                config_js_path=config_js_path,
                is_cli=False,
                download_node=download_node,
                node_version=node_version,
                theme_config=tailwind_theme_config,
            )
        self.mode = mode
        self.tailwind_version = tailwind_version
        self.content_path = content_path
        self.plugin_tmp_dir = plugin_tmp_dir
        self.input_css_path = input_css_path
        self.output_css_path = output_css_path
        self.config_js_path = config_js_path
        self.cdn_url = cdn_url
        self.download_node = download_node
        self.node_version = node_version
        self.tailwind_theme_config = tailwind_theme_config or {}
        self.clean_after = clean_after
        self.skip_build_if_recent = skip_build_if_recent
        self.skip_build_time_threshold = skip_build_time_threshold
        if mode == 'online' and tailwind_version == '4' and cdn_url == 'https://cdn.tailwindcss.com':
            new_cdn_url = 'https://registry.npmmirror.com/@tailwindcss/browser/4/files/dist/index.global.js'
            logger.warning(
                f'⚠️ Warning: {cdn_url} does not support tailwindcss 4.x version and has been replaced with {new_cdn_url} by default. '
                f'Or provide a new cdn_url that supports version 4.x.'
            )
            self.cdn_url = new_cdn_url

    def _process_online_html(self, index_string: str) -> str:
        """
        Process HTML string for online mode by adding Tailwind CSS CDN script.

        Args:
            index_string (str): Original HTML string

        Returns:
            str: Modified HTML string with Tailwind CSS CDN script
        """
        # Create Tailwind CSS CDN script with theme configuration
        tailwind_script = f'<script src="{self.cdn_url}"></script>\n'

        # Add theme configuration script if provided
        if self.tailwind_theme_config:
            # Convert Python dict to JavaScript object using the utility function
            theme_config_js = dict_to_js_object(self.tailwind_theme_config)

            # Add configuration script
            config_script = f"""<script>
  tailwind.config = {{
    theme: {{
      extend: {theme_config_js}
    }}
  }};
</script>
"""
            tailwind_script += config_script

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

    def _should_skip_build(self) -> bool:
        """
        Check if the build should be skipped based on the skip_build_if_recent setting

        Returns:
            bool: True if the build should be skipped, False otherwise
        """
        # Check if CSS file exists and was generated recently (within threshold seconds)
        if self.skip_build_if_recent and os.path.exists(self.output_css_path):
            file_mod_time = os.path.getmtime(self.output_css_path)
            current_time = time.time()
            if current_time - file_mod_time < self.skip_build_time_threshold:
                logger.info(
                    f'⚡ CSS file {self.output_css_path} was generated recently '
                    f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                )
                return True
        return False

    def _build_tailwindcss(self) -> None:
        """
        Build Tailwind CSS using Tailwind CLI

        Returns:
            None
        """
        built = self.tailwind_command.init().install().build()
        if self.clean_after:
            built.clean()

    def _serve_tailwindcss(self) -> Response:
        """
        Serve Tailwind CSS file.

        Returns:
            Response: CSS file response or 404 if file not found
        """
        # Check if the CSS file exists
        if os.path.exists(self.output_css_path):
            try:
                # Return the CSS file
                return send_file(self.output_css_path, mimetype='text/css')
            except Exception:
                # If there's an error return the file, return the content directly
                with open(self.output_css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                return Response(css_content, mimetype='text/css')
        else:
            # Return 404 if file not found
            return Response('CSS file not found', status=404, mimetype='text/plain')

    def _process_offline_html(self, built_tailwindcss_link: str, index_string: str) -> str:
        """
        Process HTML string for offline mode by adding Tailwind CSS link.

        Args:
            built_tailwindcss_link (str): Link to the built Tailwind CSS file
            index_string (str): Original HTML string

        Returns:
            str: Modified HTML string with Tailwind CSS link
        """
        # Insert Tailwind CSS link into the head section
        tailwindcss_link = f'<link rel="stylesheet" href="{built_tailwindcss_link}"></link>\n'

        # Look for the closing head tag and insert the link before it
        if '</head>' in index_string:
            index_string = index_string.replace('</head>', f'{tailwindcss_link}</head>')
        # If no head tag, look for opening body tag and insert before it
        elif '<body>' in index_string:
            index_string = index_string.replace('<body>', f'<head>\n{tailwindcss_link}</head>\n<body>')
        # If neither head nor body tag, append to the beginning
        else:
            index_string = f'<head>\n{tailwindcss_link}</head>\n' + index_string

        return index_string

    def setup_online_mode(self):
        """
        Setup Tailwind CSS using CDN

        Returns:
            None
        """

        @hooks.index()
        def add_tailwindcss_cdn(index_string: str) -> str:
            return self._process_online_html(index_string)

    def setup_offline_mode(self):
        """
        Setup Tailwind CSS using offline build process

        Returns:
            None
        """
        built_tailwindcss_vesrion = str(uuid.uuid4()).replace('-', '')
        built_tailwindcss_link = f'/_tailwind/tailwind@{built_tailwindcss_vesrion}.css'
        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_css_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate Tailwind CSS on app startup
        @hooks.setup(priority=3)
        def generate_tailwindcss(app: Dash):
            if self._should_skip_build():
                return
            self._build_tailwindcss()

        @hooks.route(name=built_tailwindcss_link, methods=('GET',), priority=2)
        def serve_tailwindcss():
            return self._serve_tailwindcss()

        @hooks.index(priority=1)
        def add_tailwindcss_link(index_string: str) -> str:
            return self._process_offline_html(built_tailwindcss_link, index_string)


def setup_tailwindcss_plugin(
    mode: Literal['online', 'offline'] = 'offline',
    tailwind_version: Literal['3', '4'] = '3',
    content_path: List[str] = ['**/*.py'],
    plugin_tmp_dir: str = '_tailwind',
    input_css_path: str = '_tailwind/tailwind_input.css',
    output_css_path: str = '_tailwind/tailwind.css',
    config_js_path: str = '_tailwind/tailwind.config.js',
    cdn_url: str = 'https://cdn.tailwindcss.com',
    download_node: bool = False,
    node_version: str = '18.17.0',
    tailwind_theme_config: Optional[Dict[Any, Any]] = None,
    clean_after: bool = True,
    skip_build_if_recent: bool = True,
    skip_build_time_threshold: int = 5,
):
    """
    Initialize Tailwind CSS plugin with specified mode and configuration.

    Args:
        mode (Literal['online', 'offline']): Mode of operation ('offline' or 'online')
        tailwind_version (Literal['3', '4']): Version of Tailwind CSS
        content_path (List[str]): Glob patterns for files to scan for Tailwind classes
        plugin_tmp_dir (str): Temporary directory for plugin files
        input_css_path (str): Path to input CSS file
        output_css_path (str): Path to output CSS file
        config_js_path (str): Path to Tailwind config file
        cdn_url (str): CDN URL for online mode, need to correspond with tailwind_version
        download_node (bool): Whether to download Node.js if not found
        node_version (str): Node.js version to download if download_node is True
        tailwind_theme_config (Optional[Dict[Any, Any]]): Custom theme configuration for Tailwind CSS
        clean_after (bool): Whether to clean up generated files after build
        skip_build_if_recent (bool): Whether to skip build if CSS file was recently generated
        skip_build_time_threshold (int): Time threshold in seconds to consider CSS file as recent
    """
    plugin = _TailwindCSSPlugin(
        mode=mode,
        tailwind_version=tailwind_version,
        content_path=content_path,
        plugin_tmp_dir=plugin_tmp_dir,
        input_css_path=input_css_path,
        output_css_path=output_css_path,
        config_js_path=config_js_path,
        cdn_url=cdn_url,
        download_node=download_node,
        node_version=node_version,
        tailwind_theme_config=tailwind_theme_config,
        clean_after=clean_after,
        skip_build_if_recent=skip_build_if_recent,
        skip_build_time_threshold=skip_build_time_threshold,
    )

    if mode == 'online':
        plugin.setup_online_mode()
    else:
        plugin.setup_offline_mode()
