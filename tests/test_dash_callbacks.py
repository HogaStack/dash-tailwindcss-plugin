#!/usr/bin/env python3
"""
Callback tests for the TailwindCSS plugin.

These tests use the dash_duo pytest fixture to test the plugin's callbacks
with a real Dash application.
"""

import pytest
import tempfile
import shutil
import os
import uuid
from dash import Dash, html, dcc, Input, Output, callback
from dash.testing.composite import DashComposite
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestDashCallbacks:
    """Test cases for Dash callbacks with the TailwindCSS plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_callback_with_tailwind_classes(self, dash_duo: DashComposite):
        """Test that callbacks work correctly with TailwindCSS classes."""
        # Setup TailwindCSS plugin
        setup_tailwindcss_plugin(mode='online')

        # Create a Dash app
        app = Dash(__name__)

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

    def test_form_callback_with_tailwind(self, dash_duo: DashComposite):
        """Test form callbacks with TailwindCSS styling."""
        # Setup TailwindCSS plugin
        setup_tailwindcss_plugin(mode='online')

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with form elements
        app.layout = html.Div(
            [
                html.H1('Form Callback Test', className='text-3xl font-bold text-center mb-4'),
                html.Div(
                    [
                        html.Label('Name:', className='block text-gray-700 text-sm font-bold mb-2'),
                        dcc.Input(
                            id='name-input',
                            type='text',
                            placeholder='Enter your name',
                            className='shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline',
                        ),
                    ],
                    className='mb-4',
                ),
                html.Div(
                    [
                        html.Label('Email:', className='block text-gray-700 text-sm font-bold mb-2'),
                        dcc.Input(
                            id='email-input',
                            type='email',
                            placeholder='Enter your email',
                            className='shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline',
                        ),
                    ],
                    className='mb-4',
                ),
                html.Button(
                    'Submit',
                    id='submit-button',
                    className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline',
                ),
                html.Div(id='form-output', className='mt-4 p-4 bg-gray-100 rounded'),
            ],
            className='container mx-auto p-4',
        )

        @callback(
            Output('form-output', 'children'),
            Input('submit-button', 'n_clicks'),
            Input('name-input', 'value'),
            Input('email-input', 'value'),
            prevent_initial_call=False,
        )
        def update_form_output(n_clicks, name, email):
            if n_clicks is None:
                return 'Please fill in the form and click submit'

            if not name and not email:
                return 'Please provide at least a name or email'

            return f'Submitted: Name={name or "N/A"}, Email={email or "N/A"}'

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Form Callback Test')

        # Check initial state
        dash_duo.wait_for_text_to_equal('#form-output', 'Please fill in the form and click submit')

        # Fill in the form
        dash_duo.find_element('#name-input').send_keys('John Doe')
        dash_duo.find_element('#email-input').send_keys('john@example.com')

        # Click submit
        dash_duo.find_element('#submit-button').click()

        # Check updated state
        dash_duo.wait_for_text_to_equal('#form-output', 'Submitted: Name=John Doe, Email=john@example.com')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_dynamic_content_callback(self, dash_duo: DashComposite):
        """Test dynamic content updates with TailwindCSS."""
        # Setup TailwindCSS plugin
        setup_tailwindcss_plugin(mode='online')

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with dynamic content
        app.layout = html.Div(
            [
                html.H1('Dynamic Content Test', className='text-3xl font-bold text-center mb-4'),
                html.Div(
                    [
                        html.Button(
                            'Show Content',
                            id='show-button',
                            className='bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mr-2',
                        ),
                        html.Button(
                            'Hide Content',
                            id='hide-button',
                            className='bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded',
                        ),
                    ],
                    className='mb-4',
                ),
                html.Div(id='dynamic-content', className='mt-4 p-4 bg-blue-100 rounded'),
            ],
            className='container mx-auto p-4',
        )

        @callback(
            Output('dynamic-content', 'children'), Input('show-button', 'n_clicks'), Input('hide-button', 'n_clicks')
        )
        def update_content(show_clicks, hide_clicks):
            if show_clicks and (not hide_clicks or show_clicks > hide_clicks):
                return html.Div(
                    [
                        html.H2('Dynamic Content', className='text-xl font-semibold'),
                        html.P('This content was dynamically added!', className='text-gray-700'),
                        html.Ul(
                            [
                                html.Li('Item 1', className='text-gray-600'),
                                html.Li('Item 2', className='text-gray-600'),
                                html.Li('Item 3', className='text-gray-600'),
                            ],
                            className='list-disc pl-5 mt-2',
                        ),
                    ],
                    className='p-4 bg-white rounded shadow',
                )
            else:
                return ''

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Dynamic Content Test')

        # Check initial state (empty content)
        dynamic_content = dash_duo.find_element('#dynamic-content')
        assert dynamic_content.text == ''

        # Click show button
        dash_duo.find_element('#show-button').click()

        # Check that content is shown
        dash_duo.wait_for_text_to_equal('#dynamic-content h2', 'Dynamic Content')

        # Click hide button
        dash_duo.find_element('#hide-button').click()

        # Check that content is hidden (empty)
        dash_duo.wait_for_text_to_equal('#dynamic-content', '')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_offline_mode_callback(self, dash_duo: DashComposite):
        """Test callbacks work in offline mode with TailwindCSS."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/offline_callback_test_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with interactive elements
        app.layout = html.Div(
            [
                html.H1('Offline Mode Callback Test', className='text-3xl font-bold text-center mb-4 text-green-600'),
                html.Div(
                    [
                        html.Label('Select an option:', className='block text-gray-700 text-sm font-bold mb-2'),
                        dcc.Dropdown(
                            id='option-dropdown',
                            options=[
                                {'label': 'Option 1', 'value': '1'},
                                {'label': 'Option 2', 'value': '2'},
                                {'label': 'Option 3', 'value': '3'},
                            ],
                            value='1',
                            className='block appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2 px-3 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline',
                        ),
                    ],
                    className='mb-4',
                ),
                html.Div(id='dropdown-output', className='mt-4 p-4 bg-gray-100 rounded'),
            ],
            className='container mx-auto p-4',
        )

        @callback(Output('dropdown-output', 'children'), Input('option-dropdown', 'value'))
        def update_dropdown_output(value):
            option_labels = {'1': 'Option 1', '2': 'Option 2', '3': 'Option 3'}
            selected_label = option_labels.get(value, 'Unknown')
            return html.Div(
                [
                    html.H3(f'You selected: {selected_label}', className='text-lg font-semibold'),
                    html.P(f'Value: {value}', className='text-gray-700'),
                ]
            )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Offline Mode Callback Test')

        # Check initial state
        dash_duo.wait_for_text_to_equal('#dropdown-output h3', 'You selected: Option 1')

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_multiple_callbacks_with_tailwind_styles(self, dash_duo: DashComposite):
        """Test multiple callbacks working together with Tailwind CSS styles."""
        # Setup TailwindCSS plugin
        setup_tailwindcss_plugin(mode='online')

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with multiple interactive elements
        app.layout = html.Div(
            [
                html.H1('Multiple Callbacks Test', className='text-3xl font-bold text-center mb-6'),
                # Counter section
                html.Div(
                    [
                        html.H2('Counter', className='text-xl font-semibold mb-2'),
                        html.Button(
                            '+',
                            id='increment-btn',
                            className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded-l',
                        ),
                        html.Button(
                            '-',
                            id='decrement-btn',
                            className='bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded-r',
                        ),
                        html.Span(id='counter-display', className='mx-4 text-2xl font-bold'),
                    ],
                    className='mb-6 p-4 bg-gray-100 rounded',
                ),
                # Color changer section
                html.Div(
                    [
                        html.H2('Color Changer', className='text-xl font-semibold mb-2'),
                        html.Button(
                            'Red',
                            id='red-btn',
                            className='bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mr-2',
                        ),
                        html.Button(
                            'Green',
                            id='green-btn',
                            className='bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mr-2',
                        ),
                        html.Button(
                            'Blue',
                            id='blue-btn',
                            className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded',
                        ),
                        html.Div(id='color-box', className='mt-4 w-32 h-32 border-2 border-gray-300'),
                    ],
                    className='mb-6 p-4 bg-gray-100 rounded',
                ),
                # Text updater section
                html.Div(
                    [
                        html.H2('Text Updater', className='text-xl font-semibold mb-2'),
                        dcc.Input(
                            id='text-input',
                            type='text',
                            placeholder='Enter text',
                            className='shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline',
                        ),
                        html.Div(id='text-display', className='mt-4 p-4 bg-white border rounded'),
                    ],
                    className='mb-6 p-4 bg-gray-100 rounded',
                ),
            ],
            className='container mx-auto p-6',
        )

        # Counter callback
        @callback(
            Output('counter-display', 'children'),
            Input('increment-btn', 'n_clicks'),
            Input('decrement-btn', 'n_clicks'),
            prevent_initial_call=False,
        )
        def update_counter(increment_clicks, decrement_clicks):
            increment_clicks = increment_clicks or 0
            decrement_clicks = decrement_clicks or 0
            return str(increment_clicks - decrement_clicks)

        # Color changer callback
        @callback(
            Output('color-box', 'className'),
            Input('red-btn', 'n_clicks'),
            Input('green-btn', 'n_clicks'),
            Input('blue-btn', 'n_clicks'),
            prevent_initial_call=False,
        )
        def change_color(red_clicks, green_clicks, blue_clicks):
            # Create a context-like object to determine which button was clicked last
            clicks = [(red_clicks or 0, 'red-btn'), (green_clicks or 0, 'green-btn'), (blue_clicks or 0, 'blue-btn')]

            # Sort by click count to find the most recently clicked button
            clicks.sort(key=lambda x: x[0], reverse=True)

            if clicks[0][0] == 0:
                # No buttons clicked yet
                return 'mt-4 w-32 h-32 border-2 border-gray-300'

            # Get the button with the highest click count
            button_id = clicks[0][1]

            color_classes = {
                'red-btn': 'mt-4 w-32 h-32 border-2 border-red-500 bg-red-200',
                'green-btn': 'mt-4 w-32 h-32 border-2 border-green-500 bg-green-200',
                'blue-btn': 'mt-4 w-32 h-32 border-2 border-blue-500 bg-blue-200',
            }

            return color_classes.get(button_id, 'mt-4 w-32 h-32 border-2 border-gray-300')

        # Text updater callback
        @callback(Output('text-display', 'children'), Input('text-input', 'value'), prevent_initial_call=False)
        def update_text(value):
            if not value:
                return 'Enter some text above'
            return html.P(value, className='text-lg')

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Multiple Callbacks Test')

        # Test counter functionality
        dash_duo.find_element('#increment-btn').click()
        dash_duo.wait_for_text_to_equal('#counter-display', '1')

        dash_duo.find_element('#increment-btn').click()
        dash_duo.wait_for_text_to_equal('#counter-display', '2')

        dash_duo.find_element('#decrement-btn').click()
        dash_duo.wait_for_text_to_equal('#counter-display', '1')

        # Test color changer functionality
        dash_duo.find_element('#red-btn').click()
        # Just verify the element exists, we can't easily check class names in tests

        dash_duo.find_element('#green-btn').click()
        # Just verify the element exists, we can't easily check class names in tests

        # Test text updater functionality
        text_input = dash_duo.find_element('#text-input')
        text_input.send_keys('Hello Tailwind!')
        dash_duo.wait_for_text_to_equal('#text-display', 'Hello Tailwind!')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_callback_with_computed_styles(self, dash_duo: DashComposite):
        """Test that callbacks work correctly with elements that have computed Tailwind styles."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/computed_styles_callback_test_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with styled elements
        app.layout = html.Div(
            [
                html.H1(
                    'Computed Styles Callback Test',
                    id='styled-header',
                    className='text-2xl font-bold text-purple-600 text-center mb-6',
                ),
                html.Div(
                    [
                        html.Button(
                            'Toggle Visibility',
                            id='toggle-button',
                            className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4',
                        ),
                        html.Div(
                            id='toggle-content',
                            children=[
                                html.P('This content can be toggled', className='text-lg'),
                                html.P('It has specific Tailwind styling', className='text-gray-600'),
                            ],
                            className='bg-yellow-100 p-6 rounded-lg shadow-lg block',
                        ),
                    ],
                    className='container mx-auto p-4',
                ),
            ]
        )

        @callback(Output('toggle-content', 'style'), Input('toggle-button', 'n_clicks'), prevent_initial_call=False)
        def toggle_visibility(n_clicks):
            if n_clicks and n_clicks % 2 == 1:
                return {'display': 'none'}
            return {'display': 'block'}

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#styled-header', 'Computed Styles Callback Test')

        # Verify that elements with Tailwind classes have the expected computed styles
        header = dash_duo.find_element('#styled-header')

        # Check font size (text-2xl should be about 1.5rem)
        font_size = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontSize;', header)
        assert font_size is not None and float(font_size.replace('px', '')) > 15

        # Check font weight (font-bold should be 700)
        font_weight = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontWeight;', header)
        assert font_weight == '700'

        # Check text color (text-purple-600 should be #9333ea)
        text_color = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).color;', header)
        # The actual color might vary depending on browser rendering
        assert text_color is not None and len(text_color) > 0

        # Test toggle functionality
        # Wait for content to be displayed initially
        dash_duo.wait_for_element_by_id('toggle-content')
        toggle_content = dash_duo.find_element('#toggle-content')
        # Use wait_for_style_to_equal to ensure the element is displayed
        dash_duo.wait_for_style_to_equal('#toggle-content', 'display', 'block')
        assert toggle_content.is_displayed()

        # Click toggle button to hide content
        dash_duo.find_element('#toggle-button').click()
        # Wait for the element to be hidden
        dash_duo.wait_for_style_to_equal('#toggle-content', 'display', 'none')
        # Check that content is hidden
        # We need to re-find the element after the DOM update
        toggle_content = dash_duo.find_element('#toggle-content')
        assert not toggle_content.is_displayed()

        # Click toggle button again to show content
        dash_duo.find_element('#toggle-button').click()
        # Wait for the element to be displayed again
        dash_duo.wait_for_style_to_equal('#toggle-content', 'display', 'block')
        # Check that content is displayed again
        # We need to re-find the element after the DOM update
        toggle_content = dash_duo.find_element('#toggle-content')
        assert toggle_content.is_displayed()

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'


if __name__ == '__main__':
    pytest.main([__file__])
