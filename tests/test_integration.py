import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
from dash import Dash
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestIntegration:
    """Integration test cases for the plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_online_mode')
    def test_setup_tailwindcss_plugin_online_mode(self, mock_setup_online):
        """Test setup_tailwindcss_plugin with online mode integration."""
        # This test verifies that the plugin can be set up with online mode
        setup_tailwindcss_plugin(mode='online')
        mock_setup_online.assert_called_once()

    @patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_offline_mode')
    def test_setup_tailwindcss_plugin_offline_mode(self, mock_setup_offline):
        """Test setup_tailwindcss_plugin with offline mode integration."""
        # This test verifies that the plugin can be set up with offline mode
        setup_tailwindcss_plugin(mode='offline')
        mock_setup_offline.assert_called_once()

    @patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_offline_mode')
    def test_setup_tailwindcss_plugin_with_custom_config(self, mock_setup_offline):
        """Test setup_tailwindcss_plugin with custom configuration."""
        # This test verifies that the plugin can be set up with custom configuration
        setup_tailwindcss_plugin(
            mode='offline',
            content_path=['*.html'],
            input_css_path='custom_input.css',
            output_css_path='custom_output.css',
            config_js_path='custom_config.js',
        )
        mock_setup_offline.assert_called_once()

    def test_setup_tailwindcss_plugin_with_dash_app(self):
        """Test setup_tailwindcss_plugin with actual Dash app creation."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup the plugin
        setup_tailwindcss_plugin(mode='online')

        # Verify that the app was created successfully
        assert app is not None
        assert hasattr(app, 'layout') or hasattr(app, '_layout') or hasattr(app, '_layout_value')


if __name__ == '__main__':
    pytest.main([__file__])
