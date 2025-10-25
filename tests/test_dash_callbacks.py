#!/usr/bin/env python3
"""
Callback tests for the TailwindCSS plugin.

These tests use the dash_duo pytest fixture to test the plugin's callbacks
with a real Dash application.
"""

import pytest
from dash import Dash, html, Input, Output, callback
from dash.testing.composite import DashComposite
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestDashCallbacks:
    """Test cases for Dash callbacks with the TailwindCSS plugin."""

    def test_callback_with_tailwind_classes(self, dash_duo: DashComposite):
        """Test that callbacks work correctly with TailwindCSS classes."""
        # Create a Dash app
        app = Dash(__name__)

        # Setup TailwindCSS plugin
        setup_tailwindcss_plugin(mode='online')

        # Define app layout with interactive elements
        app.layout = html.Div(
            [
                html.H1('Callback Test', className='text-3xl font-bold text-blue-600'),
                html.Button(
                    'Click Me',
                    id='click-button',
                    className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded',
                ),
                html.Div(id='output-div', className='mt-4 p-4 bg-gray-100 rounded'),
            ]
        )

        @callback(Output('output-div', 'children'), Input('click-button', 'n_clicks'))
        def update_output(n_clicks):
            if n_clicks is None:
                n_clicks = 0
            return f'Button clicked {n_clicks} times'

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Callback Test')

        # Check initial state
        dash_duo.wait_for_text_to_equal('#output-div', 'Button clicked 0 times')

        # Click the button
        dash_duo.find_element('#click-button').click()

        # Check updated state
        dash_duo.wait_for_text_to_equal('#output-div', 'Button clicked 1 times')

        # Click the button again
        dash_duo.find_element('#click-button').click()

        # Check updated state
        dash_duo.wait_for_text_to_equal('#output-div', 'Button clicked 2 times')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'


if __name__ == '__main__':
    pytest.main([__file__])
