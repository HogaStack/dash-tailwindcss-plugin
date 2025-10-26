import os
import platform
import urllib.request
import tarfile
import zipfile
import shutil
import subprocess
import warnings
from typing import Optional, Dict, Any


def get_command_alias_by_platform(command: str) -> str:
    """
    Get the command alias for a given command on the current platform.

    Args:
        command (str): Command to get alias for
    Returns:
        str: Command alias
    """
    if platform.system().lower() == 'windows':
        return command + '.cmd'
    else:
        return command


def get_build_tailwind_cmd(
    node_path: Optional[str],
    input_css_path: str,
    output_css_path: str,
    config_js_path: str,
) -> list[str]:
    """
    Get the command to build Tailwind CSS

    Args:
        node_path (str, optional): Path to Node.js executable
        input_css_path (str): Path to the input CSS file
        output_css_path (str): Path to the output CSS file
        config_js_path (str): Path to the Tailwind config file
    Returns:
        list[str]: Command to build Tailwind CSS
    """
    if node_path:
        # When using downloaded Node.js, we need to use npx from the same directory
        node_dir = os.path.dirname(node_path)
        npx_path = os.path.join(node_dir, get_command_alias_by_platform('npx'))
        # If npx doesn't exist in the same directory, check in bin subdirectory
        if not os.path.exists(npx_path):
            npx_path = os.path.join(node_dir, 'bin', get_command_alias_by_platform('npx'))

        # If we found npx, use it with node, otherwise fallback to just npx
        if os.path.exists(npx_path):
            cmd = [
                node_path,
                npx_path,
                'tailwindcss',
                '-i',
                input_css_path,
                '-o',
                output_css_path,
                '-c',
                config_js_path,
            ]
        else:
            cmd = [
                node_path,
                get_command_alias_by_platform('npx'),
                'tailwindcss',
                '-i',
                input_css_path,
                '-o',
                output_css_path,
                '-c',
                config_js_path,
            ]
    else:
        cmd = [
            get_command_alias_by_platform('npx'),
            'tailwindcss',
            '-i',
            input_css_path,
            '-o',
            output_css_path,
            '-c',
            config_js_path,
        ]

    return cmd


def install_tailwindcss(node_path=None):
    """
    Install Tailwind CSS if not already installed

    Args:
        node_path (str, optional): Path to Node.js executable. Defaults to None
    Raises:
        Exception: If Tailwind CSS installation fails
    """
    try:
        # Check if tailwindcss is installed
        if node_path:
            # When using downloaded Node.js, we need to use npx from the same directory
            node_dir = os.path.dirname(node_path)
            npx_path = os.path.join(node_dir, get_command_alias_by_platform('npx'))
            # If npx doesn't exist in the same directory, check in bin subdirectory
            if not os.path.exists(npx_path):
                npx_path = os.path.join(node_dir, 'bin', get_command_alias_by_platform('npx'))

            # If we found npx, use it with node, otherwise fallback to just npx
            if os.path.exists(npx_path):
                cmd = [node_path, npx_path, 'tailwindcss', '--help']
            else:
                cmd = [
                    node_path,
                    get_command_alias_by_platform('npx'),
                    'tailwindcss',
                    '--help',
                ]
        else:
            cmd = [get_command_alias_by_platform('npx'), 'tailwindcss', '--help']

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Install Tailwind CSS
            # Use npm init -y first to ensure package.json exists
            if node_path:
                # When using downloaded Node.js, we need to use npm from the same directory
                node_dir = os.path.dirname(node_path)
                npm_path = os.path.join(node_dir, get_command_alias_by_platform('npm'))
                # If npm doesn't exist in the same directory, check in bin subdirectory
                if not os.path.exists(npm_path):
                    npm_path = os.path.join(node_dir, 'bin', get_command_alias_by_platform('npm'))

                # If we found npm, use it with node, otherwise fallback to just npm
                if os.path.exists(npm_path):
                    npm_cmd = [node_path, npm_path, 'init', '-y']
                else:
                    npm_cmd = [
                        node_path,
                        get_command_alias_by_platform('npm'),
                        'init',
                        '-y',
                    ]
            else:
                npm_cmd = [get_command_alias_by_platform('npm'), 'init', '-y']
            subprocess.run(npm_cmd, capture_output=True, text=True)

            # Then install tailwindcss with a specific version that works
            if node_path:
                # When using downloaded Node.js, we need to use npm from the same directory
                node_dir = os.path.dirname(node_path)
                npm_path = os.path.join(node_dir, get_command_alias_by_platform('npm'))
                # If npm doesn't exist in the same directory, check in bin subdirectory
                if not os.path.exists(npm_path):
                    npm_path = os.path.join(node_dir, 'bin', get_command_alias_by_platform('npm'))

                # If we found npm, use it with node, otherwise fallback to just npm
                if os.path.exists(npm_path):
                    install_cmd = [
                        node_path,
                        npm_path,
                        'install',
                        '-D',
                        'tailwindcss@3',
                    ]
                else:
                    install_cmd = [
                        node_path,
                        get_command_alias_by_platform('npm'),
                        'install',
                        '-D',
                        'tailwindcss@3',
                    ]
            else:
                install_cmd = [
                    get_command_alias_by_platform('npm'),
                    'install',
                    '-D',
                    'tailwindcss@3',
                ]
            subprocess.run(install_cmd, capture_output=True, text=True)
    except Exception as e:
        warnings.warn(f'Could not install Tailwind CSS: {e}')


def _dict_to_js_object(d: Dict[Any, Any], indent: int = 0) -> str:
    """
    Convert a Python dictionary to a JavaScript object string representation.

    Args:
        d (Dict[Any, Any]): Dictionary to convert
        indent (int): Current indentation level

    Returns:
        str: JavaScript object string representation
    """
    if not d:
        return '{}'

    indent_str = '  ' * indent
    next_indent_str = '  ' * (indent + 1)

    items = []
    for key, value in d.items():
        if isinstance(value, dict):
            items.append(f'{next_indent_str}{key}: {_dict_to_js_object(value, indent + 1)}')
        elif isinstance(value, str):
            items.append(f'{next_indent_str}{key}: "{value}"')
        elif isinstance(value, bool):
            items.append(f'{next_indent_str}{key}: {"true" if value else "false"}')
        elif isinstance(value, (int, float)):
            items.append(f'{next_indent_str}{key}: {value}')
        elif isinstance(value, list):
            # Convert list to JavaScript array
            array_items = []
            for item in value:
                if isinstance(item, dict):
                    array_items.append(_dict_to_js_object(item, indent + 2))
                elif isinstance(item, str):
                    array_items.append(f'"{item}"')
                elif isinstance(item, bool):
                    array_items.append('true' if item else 'false')
                elif isinstance(item, (int, float)):
                    array_items.append(str(item))
                else:
                    array_items.append(str(item))
            items.append(f'{next_indent_str}{key}: [{", ".join(array_items)}]')
        else:
            items.append(f'{next_indent_str}{key}: {value}')

    return '{\n' + ',\n'.join(items) + f'\n{indent_str}}}'


def create_default_tailwindcss_config(
    content_path: list,
    config_js_path: str,
    theme_config: Optional[Dict[Any, Any]] = None,
):
    """
    Create a default Tailwind config file

    Args:
        content_path (list): Glob patterns for files to scan for Tailwind classes
        config_js_path (str): Path to the Tailwind config file
        theme_config (Optional[Dict[Any, Any]], optional): Custom theme configuration for Tailwind CSS

    Returns:
        None
    """
    # Convert list of content paths to JSON array format
    content_paths_str = ', '.join([f'"{path}"' for path in content_path])

    # Handle theme configuration
    if theme_config:
        theme_str = _dict_to_js_object(theme_config, 2)
        # Ensure theme_str is properly indented within the config
        theme_lines = theme_str.split('\n')
        indented_theme_lines = ['    ' + line if line.strip() else line for line in theme_lines]
        theme_str = '\n'.join(indented_theme_lines)
    else:
        theme_str = '{}'

    config_content = f"""module.exports = {{
    content: [{content_paths_str}],
    theme: {{
        extend: {theme_str},
    }},
    plugins: [],
}}
"""

    # Ensure config directory exists
    config_dir = os.path.dirname(config_js_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)

    with open(config_js_path, 'w') as f:
        f.write(config_content)


def create_default_input_tailwindcss(input_css_path: str):
    """
    Create a default input CSS file

    Args:
        input_css_path (str): Path to input CSS file

    Returns:
        None
    """
    # Ensure assets directory exists
    assets_dir = os.path.dirname(input_css_path)
    if assets_dir and not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    input_css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;
"""
    with open(input_css_path, 'w') as f:
        f.write(input_css_content)


def download_nodejs(node_version: str, is_cli: bool = False) -> str:
    """
    Download Node.js for the current platform

    Args:
        node_version (str): Node.js version to download
        is_cli (bool): Whether this is being called from CLI (affects messages)

    Returns:
        str: Path to downloaded Node.js executable
    """
    # Determine platform
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Define download URLs for different platforms
    if system == 'darwin':  # macOS
        if machine == 'arm64' or machine == 'aarch64':
            node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-darwin-arm64.tar.gz'
            node_dir = f'node-v{node_version}-darwin-arm64'
        else:
            node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-darwin-x64.tar.gz'
            node_dir = f'node-v{node_version}-darwin-x64'
    elif system == 'linux':
        if machine == 'aarch64':
            node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-linux-arm64.tar.xz'
            node_dir = f'node-v{node_version}-linux-arm64'
        else:
            node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-linux-x64.tar.xz'
            node_dir = f'node-v{node_version}-linux-x64'
    elif system == 'windows':
        node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-win-x64.zip'
        node_dir = f'node-v{node_version}-win-x64'
    else:
        raise RuntimeError(f'Unsupported platform: {system}')

    # Create directory for downloaded Node.js within the package directory
    # Use the package directory instead of current working directory
    # Get the directory of this utils.py file
    package_dir = os.path.dirname(os.path.abspath(__file__))
    node_dir_path = os.path.join(package_dir, '.nodejs_cache')
    if not os.path.exists(node_dir_path):
        os.makedirs(node_dir_path)

    # Check if Node.js is already downloaded
    if system == 'windows':
        node_executable = os.path.join(node_dir_path, node_dir, 'node.exe')
    else:
        node_executable = os.path.join(node_dir_path, node_dir, 'bin', 'node')

    # If Node.js already exists, return the path without downloading
    if os.path.exists(node_executable):
        print(f'Using cached Node.js from {node_executable}')
        return node_executable

    # Download Node.js
    node_archive = os.path.join(node_dir_path, os.path.basename(node_url))
    print('Node.js not found in PATH. Downloading Node.js...')
    if is_cli:
        print(f'Downloading Node.js from {node_url}...')
    urllib.request.urlretrieve(node_url, node_archive)

    # Extract Node.js
    if is_cli:
        print('Extracting Node.js...')
    if node_archive.endswith('.tar.gz'):
        with tarfile.open(node_archive, 'r:gz') as tar:
            tar.extractall(node_dir_path)
    elif node_archive.endswith('.tar.xz'):
        with tarfile.open(node_archive, 'r:xz') as tar:
            tar.extractall(node_dir_path)
    elif node_archive.endswith('.zip'):
        with zipfile.ZipFile(node_archive, 'r') as zip_ref:
            zip_ref.extractall(node_dir_path)

    # Remove archive
    os.remove(node_archive)

    # Make executable if not on Windows
    if system != 'windows':
        os.chmod(node_executable, 0o755)

    if is_cli:
        print(f'Node.js downloaded and extracted to {node_executable}')
    return node_executable


def clean_generated_files(input_css_path: str, config_js_path: str, is_cli: bool = False) -> None:
    """
    Clean up generated files to keep directory clean

    Args:
        input_css_path (str): Path to input CSS file
        config_js_path (str): Path to the Tailwind config file
        is_cli (bool): Whether this is being called from CLI (affects messages)

    Returns:
        None
    """
    files_to_remove = [
        config_js_path,
        'package.json',
        'package-lock.json',
        input_css_path,
    ]

    directories_to_remove = ['node_modules']

    if is_cli:
        print('Cleaning up generated files...')

    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                if is_cli:
                    print(f'Removed {file_path}')
            except Exception as e:
                if is_cli:
                    print(f'Warning: Could not remove {file_path}: {e}')
                else:
                    warnings.warn(f'Could not remove {file_path}: {e}')

    # Remove directories
    for dir_path in directories_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                if is_cli:
                    print(f'Removed {dir_path}')
            except Exception as e:
                if is_cli:
                    print(f'Warning: Could not remove {dir_path}: {e}')
                else:
                    warnings.warn(f'Could not remove {dir_path}: {e}')

    if is_cli:
        print('Cleanup completed.')


def check_nodejs_available() -> tuple[bool, str]:
    """
    Check if Node.js is available in PATH

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if Node.js is available, False otherwise
            - str: The version of Node.js if available, empty string otherwise
    """
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except FileNotFoundError:
        pass

    return False, ''


def check_or_download_nodejs(download_node: bool, node_version: str, is_cli: bool = False) -> Optional[str]:
    """
    Check if Node.js is available or download it if requested

    Args:
        download_node (bool): Whether to download Node.js if not found
        node_version (str): Node.js version to download if download_node is True
        is_cli (bool): Whether this is being called from CLI (affects error messages)

    Returns:
        str: Path to Node.js executable or None if using system Node.js
    """
    # First check if Node.js is available in PATH
    is_available, version = check_nodejs_available()
    if is_available:
        if is_cli:
            print(f'Using System Default Node.js {version}')
        return None  # Use system Node.js

    # If not found and download is not requested, raise error
    if not download_node:
        if is_cli:
            raise RuntimeError(
                'Node.js is required but not found in PATH. '
                'Install Node.js or use --download-node to automatically download it.'
            )
        else:
            raise RuntimeError(
                'Node.js is required for offline mode but not found. '
                'Install Node.js or use download_node=True to automatically download it.'
            )

    # Download Node.js using the shared utility function
    return download_nodejs(node_version, is_cli)
