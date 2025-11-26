import os
import pytest
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch
from dash_tailwindcss_plugin.utils import dict_to_js_object, TailwindCommand


class TestUtils:
    """Test cases for utility functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_dict_to_js_object(self):
        """Test dict_to_js_object with various dictionary structures."""
        # Test with empty dictionary
        result = dict_to_js_object({})
        assert result == '{}'

        # Test with simple dictionary
        test_dict = {'key': 'value'}
        result = dict_to_js_object(test_dict)
        expected = '{\n  key: "value"\n}'
        assert result == expected

        # Test with nested dictionary
        test_dict = {'outer': {'inner': 'value'}}
        result = dict_to_js_object(test_dict)
        expected = '{\n  outer: {\n    inner: "value"\n  }\n}'
        assert result == expected

        # Test with mixed value types
        test_dict = {'string': 'value', 'number': 42, 'float': 3.14, 'boolean': True, 'list': ['item1', 'item2']}
        result = dict_to_js_object(test_dict)
        assert 'string: "value"' in result
        assert 'number: 42' in result
        assert 'float: 3.14' in result
        assert 'boolean: true' in result
        assert 'list: ["item1", "item2"]' in result

        # Test with None values
        test_dict = {'key': None}
        result = dict_to_js_object(test_dict)
        expected = '{\n  key: None\n}'
        assert result == expected

        # Test with empty values
        test_dict = {'empty_string': '', 'none_value': None, 'empty_list': [], 'empty_dict': {}}
        result = dict_to_js_object(test_dict)
        assert 'empty_string: ""' in result
        assert 'none_value: None' in result
        assert 'empty_list: []' in result
        assert 'empty_dict: {}' in result

        # Test with nested arrays containing dictionaries
        test_dict = {'themes': [{'name': 'light', 'primary': '#ffffff'}, {'name': 'dark', 'primary': '#000000'}]}
        result = dict_to_js_object(test_dict)
        assert '"light"' in result
        assert '"dark"' in result
        assert 'primary: "#ffffff"' in result
        assert 'primary: "#000000"' in result

        # Test with complex nested structure
        test_dict = {
            'theme': {
                'colors': {
                    'brand': {
                        '50': '#eff6ff',
                        '500': '#3b82f6',
                    }
                },
                'spacing': {'0': '0px', '1': '0.25rem', '2': '0.5rem', '4': '1rem', '8': '2rem'},
            }
        }
        result = dict_to_js_object(test_dict)
        assert 'brand' in result
        assert '500: "#3b82f6"' in result
        assert 'spacing' in result
        assert '4: "1rem"' in result

        # Test with list items of various types
        test_dict = {'items': ['string_item', True, False, 42, 3.14, None]}
        result = dict_to_js_object(test_dict)
        assert 'string_item' in result
        assert 'true' in result
        assert 'false' in result
        assert '42' in result
        assert '3.14' in result
        assert 'None' in result

    def test_tailwind_command_config_creation(self):
        """Test TailwindCommand configuration file creation methods."""
        # Test create_default_tailwindcss_config with default theme
        config_path = 'test.config.js'
        content_path = ['*.html', '*.js']

        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=content_path,
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        tailwind_command.create_default_tailwindcss_config()
        assert os.path.exists(config_path)

        with open(config_path, 'r') as f:
            content = f.read()
            assert 'content: ["*.html", "*.js"]' in content
            assert 'theme: {' in content
            assert 'plugins: []' in content

        # Test create_default_tailwindcss_config with custom theme
        config_path2 = 'test_theme.config.js'
        theme_config = {'colors': {'primary': '#ff0000'}}

        tailwind_command2 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path2,
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
            theme_config=theme_config,
        )

        tailwind_command2.create_default_tailwindcss_config()
        assert os.path.exists(config_path2)

        with open(config_path2, 'r') as f:
            content = f.read()
            assert 'content: ["*.html"]' in content
            assert 'primary: "#ff0000"' in content

        # Test create_default_tailwindcss_config with complex theme
        config_path3 = 'test_complex.config.js'
        complex_theme_config = {
            'colors': {
                'brand': {
                    '50': '#eff6ff',
                    '500': '#3b82f6',
                }
            },
            'extend': {
                'spacing': {
                    '128': '32rem',
                }
            },
        }

        tailwind_command3 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path3,
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
            theme_config=complex_theme_config,
        )

        tailwind_command3.create_default_tailwindcss_config()
        assert os.path.exists(config_path3)

        with open(config_path3, 'r') as f:
            content = f.read()
            assert 'content: ["*.html"]' in content
            assert 'brand' in content
            assert '50: "#eff6ff"' in content
            assert '500: "#3b82f6"' in content
            assert '128: "32rem"' in content

    def test_tailwind_command_input_css_creation(self):
        """Test TailwindCommand input CSS file creation methods."""
        # Test create_default_input_tailwindcss for v3
        input_css_path = 'test_input.css'

        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path=input_css_path,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        tailwind_command.create_default_input_tailwindcss()
        assert os.path.exists(input_css_path)

        with open(input_css_path, 'r') as f:
            content = f.read()
            assert '@tailwind base;' in content
            assert '@tailwind components;' in content
            assert '@tailwind utilities;' in content

        # Test create_default_input_tailwindcss for v4
        input_css_path_v4 = 'test_input_v4.css'

        tailwind_command_v4 = TailwindCommand(
            tailwind_version='4',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path=input_css_path_v4,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        tailwind_command_v4.create_default_input_tailwindcss()
        assert os.path.exists(input_css_path_v4)

        with open(input_css_path_v4, 'r') as f:
            content = f.read()
            assert '@import "tailwindcss";' in content
            assert '@tailwind base;' not in content  # Should not be present in v4

    def test_tailwind_command_directory_creation(self):
        """Test that TailwindCommand creates directories when needed."""
        # Test create_default_tailwindcss_config creates directory
        config_dir = 'config'
        config_path = os.path.join(config_dir, 'test.config.js')
        content_path = ['*.html']

        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=content_path,
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        tailwind_command.create_default_tailwindcss_config()
        assert os.path.exists(config_dir)
        assert os.path.exists(config_path)

        # Test create_default_input_tailwindcss creates directory
        css_dir = 'assets'
        input_css_path = os.path.join(css_dir, 'test_input.css')

        tailwind_command2 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path=input_css_path,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        tailwind_command2.create_default_input_tailwindcss()
        assert os.path.exists(css_dir)
        assert os.path.exists(input_css_path)

    def test_tailwind_command_version_specific_behavior(self):
        """Test TailwindCommand behavior specific to different versions."""
        # Test TailwindCommand with Tailwind CSS v4
        tailwind_command = TailwindCommand(
            tailwind_version='4',
            content_path=['**/*.py'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        # Check that the correct CLI command and package are used for v4
        assert tailwind_command._tailwind_cli == '@tailwindcss/cli'
        assert tailwind_command._tailwind_package == ['tailwindcss', '@tailwindcss/cli']

    def test_tailwind_command_init_and_install(self):
        """Test TailwindCommand init and install methods."""
        # Test _check_npm_init method
        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        result = tailwind_command._check_npm_init()
        assert result is False  # By default, package.json does not exist

        # Test _check_tailwindcss method
        result = tailwind_command._check_tailwindcss()
        assert result is False  # By default, Tailwind CSS is not installed

        # Test init method with CLI messages
        tailwind_command_cli = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        with patch.object(tailwind_command_cli, '_check_npm_init', return_value=False):
            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = tailwind_command_cli.init()
                assert result == tailwind_command_cli

        # Test init method with existing files
        test_dir = tempfile.mkdtemp()
        input_css_path = os.path.join(test_dir, 'input.css')
        config_js_path = os.path.join(test_dir, 'config.js')

        with open(input_css_path, 'w') as f:
            f.write('/* existing input css */')
        with open(config_js_path, 'w') as f:
            f.write('/* existing config */')

        tailwind_command2 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir=test_dir,
            input_css_path=input_css_path,
            output_css_path=os.path.join(test_dir, 'output.css'),
            config_js_path=config_js_path,
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        with patch.object(tailwind_command2, '_check_npm_init', return_value=True):
            result = tailwind_command2.init()
            assert result == tailwind_command2

        shutil.rmtree(test_dir, ignore_errors=True)

        # Test install method when Tailwind CSS is not installed
        with patch.object(tailwind_command, '_check_tailwindcss', return_value=False):
            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = tailwind_command.install()
                assert result == tailwind_command

        # Test init method with npm init failure
        with patch.object(tailwind_command, '_check_npm_init', return_value=False):
            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_result.stderr = 'npm init error'
                mock_run.return_value = mock_result

                with pytest.raises(RuntimeError, match='npm init error'):
                    tailwind_command.init()

        # Test install method with npm install failure
        with patch.object(tailwind_command, '_check_tailwindcss', return_value=False):
            with patch('subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_result.stderr = 'npm install error'
                mock_run.return_value = mock_result

                with pytest.raises(RuntimeError, match='npm install error'):
                    tailwind_command.install()

    def test_tailwind_command_build_and_watch(self):
        """Test TailwindCommand build and watch methods."""
        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        # Test build method with error
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = 'Build error'
            mock_run.return_value = mock_result

            with pytest.raises(RuntimeError, match='Build error'):
                tailwind_command.build()

        # Test watch method with keyboard interrupt
        with patch('subprocess.run', side_effect=KeyboardInterrupt):
            result = tailwind_command.watch()
            assert result == tailwind_command

        # Test watch method with exception
        with patch('subprocess.run', side_effect=Exception('Watch error')):
            with pytest.raises(Exception, match='Watch error'):
                tailwind_command.watch()

    def test_tailwind_command_clean(self):
        """Test TailwindCommand clean method with various scenarios."""
        # Test clean method with nonexistent files
        tailwind_command = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='nonexistent_input.css',
            output_css_path='nonexistent_output.css',
            config_js_path='nonexistent_config.js',
            is_cli=False,
            download_node=False,
            node_version='18.17.0',
        )

        result = tailwind_command.clean()
        assert result == tailwind_command

        # Test clean method with CLI messages
        tailwind_command_cli = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        with open('input.css', 'w') as f:
            f.write('/* test */')

        result = tailwind_command_cli.clean()
        assert result == tailwind_command_cli

        # Test clean method with file removal exception
        config_path = 'test.config.js'
        tailwind_command3 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='.',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        with open(config_path, 'w') as f:
            f.write('test content')

        with patch('os.remove', side_effect=Exception('Permission denied')):
            with patch('dash_tailwindcss_plugin.utils.logger') as mock_logger:
                tailwind_command3.clean()
                mock_logger.warning.assert_called()

        # Test clean method with directory removal
        tailwind_command4 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='test_dir',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        os.makedirs('test_dir/node_modules/subdir', exist_ok=True)
        with open('test_dir/node_modules/test_file.txt', 'w') as f:
            f.write('test content')

        with patch('dash_tailwindcss_plugin.utils.logger') as mock_logger:
            tailwind_command4.clean()
            mock_logger.info.assert_called()

        # Test clean method with directory removal exception
        tailwind_command5 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='test_dir2',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        os.makedirs('test_dir2/node_modules', exist_ok=True)

        with patch('shutil.rmtree', side_effect=Exception('Permission denied')):
            with patch('dash_tailwindcss_plugin.utils.logger') as mock_logger:
                tailwind_command5.clean()
                mock_logger.warning.assert_called()

        # Test clean method with general exception
        tailwind_command6 = TailwindCommand(
            tailwind_version='3',
            content_path=['*.html'],
            plugin_tmp_dir='test_dir3',
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=True,  # Enable CLI mode
            download_node=False,
            node_version='18.17.0',
        )

        with patch('os.path.exists', side_effect=Exception('General error')):
            with patch('dash_tailwindcss_plugin.utils.logger') as mock_logger:
                with pytest.raises(Exception, match='General error'):
                    tailwind_command6.clean()
                mock_logger.error.assert_called()

    def test_file_time_functions(self):
        """Test file time related functions."""
        # Create a temporary file
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, 'test.txt')

        with open(test_file, 'w') as f:
            f.write('test content')

        mod_time = os.path.getmtime(test_file)
        current_time = time.time()

        # Verify the file was created recently
        assert current_time - mod_time < 5  # Should be created within 5 seconds

        shutil.rmtree(test_dir)


if __name__ == '__main__':
    pytest.main([__file__])
