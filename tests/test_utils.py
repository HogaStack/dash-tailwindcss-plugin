import pytest
import os
import tempfile
import shutil
from dash_tailwindcss_plugin.utils import (
    _dict_to_js_object,
    create_default_tailwindcss_config,
    create_default_input_tailwindcss,
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
        """Test _dict_to_js_object with empty dictionary."""
        result = _dict_to_js_object({})
        assert result == '{}'

    def test_dict_to_js_object_simple_dict(self):
        """Test _dict_to_js_object with simple dictionary."""
        test_dict = {'key': 'value'}
        result = _dict_to_js_object(test_dict)
        expected = '{\n  key: "value"\n}'
        assert result == expected

    def test_dict_to_js_object_nested_dict(self):
        """Test _dict_to_js_object with nested dictionary."""
        test_dict = {'outer': {'inner': 'value'}}
        result = _dict_to_js_object(test_dict)
        expected = '{\n  outer: {\n    inner: "value"\n  }\n}'
        assert result == expected

    def test_dict_to_js_object_mixed_types(self):
        """Test _dict_to_js_object with mixed value types."""
        test_dict = {'string': 'value', 'number': 42, 'float': 3.14, 'boolean': True, 'list': ['item1', 'item2']}
        result = _dict_to_js_object(test_dict)
        expected = (
            '{\n  string: "value",\n  number: 42,\n  float: 3.14,\n  boolean: true,\n  list: ["item1", "item2"]\n}'
        )
        assert result == expected

    def test_create_default_tailwindcss_config(self):
        """Test create_default_tailwindcss_config function."""
        config_path = 'test.config.js'
        content_path = ['*.html', '*.js']

        create_default_tailwindcss_config(content_path, config_path)

        # Check that file was created
        assert os.path.exists(config_path)

        # Check file content
        with open(config_path, 'r') as f:
            content = f.read()
            assert 'content: ["*.html", "*.js"]' in content
            assert 'theme: {' in content
            assert 'plugins: []' in content

    def test_create_default_tailwindcss_config_with_theme(self):
        """Test create_default_tailwindcss_config function with theme configuration."""
        config_path = 'test.config.js'
        content_path = ['*.html']
        theme_config = {'colors': {'primary': '#ff0000'}}

        create_default_tailwindcss_config(content_path, config_path, theme_config)

        # Check that file was created
        assert os.path.exists(config_path)

        # Check file content
        with open(config_path, 'r') as f:
            content = f.read()
            assert 'content: ["*.html"]' in content
            assert 'primary: "#ff0000"' in content

    def test_create_default_input_tailwindcss(self):
        """Test create_default_input_tailwindcss function."""
        input_css_path = 'test_input.css'

        create_default_input_tailwindcss(input_css_path)

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

        create_default_tailwindcss_config(content_path, config_path)

        # Check that directory was created
        assert os.path.exists(config_dir)
        assert os.path.exists(config_path)

    def test_create_default_input_tailwindcss_creates_directory(self):
        """Test that create_default_input_tailwindcss creates directory if it doesn't exist."""
        css_dir = 'assets'
        input_css_path = os.path.join(css_dir, 'test_input.css')

        create_default_input_tailwindcss(input_css_path)

        # Check that directory was created
        assert os.path.exists(css_dir)
        assert os.path.exists(input_css_path)


if __name__ == '__main__':
    pytest.main([__file__])
