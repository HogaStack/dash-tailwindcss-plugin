import argparse
import json
import os
import subprocess
import warnings
from typing import Optional, Dict, Any
from .utils import (
    check_or_download_nodejs,
    clean_generated_files,
    create_default_input_tailwindcss,
    create_default_tailwindcss_config,
    get_command_alias_by_platform,
    get_build_tailwind_cmd,
    install_tailwindcss,
)


class _TailwindCLI:
    """
    CLI class for the Dash TailwindCSS plugin
    """

    def __init__(self):
        """
        Initialize the CLI tool
        """
        pass

    def run(self):
        """
        Main entry point for the CLI tool

        Returns:
            None
        """
        parser = argparse.ArgumentParser(description='Dash TailwindCSS Plugin CLI')
        parser.add_argument(
            'command',
            choices=['init', 'build', 'watch', 'clean'],
            help='Command to execute',
        )
        parser.add_argument(
            '--content-path',
            action='append',
            help='Glob pattern for files to scan for Tailwind classes. Can be specified multiple times.',
        )
        parser.add_argument(
            '--input-css-path',
            default='./.tailwind/tailwind_input.css',
            help='Path to input CSS file',
        )
        parser.add_argument(
            '--output-css-path',
            default='./.tailwind/tailwind.css',
            help='Path to output CSS file',
        )
        parser.add_argument(
            '--config-js-path',
            default='./.tailwind/tailwind.config.js',
            help='Path to Tailwind config file',
        )
        parser.add_argument(
            '--tailwind-theme-config',
            type=str,
            help='JSON string of custom theme configuration for Tailwind CSS',
        )
        parser.add_argument(
            '--clean-after',
            action='store_true',
            help='Clean up generated files after build',
        )
        parser.add_argument(
            '--download-node',
            action='store_true',
            help='Download Node.js if not found in PATH',
        )
        parser.add_argument(
            '--node-version',
            default='18.17.0',
            help='Node.js version to download (if --download-node is used)',
        )

        args = parser.parse_args()

        # Parse theme config if provided
        theme_config = None
        if args.tailwind_theme_config:
            try:
                theme_config = json.loads(args.tailwind_theme_config)
            except json.JSONDecodeError as e:
                warnings.warn(f'Invalid JSON for theme config: {e}')
                theme_config = None

        if args.command == 'init':
            self.init_tailwindcss_config(
                content_path=args.content_path if args.content_path else ['**/*.py'],
                input_css_path=args.input_css_path,
                config_js_path=args.config_js_path,
                download_node=args.download_node,
                node_version=args.node_version,
                tailwind_theme_config=theme_config,
            )
        elif args.command == 'build':
            self.build_tailwindcss(
                content_path=args.content_path if args.content_path else ['**/*.py'],
                input_css_path=args.input_css_path,
                output_css_path=args.output_css_path,
                config_js_path=args.config_js_path,
                clean_after=args.clean_after,
                download_node=args.download_node,
                node_version=args.node_version,
                tailwind_theme_config=theme_config,
            )
        elif args.command == 'watch':
            self.watch_tailwindcss(
                content_path=args.content_path if args.content_path else ['**/*.py'],
                input_css_path=args.input_css_path,
                output_css_path=args.output_css_path,
                config_js_path=args.config_js_path,
                download_node=args.download_node,
                node_version=args.node_version,
                tailwind_theme_config=theme_config,
            )
        elif args.command == 'clean':
            clean_generated_files(
                input_css_path=args.input_css_path,
                config_js_path=args.config_js_path,
                is_cli=True,
            )

    def init_tailwindcss_config(
        self,
        content_path: list,
        input_css_path: str,
        config_js_path: str,
        download_node: bool,
        node_version: str,
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
    ):
        """
        Initialize a new Tailwind config file

        Args:
            content_path (list): Glob patterns for files to scan for Tailwind classes
            input_css_path (str): Path to input CSS file
            config_js_path (str): Path to the Tailwind config file
            download_node (bool): Whether to download Node.js if not found in PATH
            node_version (str): Node.js version to download (if download_node is True)
            tailwind_theme_config (Optional[Dict[Any, Any]], optional): Custom theme configuration for Tailwind CSS

        Returns:
            None
        """
        try:
            # Check if Node.js is available
            node_path = check_or_download_nodejs(download_node=download_node, node_version=node_version, is_cli=True)

            # Install Tailwind CSS if not already installed
            print('Start intializing Tailwind CSS...')
            install_tailwindcss(node_path)

            # Create default Tailwind config file with custom content
            print('Creating Tailwind config...')
            if not os.path.exists(config_js_path):
                create_default_tailwindcss_config(content_path, config_js_path, tailwind_theme_config)

            # Create default input CSS file
            if not os.path.exists(input_css_path):
                create_default_input_tailwindcss(input_css_path)

            print('Tailwind CSS initialized successfully!')
            print(f'Config file created at: {config_js_path}')
            print(f'Input CSS file created at: {input_css_path}')
            print('You can now customize your config file and build CSS with:')
            print('  dash-tailwindcss-plugin build')

        except subprocess.CalledProcessError as e:
            warnings.warn(f'Error initializing Tailwind CSS: {e}')
        except Exception as e:
            warnings.warn(f'Error: {e}')

    def build_tailwindcss(
        self,
        content_path: list,
        input_css_path: str,
        output_css_path: str,
        config_js_path: str,
        clean_after: bool,
        download_node: bool,
        node_version: str,
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
    ):
        """
        Build Tailwind CSS

        Args:
            content_path (list): Glob patterns for files to scan for Tailwind classes
            input_css_path (str): Path to input CSS file
            output_css_path (str): Path to the output CSS file
            config_js_path (str): Path to the Tailwind config file
            clean_after (bool): Whether to clean up generated files after build
            download_node (bool): Whether to download Node.js if not found in PATH
            node_version (str): Node.js version to download (if download_node is True)
            tailwind_theme_config (Optional[Dict[Any, Any]], optional): Custom theme configuration for Tailwind CSS

        Returns:
            None
        """
        try:
            # Check if Node.js is available or download it if requested
            node_path = check_or_download_nodejs(download_node=download_node, node_version=node_version, is_cli=True)

            # Check if Tailwind CSS is installed
            install_tailwindcss(node_path)

            # Check and create config file if it doesn't exist
            if not os.path.exists(config_js_path):
                print(f'Config file {config_js_path} not found. Creating default config...')
                create_default_tailwindcss_config(content_path, config_js_path, tailwind_theme_config)
                print(f'Default config file created at: {config_js_path}')

            # Check and create input CSS file if it doesn't exist
            if not os.path.exists(input_css_path):
                print(f'Input CSS file {input_css_path} not found. Creating default input CSS...')
                create_default_input_tailwindcss(input_css_path)
                print(f'Default input CSS file created at: {input_css_path}')

            # Build CSS
            print(f'Building Tailwind CSS from {input_css_path} to {output_css_path}...')
            cmd = get_build_tailwind_cmd(node_path, input_css_path, output_css_path, config_js_path)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                warnings.warn(f'Tailwind CSS build failed: {result.stderr}')
            else:
                print('Build completed successfully!')
                print(f'Tailwind CSS built successfully to {output_css_path}')

            # Clean up if requested
            if clean_after:
                clean_generated_files(
                    input_css_path=input_css_path,
                    config_js_path=config_js_path,
                    is_cli=True,
                )

        except subprocess.CalledProcessError as e:
            warnings.warn(f'Error building Tailwind CSS: {e}')
        except Exception as e:
            warnings.warn(f'Error: {e}')

    def watch_tailwindcss(
        self,
        content_path: list,
        input_css_path: str,
        output_css_path: str,
        config_js_path: str,
        download_node: bool,
        node_version: str,
        tailwind_theme_config: Optional[Dict[Any, Any]] = None,
    ):
        """
        Watch for changes and rebuild Tailwind CSS

        Args:
            content_path (list): Glob patterns for files to scan for Tailwind classes
            input_css_path (str): Path to input CSS file
            output_css_path (str): Path to the output CSS file
            config_js_path (str): Path to the Tailwind config file
            download_node (bool): Whether to download Node.js if not found in PATH
            node_version (str): Node.js version to download (if download_node is True)
            tailwind_theme_config (Optional[Dict[Any, Any]], optional): Custom theme configuration for Tailwind CSS

        Returns:
            None
        """
        try:
            # Check if Node.js is available or download it if requested
            node_path = check_or_download_nodejs(download_node=download_node, node_version=node_version, is_cli=True)

            # Check if Tailwind CSS is installed
            install_tailwindcss(node_path)

            # Check and create config file if it doesn't exist
            if not os.path.exists(config_js_path):
                print(f'Config file {config_js_path} not found. Creating default config...')
                create_default_tailwindcss_config(content_path, config_js_path, tailwind_theme_config)
                print(f'Default config file created at: {config_js_path}')

            # Check and create input CSS file if it doesn't exist
            if not os.path.exists(input_css_path):
                print(f'Input CSS file {input_css_path} not found. Creating default input CSS...')
                create_default_input_tailwindcss(input_css_path)
                print(f'Default input CSS file created at: {input_css_path}')

            # Watch and build CSS
            print(f'Watching {input_css_path} for changes...')
            if node_path:
                # When using downloaded Node.js, we need to use npx from the same directory
                node_dir = os.path.dirname(node_path)
                npx_path = os.path.join(node_dir, get_command_alias_by_platform('npx'))
                # If npx doesn't exist in the same directory, check in bin subdirectory
                if not os.path.exists(npx_path):
                    npx_path = os.path.join(node_dir, 'bin', get_command_alias_by_platform('npx'))

                # If we found npx, use it with node, otherwise fallback to just npx
                if os.path.exists(npx_path):
                    cmd = [
                        node_path,
                        npx_path,
                        'tailwindcss',
                        '-i',
                        input_css_path,
                        '-o',
                        output_css_path,
                        '-c',
                        config_js_path,
                        '--watch',
                    ]
                else:
                    cmd = [
                        node_path,
                        get_command_alias_by_platform('npx'),
                        'tailwindcss',
                        '-i',
                        input_css_path,
                        '-o',
                        output_css_path,
                        '-c',
                        config_js_path,
                        '--watch',
                    ]
            else:
                cmd = [
                    get_command_alias_by_platform('npx'),
                    'tailwindcss',
                    '-i',
                    input_css_path,
                    '-o',
                    output_css_path,
                    '-c',
                    config_js_path,
                    '--watch',
                ]
            subprocess.run(cmd)

        except KeyboardInterrupt:
            print('\nWatch stopped.')
        except subprocess.CalledProcessError as e:
            warnings.warn(f'Error watching Tailwind CSS: {e}')
        except Exception as e:
            warnings.warn(f'Error: {e}')


def main():
    """
    CLI tool for the Dash TailwindCSS plugin
    """
    cli = _TailwindCLI()
    cli.run()


if __name__ == '__main__':
    main()
