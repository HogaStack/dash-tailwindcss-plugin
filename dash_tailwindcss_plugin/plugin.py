import os
import time
import uuid
from dash import Dash, hooks
from flask import Response, send_file
from typing import Any, Dict, List, Literal, Optional
from .utils import dict_to_js_object, logger, NodeManager, TailwindCommand


class _TailwindCSSPlugin:
    """Main class for the Dash Tailwind CSS Plugin."""

    def __init__(
        self,
        mode: Literal['offline', 'online'] = 'offline',
        tailwind_version: Literal['3', '4'] = '3',
        content_path: List[str] = ['**/*.py'],
        input_css_path: str = '.tailwind/tailwind_input.css',
        output_css_path: str = '.tailwind/tailwind.css',
        config_js_path: str = '.tailwind/tailwind.config.js',
        cdn_url: str = 'https://cdn.tailwindcss.com',
        download_node: bool = False,
        node_version: str = '18.17.0',
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
        clean_after: bool = True,
        skip_build_if_recent: bool = True,
        skip_build_time_threshold: int = 5,
    ):
        """
        Initialize Tailwind CSS plugin with specified configuration.

        Args:
            mode (Literal['offline', 'online']): Mode of operation ('offline' or 'online')
            tailwind_version (Literal['3', '4']): Version of Tailwind CSS
            content_path (List[str]): Glob patterns for files to scan for Tailwind classes
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
        if mode == 'offline':
            node_manager = NodeManager(
                download_node=download_node,
                node_version=node_version,
                is_cli=False,
            )
            self.tailwind_command = TailwindCommand(
                node_path=node_manager.node_path,
                node_env=node_manager.node_env,
                npm_path=node_manager.npm_path,
                npx_path=node_manager.npx_path,
                tailwind_version=tailwind_version,
                content_path=content_path,
                input_css_path=input_css_path,
                output_css_path=output_css_path,
                config_js_path=config_js_path,
                is_cli=False,
                theme_config=tailwind_theme_config,
            )
        self.mode = mode
        self.tailwind_version = tailwind_version
        self.content_path = content_path
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

    def setup_online_mode(self):
        """
        Setup Tailwind CSS using CDN

        Returns:
            None
        """

        @hooks.index()
        def add_tailwindcss_cdn(index_string: str) -> str:
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
            # Check if CSS file exists and was generated recently (within threshold seconds)
            if self.skip_build_if_recent and os.path.exists(self.output_css_path):
                file_mod_time = os.path.getmtime(self.output_css_path)
                current_time = time.time()
                if current_time - file_mod_time < self.skip_build_time_threshold:
                    logger.info(
                        f'⚡ CSS file {self.output_css_path} was generated recently '
                        f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                    )
                    return

            self._build_tailwindcss()

        @hooks.route(name=built_tailwindcss_link, methods=('GET',), priority=2)
        def serve_tailwindcss():
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

        @hooks.index(priority=1)
        def add_tailwindcss_link(index_string: str) -> str:
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

    def _build_tailwindcss(self):
        """
        Build Tailwind CSS using Tailwind CLI

        Returns:
            None
        """
        try:
            built = self.tailwind_command.init().install().build()
            if self.clean_after:
                built.clean()
        except Exception as e:
            logger.error(f'❌ Failed to build Tailwind CSS: {e}')


def setup_tailwindcss_plugin(
    mode: Literal['online', 'offline'] = 'offline',
    tailwind_version: Literal['3', '4'] = '3',
    content_path: List[str] = ['**/*.py'],
    input_css_path: str = '.tailwind/tailwind_input.css',
    output_css_path: str = '.tailwind/tailwind.css',
    config_js_path: str = '.tailwind/tailwind.config.js',
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
