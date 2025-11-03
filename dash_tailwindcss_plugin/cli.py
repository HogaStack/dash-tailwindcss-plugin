import argparse
import json
from .utils import logger, NodeManager, TailwindCommand


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
            '--tailwind-version',
            type=str,
            default='3',
            help='Version of Tailwind CSS to use',
        )
        parser.add_argument(
            '--content-path',
            action='append',
            help='Glob pattern for files to scan for Tailwind classes. Can be specified multiple times.',
        )
        parser.add_argument(
            '--plugin-tmp-dir',
            default='./_tailwind',
            help='Path to temporary directory for plugin files',
        )
        parser.add_argument(
            '--input-css-path',
            default='./_tailwind/tailwind_input.css',
            help='Path to input CSS file',
        )
        parser.add_argument(
            '--output-css-path',
            default='./_tailwind/tailwind.css',
            help='Path to output CSS file',
        )
        parser.add_argument(
            '--config-js-path',
            default='./_tailwind/tailwind.config.js',
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
                logger.error(f'Invalid JSON for theme config: {e}')
                theme_config = None

        node_manager = NodeManager(
            download_node=args.download_node,
            node_version=args.node_version,
            is_cli=True,
        )
        self.tailwind_command = TailwindCommand(
            node_path=node_manager.node_path,
            node_env=node_manager.node_env,
            npm_path=node_manager.npm_path,
            npx_path=node_manager.npx_path,
            tailwind_version=args.tailwind_version,
            content_path=args.content_path if args.content_path else ['**/*.py'],
            plugin_tmp_dir=args.plugin_tmp_dir,
            input_css_path=args.input_css_path,
            output_css_path=args.output_css_path,
            config_js_path=args.config_js_path,
            is_cli=True,
            theme_config=theme_config,
        )

        if args.command == 'init':
            self.init_tailwindcss(input_css_path=args.input_css_path, config_js_path=args.config_js_path)
        elif args.command == 'build':
            self.build_tailwindcss(clean_after=args.clean_after)
        elif args.command == 'watch':
            self.watch_tailwindcss()
        elif args.command == 'clean':
            self.clean_tailwindcss()

    def init_tailwindcss(self, input_css_path: str, config_js_path: str):
        """
        Initialize a new Tailwind config file

        Args:
            input_css_path (str): Path to input CSS file
            config_js_path (str): Path to the Tailwind config file

        Returns:
            None
        """
        self.tailwind_command.init().install()
        logger.info('📝 Next steps:')
        logger.info('1. Customize your config file if needed')
        logger.info('2. Build CSS with:')
        logger.info('dash-tailwindcss-plugin build')

    def build_tailwindcss(self, clean_after: bool):
        """
        Build Tailwind CSS

        Args:
            clean_after (bool): Whether to clean up generated files after build

        Returns:
            None
        """
        built = self.tailwind_command.init().install().build()
        # Clean up if requested
        if clean_after:
            built.clean()

    def watch_tailwindcss(self):
        """
        Watch for changes and rebuild Tailwind CSS

        Returns:
            None
        """
        self.tailwind_command.init().install().watch()

    def clean_tailwindcss(self):
        """
        Clean up generated files

        Returns:
            None
        """
        self.tailwind_command.clean()


def main():
    """
    CLI tool for the Dash TailwindCSS plugin
    """
    cli = _TailwindCLI()
    cli.run()


if __name__ == '__main__':
    main()
