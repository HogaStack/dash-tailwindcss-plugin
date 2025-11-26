import os
import pytest
import shutil
import tempfile
from unittest.mock import MagicMock, patch
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
    def test_run_with_different_commands(self, mock_parse_args):
        """Test run method with different commands."""
        # Test with init command
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

        # Test with build command
        mock_args.command = 'build'
        mock_args.clean_after = False
        mock_parse_args.return_value = mock_args

        with patch.object(cli, 'build_tailwindcss') as mock_build:
            cli.run()
            mock_build.assert_called_once_with(clean_after=False)

        # Test with watch command
        mock_args.command = 'watch'
        mock_parse_args.return_value = mock_args

        with patch.object(cli, 'watch_tailwindcss') as mock_watch:
            cli.run()
            mock_watch.assert_called_once()

        # Test with clean command
        mock_args.command = 'clean'
        mock_parse_args.return_value = mock_args

        with patch.object(cli, 'clean_tailwindcss') as mock_clean:
            cli.run()
            mock_clean.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    def test_run_with_theme_config(self, mock_parse_args):
        """Test run method with theme configuration."""
        # Test with valid theme config
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

        # Test with invalid theme config
        theme_config_json = '{"colors": {"primary": "#ff0000"'  # Invalid JSON
        mock_args.tailwind_theme_config = theme_config_json
        mock_parse_args.return_value = mock_args

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
    def test_run_with_custom_parameters(self, mock_parse_args):
        """Test run method with custom parameters."""
        # Test with multiple content paths
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
            with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
                mock_tailwind_instance = MagicMock()
                mock_tailwind_command.return_value = mock_tailwind_instance
                cli.run()
                mock_tailwind_command.assert_called()
                call_args = mock_tailwind_command.call_args[1]
                assert call_args['content_path'] == ['*.html', '*.js']

        # Test with custom plugin temporary directory
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

        with patch.object(cli, 'build_tailwindcss'):
            with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
                mock_tailwind_instance = MagicMock()
                mock_tailwind_command.return_value = mock_tailwind_instance
                cli.run()
                mock_tailwind_command.assert_called()
                call_args = mock_tailwind_command.call_args[1]
                assert call_args['plugin_tmp_dir'] == './custom'

    @patch('argparse.ArgumentParser.parse_args')
    def test_tailwindcss_commands(self, mock_parse_args):
        """Test various TailwindCSS commands."""
        # Test init_tailwindcss method
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
        mock_args.clean_after = False
        mock_parse_args.return_value = mock_args

        cli = _TailwindCLI()

        # Test init_tailwindcss with logging
        with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
            mock_tailwind_instance = MagicMock()
            mock_init_instance = MagicMock()
            mock_install_instance = MagicMock()

            mock_tailwind_command.return_value = mock_tailwind_instance
            mock_tailwind_instance.init.return_value = mock_init_instance
            mock_init_instance.install.return_value = mock_install_instance

            cli.run()

            mock_tailwind_instance.init.assert_called_once()
            mock_init_instance.install.assert_called_once()

        # Test build_tailwindcss with different cleanup settings
        mock_args.command = 'build'
        mock_args.clean_after = True
        mock_parse_args.return_value = mock_args

        with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
            mock_tailwind_instance = MagicMock()
            mock_init_instance = MagicMock()
            mock_install_instance = MagicMock()
            mock_build_instance = MagicMock()
            mock_clean_instance = MagicMock()

            mock_tailwind_command.return_value = mock_tailwind_instance
            mock_tailwind_instance.init.return_value = mock_init_instance
            mock_init_instance.install.return_value = mock_install_instance
            mock_install_instance.build.return_value = mock_build_instance
            mock_build_instance.clean.return_value = mock_clean_instance

            cli.run()

            mock_tailwind_instance.init.assert_called_once()
            mock_init_instance.install.assert_called_once()
            mock_install_instance.build.assert_called_once()
            mock_build_instance.clean.assert_called_once()

        # Test build_tailwindcss without cleanup
        mock_args.clean_after = False
        mock_parse_args.return_value = mock_args

        with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
            mock_tailwind_instance = MagicMock()
            mock_init_instance = MagicMock()
            mock_install_instance = MagicMock()
            mock_build_instance = MagicMock()

            mock_tailwind_command.return_value = mock_tailwind_instance
            mock_tailwind_instance.init.return_value = mock_init_instance
            mock_init_instance.install.return_value = mock_install_instance
            mock_install_instance.build.return_value = mock_build_instance

            cli.run()

            mock_tailwind_instance.init.assert_called_once()
            mock_init_instance.install.assert_called_once()
            mock_install_instance.build.assert_called_once()

        # Test watch_tailwindcss
        mock_args.command = 'watch'
        mock_parse_args.return_value = mock_args

        with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
            mock_tailwind_instance = MagicMock()
            mock_init_instance = MagicMock()
            mock_install_instance = MagicMock()
            mock_watch_instance = MagicMock()

            mock_tailwind_command.return_value = mock_tailwind_instance
            mock_tailwind_instance.init.return_value = mock_init_instance
            mock_init_instance.install.return_value = mock_install_instance
            mock_install_instance.watch.return_value = mock_watch_instance

            cli.run()

            mock_tailwind_instance.init.assert_called_once()
            mock_init_instance.install.assert_called_once()
            mock_install_instance.watch.assert_called_once()

        # Test clean_tailwindcss
        mock_args.command = 'clean'
        mock_parse_args.return_value = mock_args

        with patch('dash_tailwindcss_plugin.cli.TailwindCommand') as mock_tailwind_command:
            mock_tailwind_instance = MagicMock()
            mock_clean_instance = MagicMock()

            mock_tailwind_command.return_value = mock_tailwind_instance
            mock_tailwind_instance.clean.return_value = mock_clean_instance

            cli.run()

            mock_tailwind_instance.clean.assert_called_once()

    def test_main_and_module_execution(self):
        """Test the main function and module execution."""
        # Test the main function
        with patch('dash_tailwindcss_plugin.cli._TailwindCLI') as mock_cli:
            mock_cli_instance = MagicMock()
            mock_cli.return_value = mock_cli_instance

            from dash_tailwindcss_plugin.cli import main

            main()

            mock_cli.assert_called_once()
            mock_cli_instance.run.assert_called_once()

        # Test the __main__ execution of the CLI module
        with patch('dash_tailwindcss_plugin.cli._TailwindCLI') as mock_cli:
            mock_cli_instance = MagicMock()
            mock_cli.return_value = mock_cli_instance

            # Import module and execute
            import dash_tailwindcss_plugin.cli as cli_module

            # Simulate the case where __name__ == '__main__'
            with patch.object(cli_module, '__name__', '__main__'):
                pass  # Call main() when actually running


if __name__ == '__main__':
    pytest.main([__file__])
