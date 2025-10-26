import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
from dash_tailwindcss_plugin.plugin import _TailwindCSSPlugin, setup_tailwindcss_plugin


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
        """Test plugin initialization with default parameters."""
        plugin = _TailwindCSSPlugin()

        assert plugin.mode == 'offline'
        assert plugin.content_path == ['**/*.py']
        assert plugin.input_css_path == '.tailwind/tailwind_input.css'
        assert plugin.output_css_path == '.tailwind/tailwind.css'
        assert plugin.config_js_path == '.tailwind/tailwind.config.js'
        assert plugin.cdn_url == 'https://cdn.tailwindcss.com'
        assert plugin.download_node is False
        assert plugin.node_version == '18.17.0'
        assert plugin.tailwind_theme_config == {}
        assert plugin.clean_after is True

    def test_plugin_initialization_with_custom_parameters(self):
        """Test plugin initialization with custom parameters."""
        custom_content_path = ['*.html', '*.js']
        plugin = _TailwindCSSPlugin(
            mode='online',
            content_path=custom_content_path,
            input_css_path='custom_input.css',
            output_css_path='custom_output.css',
            config_js_path='custom_config.js',
            cdn_url='https://custom.cdn.com',
            download_node=True,
            node_version='16.0.0',
            tailwind_theme_config={'colors': {'primary': '#ff0000'}},
            clean_after=False,
        )

        assert plugin.mode == 'online'
        assert plugin.content_path == custom_content_path
        assert plugin.input_css_path == 'custom_input.css'
        assert plugin.output_css_path == 'custom_output.css'
        assert plugin.config_js_path == 'custom_config.js'
        assert plugin.cdn_url == 'https://custom.cdn.com'
        assert plugin.download_node is True
        assert plugin.node_version == '16.0.0'
        assert plugin.tailwind_theme_config == {'colors': {'primary': '#ff0000'}}
        assert plugin.clean_after is False

    @patch('dash_tailwindcss_plugin.plugin.hooks')
    def test_setup_online_mode(self, mock_hooks):
        """Test setup_online_mode method."""
        plugin = _TailwindCSSPlugin(mode='online')
        plugin.setup_online_mode()

        # Verify that hooks.index() decorator was called
        mock_hooks.index.assert_called_once()

    @patch('dash_tailwindcss_plugin.plugin.hooks')
    @patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin._build_tailwindcss')
    def test_setup_offline_mode(self, mock_build, mock_hooks):
        """Test setup_offline_mode method."""
        plugin = _TailwindCSSPlugin(mode='offline')
        plugin.setup_offline_mode()

        # Verify that hooks.setup() decorator was called
        mock_hooks.setup.assert_called_once()

    def test_setup_tailwindcss_plugin_online(self):
        """Test setup_tailwindcss_plugin function with online mode."""
        with patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_online_mode') as mock_setup_online:
            setup_tailwindcss_plugin(mode='online')
            mock_setup_online.assert_called_once()

    def test_setup_tailwindcss_plugin_offline(self):
        """Test setup_tailwindcss_plugin function with offline mode."""
        with patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_offline_mode') as mock_setup_offline:
            setup_tailwindcss_plugin(mode='offline')
            mock_setup_offline.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
