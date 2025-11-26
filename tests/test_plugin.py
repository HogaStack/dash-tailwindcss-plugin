import os
import pytest
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch
from dash_tailwindcss_plugin.plugin import _TailwindCSSPlugin


class TestTailwindCSSPlugin:
    """Test cases for the _TailwindCSSPlugin class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plugin_initialization(self):
        """Test plugin initialization with default and custom parameters."""
        # Test with default parameters
        plugin = _TailwindCSSPlugin()
        assert plugin.mode == 'offline'
        assert plugin.content_path == ['**/*.py']
        assert plugin.plugin_tmp_dir == '_tailwind'
        assert plugin.input_css_path == '_tailwind/tailwind_input.css'
        assert plugin.output_css_path == '_tailwind/tailwind.css'
        assert plugin.config_js_path == '_tailwind/tailwind.config.js'
        assert plugin.cdn_url == 'https://cdn.tailwindcss.com'
        assert plugin.download_node is False
        assert plugin.node_version == '18.17.0'
        assert plugin.tailwind_theme_config == {}
        assert plugin.clean_after is True
        assert plugin.skip_build_if_recent is True
        assert plugin.skip_build_time_threshold == 5

        # Test with custom parameters
        custom_content_path = ['*.html', '*.js']
        plugin = _TailwindCSSPlugin(
            mode='online',
            content_path=custom_content_path,
            plugin_tmp_dir='_custom_tailwind',
            input_css_path='custom_input.css',
            output_css_path='custom_output.css',
            config_js_path='custom_config.js',
            cdn_url='https://custom.cdn.com',
            download_node=True,
            node_version='16.0.0',
            tailwind_theme_config={'colors': {'primary': '#ff0000'}},
            clean_after=False,
            skip_build_if_recent=False,
            skip_build_time_threshold=10,
        )
        assert plugin.mode == 'online'
        assert plugin.content_path == custom_content_path
        assert plugin.plugin_tmp_dir == '_custom_tailwind'
        assert plugin.input_css_path == 'custom_input.css'
        assert plugin.output_css_path == 'custom_output.css'
        assert plugin.config_js_path == 'custom_config.js'
        assert plugin.cdn_url == 'https://custom.cdn.com'
        assert plugin.download_node is True
        assert plugin.node_version == '16.0.0'
        assert plugin.tailwind_theme_config == {'colors': {'primary': '#ff0000'}}
        assert plugin.clean_after is False
        assert plugin.skip_build_if_recent is False
        assert plugin.skip_build_time_threshold == 10

    def test_setup_methods(self):
        """Test setup methods for online and offline modes."""
        # Test online mode setup
        with patch('dash_tailwindcss_plugin.plugin.hooks') as mock_hooks:
            plugin = _TailwindCSSPlugin(mode='online')
            plugin.setup_online_mode()
            mock_hooks.index.assert_called_once()

        # Test offline mode setup
        with patch('dash_tailwindcss_plugin.plugin.hooks') as mock_hooks:
            plugin = _TailwindCSSPlugin(mode='offline')
            plugin.setup_offline_mode()
            mock_hooks.setup.assert_called_once()
            mock_hooks.index.assert_called_once()
            mock_hooks.route.assert_called_once()

    def test_should_skip_build(self):
        """Test _should_skip_build method with different scenarios."""
        # Create temporary file
        css_file = os.path.join(self.test_dir, 'test.css')
        with open(css_file, 'w') as f:
            f.write('/* test css */')

        plugin = _TailwindCSSPlugin(mode='offline', skip_build_if_recent=True, skip_build_time_threshold=5)
        plugin.output_css_path = css_file

        # Test case where build should be skipped (recent file)
        result = plugin._should_skip_build()
        assert result is True

        # Test case where build should not be skipped (old file)
        old_time = time.time() - 10
        os.utime(css_file, (old_time, old_time))
        result = plugin._should_skip_build()
        assert result is False

        # Test case where build should not be skipped (skip_build_if_recent=False)
        plugin.skip_build_if_recent = False
        result = plugin._should_skip_build()
        assert result is False

        # Test case where build should not be skipped (file doesn't exist)
        plugin.output_css_path = 'nonexistent.css'
        result = plugin._should_skip_build()
        assert result is False

    def test_process_html(self):
        """Test HTML processing for both online and offline modes."""
        # Test online mode HTML processing
        plugin = _TailwindCSSPlugin(mode='online')

        # Test with head tag
        html_with_head = '<html><head></head><body><h1>Test</h1></body></html>'
        result = plugin._process_online_html(html_with_head)
        assert '<script src="' in result
        assert '</head>' in result

        # Test with body only
        html_with_body_only = '<html><body><h1>Test</h1></body></html>'
        result = plugin._process_online_html(html_with_body_only)
        assert '<script src="' in result
        assert '<head>' in result
        assert '</head>' in result

        # Test without tags
        html_without_tags = '<h1>Test</h1>'
        result = plugin._process_online_html(html_without_tags)
        assert '<script src="' in result
        assert '<head>' in result
        assert '</head>' in result

        # Test with theme config
        theme_config = {'colors': {'primary': '#ff0000'}}
        plugin = _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)
        result = plugin._process_online_html(html_with_head)
        assert '<script src="' in result
        assert 'tailwind.config' in result
        assert '"#ff0000"' in result

        # Test offline mode HTML processing
        plugin = _TailwindCSSPlugin(mode='offline')

        # Create a test built_tailwindcss_link
        test_link = '/_tailwind/test_tailwind.css'

        # Test with head tag
        result = plugin._process_offline_html(test_link, html_with_head)
        assert '<link rel="stylesheet"' in result
        assert '</head>' in result

        # Test with body only
        result = plugin._process_offline_html(test_link, html_with_body_only)
        assert '<link rel="stylesheet"' in result
        assert '<head>' in result
        assert '</head>' in result

        # Test without tags
        result = plugin._process_offline_html(test_link, html_without_tags)
        assert '<link rel="stylesheet"' in result
        assert '<head>' in result
        assert '</head>' in result

    def test_serve_tailwindcss(self):
        """Test _serve_tailwindcss method with different scenarios."""
        # Test when CSS file exists
        css_content = 'body { color: red; }'
        css_file = os.path.join(self.test_dir, 'test.css')
        with open(css_file, 'w') as f:
            f.write(css_content)

        plugin = _TailwindCSSPlugin(mode='offline')
        plugin.output_css_path = css_file

        # Test normal case
        result = plugin._serve_tailwindcss()
        assert result is not None

        # Test exception handling in send_file
        with patch('flask.send_file', side_effect=Exception('Test exception')):
            result = plugin._serve_tailwindcss()
            assert result is not None

        # Test when CSS file does not exist
        plugin.output_css_path = 'nonexistent.css'
        result = plugin._serve_tailwindcss()
        assert result is not None

    def test_tailwind_v4_cdn_handling(self):
        """Test Tailwind CSS v4 CDN URL handling."""
        # Test URL replacement when mode is 'online', tailwind_version is '4' and cdn_url is default value
        plugin = _TailwindCSSPlugin(mode='online', tailwind_version='4')
        expected_url = 'https://registry.npmmirror.com/@tailwindcss/browser/4/files/dist/index.global.js'
        assert plugin.cdn_url == expected_url

        # Test that no replacement occurs when mode is 'online', tailwind_version is '4' and custom cdn_url is provided
        custom_cdn_url = 'https://custom.cdn.com/tailwindcss4.js'
        plugin = _TailwindCSSPlugin(mode='online', tailwind_version='4', cdn_url=custom_cdn_url)
        assert plugin.cdn_url == custom_cdn_url

    def test_build_tailwindcss(self):
        """Test _build_tailwindcss method."""
        # Create a TailwindCommand mock object
        mock_tailwind_command = MagicMock()
        mock_built = MagicMock()
        mock_tailwind_command.init.return_value = mock_tailwind_command
        mock_tailwind_command.install.return_value = mock_tailwind_command
        mock_tailwind_command.build.return_value = mock_built
        mock_built.clean = MagicMock()

        # Test with clean_after=True
        plugin = _TailwindCSSPlugin(mode='offline', clean_after=True)
        plugin.tailwind_command = mock_tailwind_command
        plugin._build_tailwindcss()
        mock_built.clean.assert_called_once()

        # Test with clean_after=False
        plugin = _TailwindCSSPlugin(mode='offline', clean_after=False)
        plugin.tailwind_command = mock_tailwind_command
        mock_built.clean.reset_mock()
        plugin._build_tailwindcss()
        mock_built.clean.assert_not_called()

    def test_decorated_functions_execution(self):
        """Test the execution of functions decorated by hooks."""
        # Create a temporary CSS file
        css_content = 'body { color: red; }'
        css_file = os.path.join(self.test_dir, 'test.css')
        with open(css_file, 'w') as f:
            f.write(css_content)

        plugin = _TailwindCSSPlugin(mode='offline')
        plugin.output_css_path = css_file

        # Modify file modification time to recent (1 second ago) to ensure _should_skip_build returns True
        recent_time = time.time() - 1
        os.utime(css_file, (recent_time, recent_time))

        # Mock the hooks to capture the decorated functions
        with patch('dash_tailwindcss_plugin.plugin.hooks') as mock_hooks:
            # Define a decorator that captures the function
            captured_funcs = []

            def mock_decorator(fn):
                captured_funcs.append(fn)
                return fn

            # Set the mock hooks to return our decorator
            mock_hooks.setup.return_value = mock_decorator
            mock_hooks.route.return_value = mock_decorator
            mock_hooks.index.return_value = mock_decorator

            # Call setup_offline_mode to register the functions
            plugin.setup_offline_mode()

            # We should have captured 3 functions: setup, route, and index
            assert len(captured_funcs) == 3

            # The first function should be generate_tailwindcss (from hooks.setup)
            generate_tailwindcss_func = captured_funcs[0]

            # Call this function with a mock app - this will execute the return statement when _should_skip_build returns True
            mock_app = MagicMock()
            generate_tailwindcss_func(mock_app)

            # The second function should be serve_tailwindcss (from hooks.route)
            serve_tailwindcss_func = captured_funcs[1]

            # Call this function - this will execute the return statement in _serve_tailwindcss
            serve_tailwindcss_func()

            # The third function should be add_tailwindcss_link (from hooks.index)
            add_tailwindcss_link_func = captured_funcs[2]

            # Call this function with a test HTML string
            test_html = '<html><head></head><body><h1>Test</h1></body></html>'
            result = add_tailwindcss_link_func(test_html)
            assert '<link rel="stylesheet"' in result


if __name__ == '__main__':
    pytest.main([__file__])
