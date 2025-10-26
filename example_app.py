"""
Example Dash application using the TailwindCSS plugin.
"""

try:
    from dash import Dash, html, dcc, Input, Output, callback
    from dash_tailwindcss_plugin import setup_tailwindcss_plugin
except ImportError as e:
    print(f'Import error: {e}')
    print('Please install required dependencies: pip install -r requirements.txt')
    exit(1)

# Example 1: Initialize TailwindCSS plugin in ONLINE mode (CDN)
# setup_tailwindcss_plugin(mode="online")

# Example 2: Initialize TailwindCSS plugin in OFFLINE mode (CLI) - default
# setup_tailwindcss_plugin(mode="offline")

# Example 3: Initialize with custom theme configuration
theme_config = {
    "colors": {
        "brand": {
            "50": "#eff6ff",
            "100": "#dbeafe",
            "200": "#bfdbfe",
            "300": "#93c5fd",
            "400": "#60a5fa",
            "500": "#3b82f6",
            "600": "#2563eb",
            "700": "#1d4ed8",
            "800": "#1e40af",
            "900": "#1e3a8a"
        }
    }
}
setup_tailwindcss_plugin(mode="offline", tailwind_theme_config=theme_config)

# Example 4: Initialize with download_node option
# setup_tailwindcss_plugin(mode="offline", download_node=True, node_version="18.17.0")

# Example 5: Initialize with cleanup disabled (useful for development)
# setup_tailwindcss_plugin(mode="offline", clean_after=False)

# Example 6: Initialize with custom skip build parameters
# setup_tailwindcss_plugin(mode="offline", skip_build_if_recent=True, skip_build_time_threshold=10)

app = Dash(__name__)
app.title = 'Dash TailwindCSS Plugin Example'

app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1('Dash TailwindCSS Plugin', className='text-3xl font-bold text-white'),
                html.P('Example application showing TailwindCSS integration', className='text-blue-200'),
            ],
            className='bg-blue-600 p-6',
        ),
        # Main content
        html.Div(
            [
                # Card 1
                html.Div(
                    [
                        html.H2('Interactive Component', className='text-xl font-semibold mb-4'),
                        html.P('Enter some text below and see it styled with TailwindCSS:', className='mb-4'),
                        dcc.Input(
                            id='input-text',
                            type='text',
                            placeholder='Type something...',
                            className='border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
                        ),
                        html.Div(id='output-text', className='mt-4 p-4 bg-gray-100 rounded'),
                    ],
                    className='bg-white p-6 rounded-lg shadow-md mb-6',
                ),
                # Card 2
                html.Div(
                    [
                        html.H2('Styled Elements', className='text-xl font-semibold mb-4'),
                        html.Div(
                            [
                                html.Button(
                                    'Primary Button',
                                    className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2',
                                ),
                                html.Button(
                                    'Secondary Button',
                                    className='bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded',
                                ),
                            ],
                            className='mb-4',
                        ),
                        html.Div(
                            [
                                html.Span(
                                    'Badge',
                                    className='bg-red-100 text-red-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded',
                                ),
                                html.Span(
                                    'Pill',
                                    className='bg-green-100 text-green-800 text-sm font-medium mr-2 px-3 py-0.5 rounded-full',
                                ),
                            ],
                            className='mb-4',
                        ),
                        html.Div(
                            [
                                html.Div(
                                    'Alert Box', className='p-4 mb-4 text-sm text-blue-700 bg-blue-100 rounded-lg'
                                ),
                                html.Div(
                                    'Success Box', className='p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg'
                                ),
                            ]
                        ),
                    ],
                    className='bg-white p-6 rounded-lg shadow-md',
                ),
            ],
            className='container mx-auto p-6',
        ),
    ],
    className='min-h-screen bg-gray-100',
)


@callback(Output('output-text', 'children'), Input('input-text', 'value'))
def update_output(value):
    if value:
        return html.P(
            ['You entered: ', html.Span(value, className='font-semibold text-blue-600')], className='text-gray-700'
        )
    return html.P('Enter some text above to see it styled', className='text-gray-500 italic')


if __name__ == '__main__':
    print('Starting Dash app with TailwindCSS plugin...')
    print('Access the app at http://127.0.0.1:8050')
    app.run(debug=True)