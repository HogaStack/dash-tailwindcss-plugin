import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from dash_tailwindcss_plugin.cli import _TailwindCLI


class TestTailwindCLI:
    """Test cases for the _TailwindCLI class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = _TailwindCLI()
        assert cli is not None

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_init_command(self, mock_parse_args):
        """Test run method with init command."""
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss_config') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                content_path=['**/*.py'],
                input_css_path='./.tailwind/tailwind_input.css',
                config_js_path='./.tailwind/tailwind.config.js',
                download_node=False,
                node_version='18.17.0',
                tailwind_theme_config=None,
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_build_command(self, mock_parse_args):
        """Test run method with build command."""
        mock_args = MagicMock()
        mock_args.command = 'build'
        mock_args.content_path = None
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.output_css_path = './.tailwind/tailwind.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.clean_after = False
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'build_tailwindcss') as mock_build:
            cli.run()
            mock_build.assert_called_once_with(
                content_path=['**/*.py'],
                input_css_path='./.tailwind/tailwind_input.css',
                output_css_path='./.tailwind/tailwind.css',
                config_js_path='./.tailwind/tailwind.config.js',
                clean_after=False,
                download_node=False,
                node_version='18.17.0',
                tailwind_theme_config=None,
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_watch_command(self, mock_parse_args):
        """Test run method with watch command."""
        mock_args = MagicMock()
        mock_args.command = 'watch'
        mock_args.content_path = None
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.output_css_path = './.tailwind/tailwind.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'watch_tailwindcss') as mock_watch:
            cli.run()
            mock_watch.assert_called_once_with(
                content_path=['**/*.py'],
                input_css_path='./.tailwind/tailwind_input.css',
                output_css_path='./.tailwind/tailwind.css',
                config_js_path='./.tailwind/tailwind.config.js',
                download_node=False,
                node_version='18.17.0',
                tailwind_theme_config=None,
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_clean_command(self, mock_parse_args):
        """Test run method with clean command."""
        mock_args = MagicMock()
        mock_args.command = 'clean'
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.tailwind_theme_config = None
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch('dash_tailwindcss_plugin.cli.clean_generated_files') as mock_clean:
            cli.run()
            mock_clean.assert_called_once_with(
                input_css_path='./.tailwind/tailwind_input.css',
                config_js_path='./.tailwind/tailwind.config.js',
                is_cli=True,
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_theme_config(self, mock_parse_args):
        """Test run method with theme configuration."""
        theme_config_json = '{"colors": {"primary": "#ff0000"}}'
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = theme_config_json
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss_config') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                content_path=['**/*.py'],
                input_css_path='./.tailwind/tailwind_input.css',
                config_js_path='./.tailwind/tailwind.config.js',
                download_node=False,
                node_version='18.17.0',
                tailwind_theme_config={'colors': {'primary': '#ff0000'}},
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_invalid_theme_config(self, mock_parse_args):
        """Test run method with invalid theme configuration."""
        theme_config_json = '{"colors": {"primary": "#ff0000"'  # Invalid JSON
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './.tailwind/tailwind_input.css'
        mock_args.config_js_path = './.tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = theme_config_json
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss_config') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                content_path=['**/*.py'],
                input_css_path='./.tailwind/tailwind_input.css',
                config_js_path='./.tailwind/tailwind.config.js',
                download_node=False,
                node_version='18.17.0',
                tailwind_theme_config=None,
            )


if __name__ == '__main__':
    pytest.main([__file__])
