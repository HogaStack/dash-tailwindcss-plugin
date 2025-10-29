import pytest
import os
import tempfile
import shutil
import time
from unittest.mock import patch, Mock
from dash_tailwindcss_plugin.utils import (
    dict_to_js_object,
    NodeManager,
    TailwindCommand,
)


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

    def test_dict_to_js_object_empty_dict(self):
        """Test dict_to_js_object with empty dictionary."""
        result = dict_to_js_object({})
        assert result == '{}'

    def test_dict_to_js_object_simple_dict(self):
        """Test dict_to_js_object with simple dictionary."""
        test_dict = {'key': 'value'}
        result = dict_to_js_object(test_dict)
        expected = '{\n  key: "value"\n}'
        assert result == expected

    def test_dict_to_js_object_nested_dict(self):
        """Test dict_to_js_object with nested dictionary."""
        test_dict = {'outer': {'inner': 'value'}}
        result = dict_to_js_object(test_dict)
        expected = '{\n  outer: {\n    inner: "value"\n  }\n}'
        assert result == expected

    def test_dict_to_js_object_mixed_types(self):
        """Test dict_to_js_object with mixed value types."""
        test_dict = {'string': 'value', 'number': 42, 'float': 3.14, 'boolean': True, 'list': ['item1', 'item2']}
        result = dict_to_js_object(test_dict)
        expected = (
            '{\n  string: "value",\n  number: 42,\n  float: 3.14,\n  boolean: true,\n  list: ["item1", "item2"]\n}'
        )
        assert result == expected

    def test_dict_to_js_object_with_none_values(self):
        """Test dict_to_js_object with None values."""
        test_dict = {'key': None}
        result = dict_to_js_object(test_dict)
        expected = '{\n  key: None\n}'
        assert result == expected

    def test_dict_to_js_object_with_empty_values(self):
        """Test dict_to_js_object with empty values."""
        test_dict = {'empty_string': '', 'none_value': None, 'empty_list': [], 'empty_dict': {}}
        result = dict_to_js_object(test_dict)
        assert 'empty_string: ""' in result
        assert 'none_value: None' in result
        assert 'empty_list: []' in result
        assert 'empty_dict: {}' in result

    def test_dict_to_js_object_with_nested_arrays(self):
        """Test dict_to_js_object with nested arrays containing dictionaries."""
        test_dict = {'themes': [{'name': 'light', 'primary': '#ffffff'}, {'name': 'dark', 'primary': '#000000'}]}
        result = dict_to_js_object(test_dict)
        assert '"light"' in result
        assert '"dark"' in result
        assert 'primary: "#ffffff"' in result
        assert 'primary: "#000000"' in result

    def test_dict_to_js_object_with_complex_nested_structure(self):
        """Test dict_to_js_object with complex nested structure."""
        test_dict = {
            'theme': {
                'colors': {
                    'brand': {
                        '50': '#eff6ff',
                        '100': '#dbeafe',
                        '200': '#bfdbfe',
                        '300': '#93c5fd',
                        '400': '#60a5fa',
                        '500': '#3b82f6',
                        '600': '#2563eb',
                        '700': '#1d4ed8',
                        '800': '#1e40af',
                        '900': '#1e3a8a',
                    }
                },
                'spacing': {'0': '0px', '1': '0.25rem', '2': '0.5rem', '4': '1rem', '8': '2rem'},
            }
        }
        result = dict_to_js_object(test_dict)
        # Check that all nested keys are present
        assert 'brand' in result
        assert '500: "#3b82f6"' in result
        assert 'spacing' in result
        assert '4: "1rem"' in result

    def test_create_default_tailwindcss_config(self):
        """Test create_default_tailwindcss_config method."""
        config_path = 'test.config.js'
        content_path = ['*.html', '*.js']

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='3',
            content_path=content_path,
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=False,
        )

        tailwind_command.create_default_tailwindcss_config()

        # Check that file was created
        assert os.path.exists(config_path)

        # Check file content
        with open(config_path, 'r') as f:
            content = f.read()
            assert 'content: ["*.html", "*.js"]' in content
            assert 'theme: {' in content
            assert 'plugins: []' in content

    def test_create_default_tailwindcss_config_with_theme(self):
        """Test create_default_tailwindcss_config method with theme configuration."""
        config_path = 'test.config.js'
        content_path = ['*.html']
        theme_config = {'colors': {'primary': '#ff0000'}}

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='3',
            content_path=content_path,
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=False,
            theme_config=theme_config,
        )

        tailwind_command.create_default_tailwindcss_config()

        # Check that file was created
        assert os.path.exists(config_path)

        # Check file content
        with open(config_path, 'r') as f:
            content = f.read()
            assert 'content: ["*.html"]' in content
            assert 'primary: "#ff0000"' in content

    def test_create_default_input_tailwindcss(self):
        """Test create_default_input_tailwindcss method."""
        input_css_path = 'test_input.css'

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='3',
            content_path=['*.html'],
            input_css_path=input_css_path,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
        )

        tailwind_command.create_default_input_tailwindcss()

        # Check that file was created
        assert os.path.exists(input_css_path)

        # Check file content
        with open(input_css_path, 'r') as f:
            content = f.read()
            assert '@tailwind base;' in content
            assert '@tailwind components;' in content
            assert '@tailwind utilities;' in content

    def test_create_default_tailwindcss_config_creates_directory(self):
        """Test that create_default_tailwindcss_config creates directory if it doesn't exist."""
        config_dir = 'config'
        config_path = os.path.join(config_dir, 'test.config.js')
        content_path = ['*.html']

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='3',
            content_path=content_path,
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path=config_path,
            is_cli=False,
        )

        tailwind_command.create_default_tailwindcss_config()

        # Check that directory was created
        assert os.path.exists(config_dir)
        assert os.path.exists(config_path)

    def test_create_default_input_tailwindcss_creates_directory(self):
        """Test that create_default_input_tailwindcss creates directory if it doesn't exist."""
        css_dir = 'assets'
        input_css_path = os.path.join(css_dir, 'test_input.css')

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='3',
            content_path=['*.html'],
            input_css_path=input_css_path,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
        )

        tailwind_command.create_default_input_tailwindcss()

        # Check that directory was created
        assert os.path.exists(css_dir)
        assert os.path.exists(input_css_path)

    def test_tailwind_command_with_v4_version(self):
        """Test TailwindCommand with Tailwind CSS v4."""
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='4',
            content_path=['**/*.py'],
            input_css_path='input.css',
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
        )

        # Check that the correct CLI command and package are used for v4
        assert tailwind_command._tailwind_cli == '@tailwindcss/cli'
        assert tailwind_command._tailwind_package == ['tailwindcss', '@tailwindcss/cli']

    def test_tailwind_command_create_default_input_v4(self):
        """Test create_default_input_tailwindcss method with v4."""
        input_css_path = 'test_input_v4.css'

        # Create a TailwindCommand instance to access the method
        tailwind_command = TailwindCommand(
            node_path=None,
            npm_path='npm',
            npx_path='npx',
            tailwind_version='4',
            content_path=['*.html'],
            input_css_path=input_css_path,
            output_css_path='output.css',
            config_js_path='config.js',
            is_cli=False,
        )

        tailwind_command.create_default_input_tailwindcss()

        # Check that file was created
        assert os.path.exists(input_css_path)

        # Check file content for v4
        with open(input_css_path, 'r') as f:
            content = f.read()
            assert '@import "tailwindcss";' in content
            assert '@tailwind base;' not in content  # Should not be present in v4

    def test_get_command_alias_by_platform(self):
        """Test get_command_alias_by_platform method."""
        node_manager = NodeManager(download_node=False, node_version='18.17.0')

        # Test with Windows
        with patch('platform.system', return_value='Windows'):
            result = node_manager.get_command_alias_by_platform('npx')
            assert result == 'npx.cmd'

        # Test with other systems
        with patch('platform.system', return_value='Linux'):
            result = node_manager.get_command_alias_by_platform('npx')
            assert result == 'npx'

    def test_check_nodejs_available(self):
        """Test check_nodejs_available method."""
        node_manager = NodeManager(download_node=False, node_version='18.17.0')

        # Mock subprocess.run to return a successful result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'v14.17.0\n'  # Note: stdout should be a string, not bytes
        with patch('subprocess.run', return_value=mock_result):
            is_available, version = node_manager.check_nodejs_available()
            assert is_available is True
            assert version == 'v14.17.0'

    def test_check_nodejs_available_not_found(self):
        """Test check_nodejs_available when Node.js is not found."""
        node_manager = NodeManager(download_node=False, node_version='18.17.0')

        with patch('subprocess.run', side_effect=FileNotFoundError()):
            is_available, version = node_manager.check_nodejs_available()
            assert is_available is False
            assert version == ''

    def test_node_manager_with_different_versions(self):
        """Test NodeManager with different Node.js versions."""
        node_manager = NodeManager(download_node=True, node_version='16.0.0')
        assert node_manager.node_version == '16.0.0'

        node_manager = NodeManager(download_node=True, node_version='20.0.0')
        assert node_manager.node_version == '20.0.0'

    def test_node_manager_with_v4_node_version(self):
        """Test NodeManager with different Node.js versions including v4."""
        node_manager = NodeManager(download_node=True, node_version='20.0.0')
        assert node_manager.node_version == '20.0.0'

    def test_file_time_functions(self):
        """Test file time related functions."""
        # Create a temporary file
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, 'test.txt')

        # Create file and check its modification time
        with open(test_file, 'w') as f:
            f.write('test content')

        # Get modification time
        mod_time = os.path.getmtime(test_file)
        current_time = time.time()

        # Verify the file was created recently
        assert current_time - mod_time < 5  # Should be created within 5 seconds

        # Clean up
        os.remove(test_file)
        os.rmdir(test_dir)


if __name__ == '__main__':
    pytest.main([__file__])
