import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
from dash_tailwindcss_plugin.plugin import _TailwindCSSPlugin


class TestOnlineThemeConfig:
    """Test cases for online mode theme configuration."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('dash_tailwindcss_plugin.plugin.hooks')
    def test_online_mode_with_theme_config(self, mock_hooks):
        """Test online mode with theme configuration."""
        # Define a custom theme configuration
        theme_config = {
            'colors': {
                'brand': {
                    '50': '#eff6ff',
                    '500': '#3b82f6',
                }
            }
        }

        # Create plugin with online mode and theme config
        plugin = _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)

        # Verify plugin properties
        assert plugin.mode == 'online'
        assert plugin.tailwind_theme_config == theme_config

        # Call setup_online_mode
        plugin.setup_online_mode()

        # Verify that hooks.index() decorator was called
        mock_hooks.index.assert_called_once()

    @patch('dash_tailwindcss_plugin.plugin.hooks')
    def test_online_mode_without_theme_config(self, mock_hooks):
        """Test online mode without theme configuration."""
        # Create plugin with online mode but no theme config
        plugin = _TailwindCSSPlugin(mode='online')

        # Verify plugin properties
        assert plugin.mode == 'online'
        assert plugin.tailwind_theme_config == {}

        # Call setup_online_mode
        plugin.setup_online_mode()

        # Verify that hooks.index() decorator was called
        mock_hooks.index.assert_called_once()

    def test_theme_config_conversion(self):
        """Test that theme config is properly converted to JavaScript."""
        # Define a custom theme configuration with nested structure
        theme_config = {
            'colors': {
                'primary': '#ff0000',
                'secondary': '#00ff00',
                'brand': {'100': '#dbeafe', '500': '#3b82f6', '900': '#1e3a8a'},
            },
            'borderRadius': {'none': '0px', 'sm': '2px', 'DEFAULT': '4px', 'md': '8px'},
        }

        # Create plugin with online mode and theme config
        _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)

        # Test the _dict_to_js_object function directly
        from dash_tailwindcss_plugin.utils import dict_to_js_object

        js_object = dict_to_js_object(theme_config)

        # Verify the structure
        assert 'colors' in js_object
        assert 'primary: "#ff0000"' in js_object
        assert 'secondary: "#00ff00"' in js_object
        assert 'brand' in js_object
        assert '100: "#dbeafe"' in js_object
        assert '500: "#3b82f6"' in js_object
        assert 'borderRadius' in js_object
        assert 'none: "0px"' in js_object
        assert 'sm: "2px"' in js_object

    def test_complex_theme_config(self):
        """Test complex theme configuration with arrays and nested objects."""
        # Define a complex theme configuration
        theme_config = {
            'colors': {
                'brand': {
                    '50': '#eff6ff',
                    '100': '#dbeafe',
                    '200': '#bfdbfe',
                    '300': '#93c5fd',
                    '400': '#60a5fa',
                    '500': '#3b82f6',
                    '600': '#2563eb',
                    '700': '#1d4ed8',
                    '800': '#1e40af',
                    '900': '#1e3a8a',
                }
            },
            'extend': {
                'spacing': {
                    '128': '32rem',
                    '144': '36rem',
                },
                'borderRadius': {
                    'xl': '1rem',
                    '2xl': '2rem',
                },
            },
        }

        # Create plugin with online mode and theme config
        _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)

        # Test the _dict_to_js_object function directly
        from dash_tailwindcss_plugin.utils import dict_to_js_object

        js_object = dict_to_js_object(theme_config)

        # Verify the structure contains all expected elements
        assert 'brand' in js_object
        assert '50: "#eff6ff"' in js_object
        assert '500: "#3b82f6"' in js_object
        assert '900: "#1e3a8a"' in js_object
        assert 'extend' in js_object
        assert 'spacing' in js_object
        assert '128: "32rem"' in js_object
        assert 'borderRadius' in js_object
        assert 'xl: "1rem"' in js_object

    def test_theme_config_with_v4(self):
        """Test theme config with Tailwind CSS v4."""
        # Define a custom theme configuration
        theme_config = {
            'colors': {
                'brand': {
                    '50': '#eff6ff',
                    '500': '#3b82f6',
                }
            }
        }

        # Create plugin with online mode, v4, and theme config
        plugin = _TailwindCSSPlugin(mode='online', tailwind_version='4', tailwind_theme_config=theme_config)

        # Verify plugin properties
        assert plugin.mode == 'online'
        assert plugin.tailwind_version == '4'
        assert plugin.tailwind_theme_config == theme_config

    def test_theme_config_with_empty_values(self):
        """Test theme config with empty values."""
        # Define a theme configuration with empty values
        theme_config = {
            'colors': {
                'primary': '',
                'secondary': None,
            },
            'spacing': {},
        }

        # Create plugin with online mode and theme config
        plugin = _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)

        # Verify plugin properties
        assert plugin.mode == 'online'
        assert plugin.tailwind_theme_config == theme_config

    def test_theme_config_with_complex_structure(self):
        """Test theme config with complex structure."""
        # Define a complex theme configuration
        theme_config = {
            'colors': {
                'brand': {
                    '50': '#eff6ff',
                    '100': '#dbeafe',
                    '200': '#bfdbfe',
                    '300': '#93c5fd',
                    '400': '#60a5fa',
                    '500': '#3b82f6',
                    '600': '#2563eb',
                    '700': '#1d4ed8',
                    '800': '#1e40af',
                    '900': '#1e3a8a',
                }
            },
            'extend': {
                'spacing': {
                    '128': '32rem',
                    '144': '36rem',
                },
                'borderRadius': {
                    'xl': '1rem',
                    '2xl': '2rem',
                },
                'keyframes': {'spin': {'from': {'transform': 'rotate(0deg)'}, 'to': {'transform': 'rotate(360deg)'}}},
                'animation': {'spin': 'spin 1s linear infinite'},
            },
        }

        # Create plugin with online mode and theme config
        plugin = _TailwindCSSPlugin(mode='online', tailwind_theme_config=theme_config)

        # Verify plugin properties
        assert plugin.mode == 'online'
        assert plugin.tailwind_theme_config == theme_config

        # Test the dict_to_js_object function directly
        from dash_tailwindcss_plugin.utils import dict_to_js_object

        js_object = dict_to_js_object(theme_config)

        # Verify the structure contains all expected elements
        assert 'brand' in js_object
        assert '500: "#3b82f6"' in js_object
        assert 'extend' in js_object
        assert 'spacing' in js_object
        assert '128: "32rem"' in js_object
        assert 'borderRadius' in js_object
        assert 'xl: "1rem"' in js_object
        assert 'keyframes' in js_object
        assert 'spin' in js_object
        assert 'from: {' in str(js_object)  # Check that the keyframes structure is present


if __name__ == '__main__':
    pytest.main([__file__])
