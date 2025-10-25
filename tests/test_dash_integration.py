#!/usr/bin/env python3
"""
Dash integration tests for the TailwindCSS plugin.

These tests use the dash_duo pytest fixture to test the plugin's integration
with a real Dash application.
"""

import pytest
from dash import Dash, html
from dash.testing.composite import DashComposite
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestDashIntegration:
    """Test cases for Dash integration with the TailwindCSS plugin."""

    def test_online_mode_integration(self, dash_duo: DashComposite):
        """Test the plugin works in online mode with a Dash app."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup TailwindCSS plugin in online mode
        setup_tailwindcss_plugin(mode='online')

        # Define app layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Test App', className='text-3xl font-bold text-blue-600'),
                html.P('This is a test paragraph.', className='text-gray-700 mt-4'),
                html.Button(
                    'Click Me',
                    id='test-button',
                    className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded',
                ),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Test App')

        # Check that the H1 element has the expected Tailwind classes applied
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the paragraph is rendered
        dash_duo.wait_for_text_to_equal('p', 'This is a test paragraph.')

        # Check that the button is rendered
        button_element = dash_duo.find_element('#test-button')
        assert button_element is not None

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_offline_mode_integration(self, dash_duo: DashComposite):
        """Test the plugin works in offline mode with a Dash app."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup TailwindCSS plugin in offline mode
        setup_tailwindcss_plugin(mode='offline')

        # Define app layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Offline Test App', className='text-3xl font-bold text-green-600'),
                html.P('This is a test paragraph in offline mode.', className='text-gray-700 mt-4'),
                html.Div(
                    [
                        html.Button(
                            'Primary',
                            className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2',
                        ),
                        html.Button(
                            'Secondary',
                            className='bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded',
                        ),
                    ],
                    className='mt-4',
                ),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Offline Test App')

        # Check that the H1 element is rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the paragraph is rendered
        dash_duo.wait_for_text_to_equal('p', 'This is a test paragraph in offline mode.')

        # Check that both buttons are rendered
        primary_button = dash_duo.find_element('button:nth-child(1)')
        secondary_button = dash_duo.find_element('button:nth-child(2)')
        assert primary_button is not None
        assert secondary_button is not None

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_custom_theme_integration(self, dash_duo: DashComposite):
        """Test the plugin works with custom theme configuration."""
        # Create a Dash app
        app = Dash(__name__)

        # Define custom theme configuration
        theme_config = {'colors': {'brand': {'500': '#3b82f6'}}}

        # Setup TailwindCSS plugin with custom theme
        setup_tailwindcss_plugin(mode='online', tailwind_theme_config=theme_config)

        # Define app layout with custom theme classes
        app.layout = html.Div(
            [
                html.H1('Custom Theme Test', className='text-3xl font-bold text-brand-500'),
                html.P('This uses a custom brand color.', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Custom Theme Test')

        # Check that the H1 element is rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the paragraph is rendered
        dash_duo.wait_for_text_to_equal('p', 'This uses a custom brand color.')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'


if __name__ == '__main__':
    pytest.main([__file__])
