#!/usr/bin/env python3
"""
Simple tests for the TailwindCSS plugin with Dash.

These tests verify that the plugin integrates correctly with Dash applications
without requiring browser automation.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestDashSimple:
    """Simple test cases for Dash integration with the TailwindCSS plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plugin_setup_with_dash_app(self):
        """Test that the plugin can be set up with a Dash app."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup the plugin - this should not raise an exception
        setup_tailwindcss_plugin(mode='online')

        # Define a simple layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Test', className='text-3xl font-bold text-blue-600'),
                html.P('Test paragraph', className='text-gray-700 mt-4'),
            ]
        )

        # Verify that the app was created successfully
        assert app is not None
        assert hasattr(app, 'layout')

    def test_plugin_setup_offline_mode(self):
        """Test that the plugin can be set up in offline mode."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup the plugin in offline mode
        with patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_offline_mode') as mock_setup:
            setup_tailwindcss_plugin(mode='offline')
            mock_setup.assert_called_once()

        # Define a simple layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Test', className='text-3xl font-bold text-green-600'),
                html.P('Test paragraph', className='text-gray-700 mt-4'),
            ]
        )

        # Verify that the app was created successfully
        assert app is not None
        assert hasattr(app, 'layout')

    def test_plugin_setup_with_custom_config(self):
        """Test that the plugin can be set up with custom configuration."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup the plugin with custom configuration
        with patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_offline_mode') as mock_setup:
            setup_tailwindcss_plugin(
                mode='offline',
                content_path=['*.html'],
                input_css_path='custom_input.css',
                output_css_path='custom_output.css',
                config_js_path='custom_config.js',
            )
            mock_setup.assert_called_once()

        # Define a simple layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Test', className='text-3xl font-bold text-red-600'),
                html.P('Test paragraph', className='text-gray-700 mt-4'),
            ]
        )

        # Verify that the app was created successfully
        assert app is not None
        assert hasattr(app, 'layout')

    def test_plugin_setup_with_theme_config(self):
        """Test that the plugin can be set up with theme configuration."""
        # Create a Dash app
        app = Dash(__name__)

        # Define custom theme configuration
        theme_config = {'colors': {'brand': {'500': '#3b82f6'}}}

        # Setup the plugin with theme configuration
        with patch('dash_tailwindcss_plugin.plugin._TailwindCSSPlugin.setup_online_mode') as mock_setup:
            setup_tailwindcss_plugin(mode='online', tailwind_theme_config=theme_config)
            mock_setup.assert_called_once()

        # Define a simple layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Test', className='text-3xl font-bold text-brand-500'),
                html.P('Test paragraph', className='text-gray-700 mt-4'),
            ]
        )

        # Verify that the app was created successfully
        assert app is not None
        assert hasattr(app, 'layout')


if __name__ == '__main__':
    pytest.main([__file__])
