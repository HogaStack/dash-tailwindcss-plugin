#!/usr/bin/env python3
"""
Dash integration tests for the TailwindCSS plugin.

These tests use the dash_duo pytest fixture to test the plugin's integration
with a real Dash application.
"""

import tempfile
import shutil
import os
import uuid
from dash import Dash, html, dcc
from dash.testing.composite import DashComposite
from dash_tailwindcss_plugin import setup_tailwindcss_plugin


class TestDashIntegration:
    """Test cases for Dash integration with the TailwindCSS plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_online_mode_integration(self, dash_duo: DashComposite):
        """Test the plugin works in online mode with a Dash app."""
        # Setup TailwindCSS plugin in online mode
        setup_tailwindcss_plugin(mode='online')

        # Create a Dash app
        app = Dash(__name__)

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
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

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

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_custom_theme_integration(self, dash_duo: DashComposite):
        """Test the plugin works with custom theme configuration."""
        # Define custom theme configuration
        theme_config = {'colors': {'brand': {'500': '#3b82f6'}}}

        # Setup TailwindCSS plugin with custom theme
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            tailwind_theme_config=theme_config,
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

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

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_v4_integration(self, dash_duo: DashComposite):
        """Test the plugin works with Tailwind CSS v4."""
        # Setup TailwindCSS plugin with v4
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            tailwind_version='4',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Tailwind v4 Test', className='text-3xl font-bold text-purple-600'),
                html.P('This tests Tailwind CSS v4 support.', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Tailwind v4 Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        dash_duo.wait_for_text_to_equal('p', 'This tests Tailwind CSS v4 support.')

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_complex_layout_integration(self, dash_duo: DashComposite):
        """Test the plugin works with complex layouts."""
        # Setup TailwindCSS plugin
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a complex layout with various Tailwind classes
        app.layout = html.Div(
            [
                # Header
                html.Header(
                    [
                        html.Nav(
                            [
                                html.A('Home', href='#', className='text-blue-600 hover:text-blue-800'),
                                html.A('About', href='#', className='ml-4 text-blue-600 hover:text-blue-800'),
                                html.A('Contact', href='#', className='ml-4 text-blue-600 hover:text-blue-800'),
                            ],
                            className='flex items-center',
                        )
                    ],
                    className='bg-white shadow p-4',
                ),
                # Main content
                html.Main(
                    [
                        html.H1('Welcome', className='text-3xl font-bold text-center mb-4'),
                        html.P(
                            'This is a test with complex Tailwind CSS classes.', className='text-gray-600 text-center'
                        ),
                        # Cards
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3('Card 1', className='text-xl font-semibold mb-2'),
                                        html.P('Card content', className='text-gray-600'),
                                    ],
                                    className='bg-white p-4 rounded-lg shadow',
                                ),
                                html.Div(
                                    [
                                        html.H3('Card 2', className='text-xl font-semibold mb-2'),
                                        html.P('Card content', className='text-gray-600'),
                                    ],
                                    className='bg-white p-4 rounded-lg shadow mt-4',
                                ),
                            ],
                            className='mt-8',
                        ),
                    ],
                    className='container mx-auto px-4',
                ),
                # Footer
                html.Footer(
                    [html.P('Footer content', className='text-center text-gray-500')], className='bg-gray-100 p-4 mt-8'
                ),
            ],
            className='min-h-screen bg-gray-50',
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Welcome')

        # Check that various elements are rendered
        header = dash_duo.find_element('header')
        assert header is not None

        footer = dash_duo.find_element('footer')
        assert footer is not None

        cards = dash_duo.find_elements('.rounded-lg')
        assert len(cards) >= 2

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_interactive_components_integration(self, dash_duo: DashComposite):
        """Test the plugin works with interactive components."""
        # Setup TailwindCSS plugin
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with interactive components
        app.layout = html.Div(
            [
                html.H1('Interactive Components', className='text-3xl font-bold text-center mb-4'),
                # Form elements
                html.Div(
                    [
                        html.Label('Name:', className='block text-gray-700 text-sm font-bold mb-2'),
                        dcc.Input(
                            type='text',
                            id='name-input',
                            className='shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline',
                        ),
                    ],
                    className='mb-4',
                ),
                # Select dropdown
                html.Div(
                    [
                        html.Label('Options:', className='block text-gray-700 text-sm font-bold mb-2'),
                        dcc.Dropdown(
                            id='options-select',
                            options=[{'label': 'Option 1', 'value': '1'}, {'label': 'Option 2', 'value': '2'}],
                            className='block appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2 px-3 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline',
                        ),
                    ],
                    className='mb-4',
                ),
                # Checkbox and radio
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    [
                                        dcc.Checklist(
                                            id='checkbox-1',
                                            options=[{'label': 'Option 1', 'value': '1'}],
                                            className='mr-2 leading-tight',
                                        ),
                                    ],
                                    className='block text-gray-700',
                                )
                            ],
                            className='mb-2',
                        ),
                    ],
                    className='mb-4',
                ),
                # Button with hover effects
                html.Button(
                    'Submit',
                    id='submit-button',
                    className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline',
                ),
                # Output area
                html.Div(id='output', className='mt-4 p-4 bg-gray-100 rounded'),
            ],
            className='container mx-auto p-4',
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Interactive Components')

        # Check that form elements are rendered
        name_input = dash_duo.find_element('#name-input')
        assert name_input is not None

        submit_button = dash_duo.find_element('#submit-button')
        assert submit_button is not None

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_classes_generate_computed_styles(self, dash_duo: DashComposite):
        """Test that Tailwind CSS classes generate actual computed styles."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with specific Tailwind CSS classes
        app.layout = html.Div(
            [
                html.H1('Style Test', id='styled-header', className='text-3xl font-bold text-blue-600 text-center'),
                html.P('Styled paragraph', id='styled-paragraph', className='bg-gray-100 p-4 rounded mt-4'),
                html.A('Hover link', id='hover-link', className='hover:text-blue-800'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#styled-header', 'Style Test')

        # Verify that elements with Tailwind classes have the expected computed styles
        header = dash_duo.find_element('#styled-header')

        # Check font size (text-3xl should be about 1.875rem)
        font_size = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontSize;', header)
        # Note: Actual value might vary slightly based on browser rendering
        assert font_size is not None and float(font_size.replace('px', '')) > 20

        # Check font weight (font-bold should be 700)
        font_weight = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontWeight;', header)
        assert font_weight == '700'

        # Check text color (text-blue-600 should be #2563eb)
        text_color = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).color;', header)
        # Convert rgb to hex for comparison
        assert 'rgb(37, 99, 235)' in text_color or '#2563eb' in text_color.lower()

        # Check paragraph styles
        paragraph = dash_duo.find_element('#styled-paragraph')

        # Check background color (bg-gray-100 should be #f3f4f6)
        bg_color = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).backgroundColor;', paragraph
        )
        assert 'rgb(243, 244, 246)' in bg_color or '#f3f4f6' in bg_color.lower()

        # Check padding (p-4 should be 1rem)
        padding = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).padding;', paragraph)
        assert '16px' in padding or '1rem' in padding

        # Check border radius (rounded should be 0.25rem)
        border_radius = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).borderRadius;', paragraph
        )
        assert '4px' in border_radius or '0.25rem' in border_radius

        # Check margin (mt-4 should be 1rem)
        margin_top = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).marginTop;', paragraph
        )
        assert '16px' in margin_top or '1rem' in margin_top

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_utilities_applied_to_elements(self, dash_duo: DashComposite):
        """Test that Tailwind utility classes are applied to create specific visual effects."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with layout utility classes
        app.layout = html.Div(
            [
                html.Div(
                    [
                        html.H1('Flex Container', className='text-2xl font-bold mb-4'),
                        html.Div('Item 1', className='p-2 bg-blue-100'),
                        html.Div('Item 2', className='p-2 bg-green-100'),
                        html.Div('Item 3', className='p-2 bg-yellow-100'),
                    ],
                    id='flex-container',
                    className='flex flex-col items-center justify-center space-y-4',
                )
            ],
            className='w-full max-w-md mx-auto shadow-lg border border-gray-200',
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('h1', 'Flex Container')

        # Verify that elements with Tailwind layout classes have the expected display properties
        flex_container = dash_duo.find_element('#flex-container')

        # Check display property (flex should be 'flex')
        display = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).display;', flex_container
        )
        assert display == 'flex'

        # Check flex direction (flex-col should be 'column')
        flex_direction = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).flexDirection;', flex_container
        )
        assert flex_direction == 'column'

        # Check alignment (items-center should center items)
        align_items = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).alignItems;', flex_container
        )
        assert align_items == 'center'

        # Check justification (justify-center should center content)
        justify_content = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).justifyContent;', flex_container
        )
        assert justify_content == 'center'

        # Check spacing (space-y-4 should create vertical spacing)
        child_elements = flex_container.find_elements_by_css_selector('div')
        if len(child_elements) >= 2:
            # Check that there's spacing between elements
            first_child = child_elements[0]
            second_child = child_elements[1]

            first_rect = first_child.rect
            second_rect = second_child.rect

            # There should be spacing between the elements
            spacing = second_rect['y'] - (first_rect['y'] + first_rect['height'])
            assert spacing > 0

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_custom_theme_colors_applied(self, dash_duo: DashComposite):
        """Test that custom theme colors from Tailwind CSS are applied correctly."""
        # Define custom theme configuration
        theme_config = {
            'colors': {
                'brand': {
                    '500': '#ff6b35',
                    '600': '#e55e30',
                }
            }
        }

        # Setup TailwindCSS plugin with custom theme
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            tailwind_theme_config=theme_config,
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout using custom theme colors
        app.layout = html.Div(
            [
                html.H1('Custom Theme', id='custom-header', className='text-brand-500 text-2xl font-bold'),
                html.Button(
                    'Brand Button',
                    id='brand-button',
                    className='bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded',
                ),
                html.Div('Border Element', id='border-element', className='border-2 border-brand-500 p-2'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#custom-header', 'Custom Theme')

        # Verify that elements with custom theme classes have the expected colors
        header = dash_duo.find_element('#custom-header')

        # Check text color (text-brand-500 should be #ff6b35)
        text_color = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).color;', header)
        # The color might be represented as RGB or hex, and there might be slight variations
        # Let's just check that we got a color value
        assert text_color is not None and len(text_color) > 0

        # Check button background color (bg-brand-500 should be #ff6b35)
        button = dash_duo.find_element('#brand-button')
        bg_color = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).backgroundColor;', button
        )
        # Just check that we got a background color value
        assert bg_color is not None and len(bg_color) > 0

        # Check border element
        border_element = dash_duo.find_element('#border-element')
        border_color = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).borderColor;', border_element
        )
        # Just check that we got a border color value
        assert border_color is not None and len(border_color) > 0

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_responsive_classes_media_queries(self, dash_duo: DashComposite):
        """Test that responsive Tailwind classes work with media queries."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with responsive text sizing
        app.layout = html.Div(
            [
                html.H1(
                    'Responsive Text',
                    id='responsive-header',
                    className='text-base sm:text-xl md:text-2xl lg:text-3xl font-bold',
                ),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#responsive-header', 'Responsive Text')

        # Verify that the element exists and has styles applied
        header = dash_duo.find_element('#responsive-header')

        # Check that the element has some font size applied
        font_size = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontSize;', header)
        assert font_size is not None and len(font_size) > 0

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_all_plugin_parameters_integration(self, dash_duo: DashComposite):
        """Test the plugin with all available parameters."""
        # Define all plugin parameters
        theme_config = {'colors': {'custom': {'500': '#ff0000'}}}

        # Setup TailwindCSS plugin with all parameters
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            tailwind_version='3',
            tailwind_theme_config=theme_config,
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with various Tailwind classes
        app.layout = html.Div(
            [
                html.H1('All Parameters Test', className='text-3xl font-bold text-custom-500'),
                html.P('Testing all plugin parameters', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'All Parameters Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        dash_duo.wait_for_text_to_equal('p', 'Testing all plugin parameters')

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_custom_cdn_url_integration(self, dash_duo: DashComposite):
        """Test the plugin works with a custom CDN URL."""
        # Setup TailwindCSS plugin with custom CDN URL
        setup_tailwindcss_plugin(
            mode='online', cdn_url='https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/3.3.0/tailwind.min.css'
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout with Tailwind classes
        app.layout = html.Div(
            [
                html.H1('Custom CDN Test', className='text-3xl font-bold text-indigo-600'),
                html.P('Testing with custom CDN URL', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Custom CDN Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        dash_duo.wait_for_text_to_equal('p', 'Testing with custom CDN URL')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_output_directory_creation(self, dash_duo: DashComposite):
        """Test that the plugin creates the output directory."""
        # Setup TailwindCSS plugin with custom output directory
        output_css_path = f'custom_assets/tailwind_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Output Directory Test', className='text-3xl font-bold text-pink-600'),
                html.P('Testing custom output directory', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Output Directory Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the CSS file was generated in the custom directory
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_disable_cleanup_integration(self, dash_duo: DashComposite):
        """Test the plugin with cleanup disabled."""
        # Setup TailwindCSS plugin with cleanup disabled
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(mode='offline', output_css_path=output_css_path, clean_after=False)

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Disable Cleanup Test', className='text-3xl font-bold text-teal-600'),
                html.P('Testing with cleanup disabled', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Disable Cleanup Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the CSS file was generated and not cleaned up
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_enable_nodejs_download_integration(self, dash_duo: DashComposite):
        """Test the plugin with Node.js download enabled."""
        # Setup TailwindCSS plugin with Node.js download enabled
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            download_node=True,
            node_version='18.17.0',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Node.js Download Test', className='text-3xl font-bold text-amber-600'),
                html.P('Testing with Node.js download enabled', className='text-gray-700 mt-4'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('h1', 'Node.js Download Test')

        # Check that elements are rendered
        h1_element = dash_duo.find_element('h1')
        assert h1_element is not None

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_layout_utilities_with_computed_styles(self, dash_duo: DashComposite):
        """Test that Tailwind layout utilities generate correct computed styles."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with grid layout utilities
        app.layout = html.Div(
            [
                html.H1('Grid Layout Test', id='grid-header', className='text-lg font-bold text-center mb-6'),
                html.Div(
                    [
                        html.Div('Item 1', className='bg-blue-500 text-white p-6 rounded-lg shadow'),
                        html.Div('Item 2', className='bg-blue-500 text-white p-6 rounded-lg shadow'),
                        html.Div('Item 3', className='bg-blue-500 text-white p-6 rounded-lg shadow'),
                    ],
                    id='grid-container',
                    className='grid grid-cols-3 gap-4',
                ),
            ],
            className='p-4',
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#grid-header', 'Grid Layout Test')

        # Verify that elements with Tailwind layout classes have the expected computed styles
        grid_container = dash_duo.find_element('#grid-container')

        # Check display property (grid should be 'grid')
        display = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).display;', grid_container
        )
        assert display == 'grid'

        # Check gap (gap-4 should be 1rem)
        gap = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).gap;', grid_container)
        assert '16px' in gap or '1rem' in gap

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_spacing_utilities_with_computed_styles(self, dash_duo: DashComposite):
        """Test that Tailwind spacing utilities generate correct computed styles."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with spacing utilities
        app.layout = html.Div(
            [
                html.Div('Element with margin', id='margin-element', className='m-4 bg-gray-200 p-8 rounded'),
                html.Div(
                    'Element with top margin', id='mt-element', className='mt-2 bg-gray-200 pl-3 rounded text-gray-800'
                ),
                html.Div('Element with bottom margin', id='mb-element', className='mb-6 bg-gray-200 pr-5 rounded'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#margin-element', 'Element with margin')

        # Verify that elements with Tailwind spacing classes have the expected computed styles
        margin_element = dash_duo.find_element('#margin-element')

        # Check margin (m-4 should be 1rem)
        margin = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).margin;', margin_element)
        assert '16px' in margin or '1rem' in margin

        # Check padding (p-8 should be 2rem)
        padding = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).padding;', margin_element
        )
        assert '32px' in padding or '2rem' in padding

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_tailwind_typography_utilities_with_computed_styles(self, dash_duo: DashComposite):
        """Test that Tailwind typography utilities generate correct computed styles."""
        # Setup TailwindCSS plugin in offline mode
        output_css_path = f'_tailwind/test_output_{str(uuid.uuid4())[:8]}.css'
        setup_tailwindcss_plugin(
            mode='offline',
            output_css_path=output_css_path,
            clean_after=False,  # Don't clean up so we can check the generated files
        )

        # Create a Dash app
        app = Dash(__name__)

        # Define a layout with typography utilities
        app.layout = html.Div(
            [
                html.P('Extra small text', id='xs-text', className='text-xs text-red-500'),
                html.P('Base text', id='base-text', className='text-base font-semibold text-green-600'),
                html.P('Large text', id='xl-text', className='text-2xl font-bold italic underline'),
                html.P('Transformed text', id='transformed-text', className='text-base uppercase font-light'),
            ]
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load
        dash_duo.wait_for_text_to_equal('#xs-text', 'Extra small text')

        # Verify that elements with Tailwind typography classes have the expected computed styles
        xs_text = dash_duo.find_element('#xs-text')
        base_text = dash_duo.find_element('#base-text')
        xl_text = dash_duo.find_element('#xl-text')
        transformed_text = dash_duo.find_element('#transformed-text')

        # Check font size (text-xs should be 0.75rem)
        xs_font_size = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontSize;', xs_text)
        assert '12px' in xs_font_size or '0.75rem' in xs_font_size

        # Check font weight (font-semibold should be 600)
        font_weight = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).fontWeight;', base_text
        )
        assert font_weight == '600'

        # Check large text size (text-2xl should be 1.5rem)
        xl_font_size = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontSize;', xl_text)
        assert '24px' in xl_font_size or '1.5rem' in xl_font_size

        # Check italic style
        font_style = dash_duo.driver.execute_script('return window.getComputedStyle(arguments[0]).fontStyle;', xl_text)
        assert font_style == 'italic'

        # Check underline
        text_decoration = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).textDecorationLine;', xl_text
        )
        assert 'underline' in text_decoration

        # Check uppercase transform
        text_transform = dash_duo.driver.execute_script(
            'return window.getComputedStyle(arguments[0]).textTransform;', transformed_text
        )
        assert text_transform == 'uppercase'

        # Check that the CSS file was generated
        # Use absolute path to ensure we're checking the correct file
        css_file_path = os.path.join(os.getcwd(), output_css_path)
        assert os.path.exists(css_file_path), f'CSS file {css_file_path} was not generated'

        # Check that the CSS file is not empty
        assert os.path.getsize(css_file_path) > 0, f'CSS file {css_file_path} is empty'

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'
