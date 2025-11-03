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
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                input_css_path='./_tailwind/tailwind_input.css', config_js_path='./_tailwind/tailwind.config.js'
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_build_command(self, mock_parse_args):
        """Test run method with build command."""
        mock_args = MagicMock()
        mock_args.command = 'build'
        mock_args.content_path = None
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.clean_after = False
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'build_tailwindcss') as mock_build:
            cli.run()
            mock_build.assert_called_once_with(clean_after=False)

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_watch_command(self, mock_parse_args):
        """Test run method with watch command."""
        mock_args = MagicMock()
        mock_args.command = 'watch'
        mock_args.content_path = None
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'watch_tailwindcss') as mock_watch:
            cli.run()
            mock_watch.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_clean_command(self, mock_parse_args):
        """Test run method with clean command."""
        mock_args = MagicMock()
        mock_args.command = 'clean'
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'clean_tailwindcss') as mock_clean:
            cli.run()
            mock_clean.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_theme_config(self, mock_parse_args):
        """Test run method with theme configuration."""
        theme_config_json = '{"colors": {"primary": "#ff0000"}}'
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = theme_config_json
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                input_css_path='./_tailwind/tailwind_input.css', config_js_path='./_tailwind/tailwind.config.js'
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_invalid_theme_config(self, mock_parse_args):
        """Test run method with invalid theme configuration."""
        theme_config_json = '{"colors": {"primary": "#ff0000"'  # Invalid JSON
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = theme_config_json
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                input_css_path='./_tailwind/tailwind_input.css', config_js_path='./_tailwind/tailwind.config.js'
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_tailwind_v4(self, mock_parse_args):
        """Test run method with Tailwind CSS v4."""
        mock_args = MagicMock()
        mock_args.command = 'init'
        mock_args.content_path = None
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '4'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'init_tailwindcss') as mock_init:
            cli.run()
            mock_init.assert_called_once_with(
                input_css_path='./_tailwind/tailwind_input.css', config_js_path='./_tailwind/tailwind.config.js'
            )

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_multiple_content_paths(self, mock_parse_args):
        """Test run method with multiple content paths."""
        mock_args = MagicMock()
        mock_args.command = 'build'
        mock_args.content_path = ['*.html', '*.js']
        mock_args.input_css_path = './_tailwind/tailwind_input.css'
        mock_args.output_css_path = './_tailwind/tailwind.css'
        mock_args.config_js_path = './_tailwind/tailwind.config.js'
        mock_args.clean_after = False
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './_tailwind'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'build_tailwindcss'):
            with patch('dash_tailwindcss_plugin.cli.NodeManager'), patch(
                'dash_tailwindcss_plugin.cli.TailwindCommand'
            ) as mock_tailwind_command:
                mock_tailwind_instance = MagicMock()
                mock_tailwind_command.return_value = mock_tailwind_instance
                cli.run()
                # Verify that the multiple content paths are passed correctly
                mock_tailwind_command.assert_called()
                call_args = mock_tailwind_command.call_args[1]  # Get keyword arguments
                assert call_args['content_path'] == ['*.html', '*.js']

    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_with_multiple_content_paths(self, mock_parse_args):
        """Test CLI with multiple content paths."""
        with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
            mock_args = MagicMock()
            mock_args.command = 'build'
            mock_args.content_path = ['*.html', '*.js', '*.py']
            mock_args.input_css_path = './_tailwind/tailwind_input.css'
            mock_args.output_css_path = './_tailwind/tailwind.css'
            mock_args.config_js_path = './_tailwind/tailwind.config.js'
            mock_args.clean_after = False
            mock_args.download_node = False
            mock_args.node_version = '18.17.0'
            mock_args.tailwind_theme_config = None
            mock_args.tailwind_version = '3'
            mock_args.plugin_tmp_dir = './_tailwind'
            mock_parse_args.return_value = mock_args

            cli = _TailwindCLI()
            with patch.object(cli, 'build_tailwindcss'):
                with patch('dash_tailwindcss_plugin.cli.NodeManager'), patch(
                    'dash_tailwindcss_plugin.cli.TailwindCommand'
                ) as mock_tailwind_command:
                    mock_tailwind_instance = MagicMock()
                    mock_tailwind_command.return_value = mock_tailwind_instance
                    cli.run()
                    # Verify that the multiple content paths are passed correctly
                    mock_tailwind_command.assert_called()
                    call_args = mock_tailwind_command.call_args[1]  # Get keyword arguments
                    assert call_args['content_path'] == ['*.html', '*.js', '*.py']

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_custom_plugin_tmp_dir(self, mock_parse_args):
        """Test run method with custom plugin temporary directory."""
        mock_args = MagicMock()
        mock_args.command = 'build'
        mock_args.content_path = None
        mock_args.input_css_path = './custom/tailwind_input.css'
        mock_args.output_css_path = './custom/tailwind.css'
        mock_args.config_js_path = './custom/tailwind.config.js'
        mock_args.clean_after = False
        mock_args.download_node = False
        mock_args.node_version = '18.17.0'
        mock_args.tailwind_theme_config = None
        mock_args.tailwind_version = '3'
        mock_args.plugin_tmp_dir = './custom'
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()
        with patch.object(cli, 'build_tailwindcss'):
            with patch('dash_tailwindcss_plugin.cli.NodeManager'), patch(
                'dash_tailwindcss_plugin.cli.TailwindCommand'
            ) as mock_tailwind_command:
                mock_tailwind_instance = MagicMock()
                mock_tailwind_command.return_value = mock_tailwind_instance
                cli.run()
                # Verify that the custom plugin temporary directory is passed correctly
                mock_tailwind_command.assert_called()
                call_args = mock_tailwind_command.call_args[1]  # Get keyword arguments
                assert call_args['plugin_tmp_dir'] == './custom'


if __name__ == '__main__':
    pytest.main([__file__])
