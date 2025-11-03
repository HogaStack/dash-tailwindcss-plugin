import os
import platform
import shutil
import subprocess
import tarfile
from typing_extensions import Self
import urllib.request
import logging
import zipfile
from typing import Any, Dict, List, Literal, Optional


# Custom log formatter to add colors for different log levels
class ColoredFormatter(logging.Formatter):
    """Custom log formatter to add colors for different log levels and emoji"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',  # cyan
        'INFO': '\033[32m',  # green
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',  # red
        'CRITICAL': '\033[35m',  # purple
        'RESET': '\033[0m',  # reset
    }

    def format(self, record):
        # Obtain the color corresponding to the log level
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']

        # Add color to log level
        record.levelname = f'{log_color}{record.levelname}{reset_color}'

        # Call the format method of the parent class
        return super().format(record)


# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console processor
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)


def dict_to_js_object(d: Dict[Any, Any], indent: int = 0) -> str:
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
            items.append(f'{next_indent_str}{key}: {dict_to_js_object(value, indent + 1)}')
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
                    array_items.append(dict_to_js_object(item, indent + 2))
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


class NodeManager:
    def __init__(self, download_node: bool, node_version: str, is_cli: bool = False):
        """
        Node.js manager class

        Args:
            download_node (bool): Whether to download Node.js if not found
            node_version (str): Node.js version to download if download_node is True
            is_cli (bool): Whether this is being called from CLI (affects error messages)
        """
        self.download_node = download_node
        self.node_version = node_version
        self.is_cli = is_cli
        self.node_path = self._node_path()
        self.node_env = self._node_env()
        self.npm_path = self._npm_path()
        self.npx_path = self._npx_path()

    def check_nodejs_available(self) -> tuple[bool, str]:
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

    def download_nodejs(self) -> str:
        """
        Download Node.js for the current platform

        Returns:
            str: Path to downloaded Node.js executable
        """
        # Determine platform
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Define download URLs for different platforms
        if system == 'darwin':  # macOS
            if machine == 'arm64' or machine == 'aarch64':
                node_url = f'https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-darwin-arm64.tar.gz'
                node_dir = f'node-v{self.node_version}-darwin-arm64'
            else:
                node_url = f'https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-darwin-x64.tar.gz'
                node_dir = f'node-v{self.node_version}-darwin-x64'
        elif system == 'linux':
            if machine == 'aarch64':
                node_url = f'https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-linux-arm64.tar.xz'
                node_dir = f'node-v{self.node_version}-linux-arm64'
            else:
                node_url = f'https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-linux-x64.tar.xz'
                node_dir = f'node-v{self.node_version}-linux-x64'
        elif system == 'windows':
            node_url = f'https://nodejs.org/dist/v{self.node_version}/node-v{self.node_version}-win-x64.zip'
            node_dir = f'node-v{self.node_version}-win-x64'
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
            logger.info(f'📦 Using cached Node.js from {node_executable}')
            return node_executable

        # Download Node.js
        node_archive = os.path.join(node_dir_path, os.path.basename(node_url))
        logger.info('🌐 Node.js not found in PATH. Downloading Node.js...')
        if self.is_cli:
            logger.info(f'📥 Downloading Node.js from {node_url}...')
        urllib.request.urlretrieve(node_url, node_archive)

        # Extract Node.js
        if self.is_cli:
            logger.info('🔧 Extracting Node.js...')
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

        logger.info(f'✅ Node.js downloaded and extracted to {node_executable}')
        return node_executable

    def check_or_download_nodejs(self) -> Optional[str]:
        """
        Check if Node.js is available or download it if requested

        Returns:
            Optional[str]: Path to Node.js executable or None if using system Node.js
        """
        # First check if Node.js is available in PATH
        is_available, version = self.check_nodejs_available()
        if is_available:
            logger.info(f'💻 Using System Default Node.js {version}')

            return None  # Use system Node.js

        # If not found and download is not requested, raise error
        if not self.download_node:
            if self.is_cli:
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
        return self.download_nodejs()

    def get_command_alias_by_platform(self, command: str) -> str:
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

    def _node_path(self) -> Optional[str]:
        """
        Get the path to the Node.js executable

        Returns:
            Optional[str]: Path to Node.js executable or None if using system Node.js
        """
        node_path = self.check_or_download_nodejs()

        return node_path

    def _node_env(self) -> Optional[Dict[str, str]]:
        """
        Get the environment variables for the Node.js executable

        Returns:
            Optional[Dict[str, str]]: Environment variables for Node.js executable or None if using system Node.js
        """
        env = None
        if self.node_path:
            node_dir = os.path.dirname(self.node_path)
            env = os.environ.copy()
            env['PATH'] = node_dir + os.pathsep + env.get('PATH', '')

        return env

    def _npm_path(self) -> str:
        """
        Get the path to the npm executable

        Returns:
            str: Path to npm executable
        """
        if self.node_path:
            # When using downloaded Node.js, we need to use npm from the same directory
            node_dir = os.path.dirname(self.node_path)
            npm_path = os.path.join(node_dir, self.get_command_alias_by_platform('npm'))
            # If npm doesn't exist in the same directory, check in bin subdirectory
            if not os.path.exists(npm_path):
                npm_path = os.path.join(node_dir, 'bin', self.get_command_alias_by_platform('npm'))

        else:
            npm_path = self.get_command_alias_by_platform('npm')

        return npm_path

    def _npx_path(self) -> str:
        """
        Get the path to the npx executable

        Returns:
            str: Path to npx executable
        """
        if self.node_path:
            # When using downloaded Node.js, we need to use npx from the same directory
            node_dir = os.path.dirname(self.node_path)
            npx_path = os.path.join(node_dir, self.get_command_alias_by_platform('npx'))
            # If npx doesn't exist in the same directory, check in bin subdirectory
            if not os.path.exists(npx_path):
                npx_path = os.path.join(node_dir, 'bin', self.get_command_alias_by_platform('npx'))

        else:
            npx_path = self.get_command_alias_by_platform('npx')

        return npx_path


class TailwindCommand:
    def __init__(
        self,
        node_path: Optional[str],
        node_env: Optional[Dict[str, str]],
        npm_path: str,
        npx_path: str,
        tailwind_version: Literal['3', '4'],
        content_path: List[str],
        plugin_tmp_dir: str,
        input_css_path: str,
        output_css_path: str,
        config_js_path: str,
        is_cli: bool,
        theme_config: Optional[Dict[Any, Any]] = None,
    ):
        """
        Initialize the TailwindCommand class

        Args:
            node_path (Optional[str]): Path to Node.js executable
            node_env (Optional[Dict[str, str]]): Environment variables for Node.js executable
            npm_path (str): Path to npm executable
            npx_path (str): Path to npx executable
            tailwind_version (Literal['3', '4']): Version of Tailwind CSS
            content_path (List[str]): List of paths to content files
            input_css_path (str): Path to input CSS file
            output_css_path (str): Path to output CSS file
            config_js_path (str): Path to Tailwind config file
            is_cli (bool): Whether the command is being run from the CLI
            theme_config (Optional[Dict[Any, Any]]): Custom theme configuration for Tailwind CSS
        """
        self.node_path = node_path
        self.node_env = node_env
        self.npm_path = npm_path
        self.npx_path = npx_path
        self.tailwind_version = tailwind_version
        self.content_path = content_path
        self.input_css_path = input_css_path
        self.output_css_path = output_css_path
        self.config_js_path = config_js_path
        self.is_cli = is_cli
        self.theme_config = theme_config or {}
        # Ensure the tailwind_plugin directory exists
        self.plugin_tmp_dir = plugin_tmp_dir
        if not os.path.exists(self.plugin_tmp_dir):
            os.makedirs(self.plugin_tmp_dir)

    def create_default_input_tailwindcss(self):
        """
        Create a default input CSS file

        Returns:
            None
        """
        # Ensure assets directory exists
        assets_dir = os.path.dirname(self.input_css_path)
        if assets_dir and not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        if self.tailwind_version == '3':
            input_css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;
"""
        else:
            input_css_content = """@import "tailwindcss";"""
        with open(self.input_css_path, 'w') as f:
            f.write(input_css_content)

    def create_default_tailwindcss_config(self):
        """
        Create a default Tailwind config file

        Returns:
            None
        """
        # Convert list of content paths to JSON array format
        content_paths_str = ', '.join([f'"{path}"' for path in self.content_path])

        # Handle theme configuration
        if self.theme_config:
            theme_str = dict_to_js_object(self.theme_config, 2)
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
        config_dir = os.path.dirname(self.config_js_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

        with open(self.config_js_path, 'w') as f:
            f.write(config_content)

    @property
    def _tailwind_cli(self) -> Literal['tailwindcss', '@tailwindcss/cli']:
        """
        Get the name of the Tailwind CSS command to use

        Returns:
            Literal['tailwindcss', '@tailwindcss/cli']: Name of the Tailwind CSS command to use
        """
        if self.tailwind_version == '3':
            return 'tailwindcss'
        else:
            return '@tailwindcss/cli'

    @property
    def _tailwind_package(self) -> List[str]:
        """
        Get the name of the Tailwind CSS package to use

        Returns:
            List[str]: Name of the Tailwind CSS package to use
        """
        if self.tailwind_version == '3':
            return ['tailwindcss@3']
        else:
            return ['tailwindcss', '@tailwindcss/cli']

    def _check_npm_init(self) -> bool:
        """
        Check if npm init has been run

        Returns:
            bool: True if npm init has been run, False otherwise
        """
        return os.path.exists(f'{self.plugin_tmp_dir}/package.json')

    def _check_tailwindcss(self) -> bool:
        """
        Check if Tailwind CSS is installed

        Returns:
            bool: True if Tailwind CSS is installed, False otherwise
        """
        check_cmd = [self.npx_path, f'{self._tailwind_cli} --help']

        result = subprocess.run(check_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env)
        return result.returncode == 0

    def init(self) -> Self:
        """
        Initialize Tailwind CSS

        Returns:
            Self: The TailwindCommand instance
        """
        logger.info('🚀 Start initializing Tailwind CSS...')
        try:
            # Create default config if it doesn't exist
            if self.is_cli:
                logger.info('📄 Creating input CSS file...')

            if not os.path.exists(self.input_css_path):
                if self.is_cli:
                    logger.info(
                        f'🔍 Input CSS file {self.input_css_path} not found. Creating default input CSS file...'
                    )

                self.create_default_input_tailwindcss()

                if self.is_cli:
                    logger.info(f'💾 Default input CSS file created at: {self.input_css_path}')

            # Create default input Tailwind CSS file if it doesn't exist
            if self.is_cli:
                logger.info('⚙️ Creating Tailwind config...')

            if not os.path.exists(self.config_js_path):
                if self.is_cli:
                    logger.info(f'🔍 Config file {self.config_js_path} not found. Creating default config file...')

                self.create_default_tailwindcss_config()

                if self.is_cli:
                    logger.info(f'💾 Default config file created at: {self.config_js_path}')

            if not self._check_npm_init():
                init_cmd = [self.npm_path, 'init', '-y']
                result = subprocess.run(
                    init_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Tailwind CSS initialized successfully!')

        except Exception as e:
            logger.error(f'❌ Error initializing Tailwind CSS: {e}')
            raise e

        return self

    def install(self) -> Self:
        """
        Install Tailwind CSS

        Returns:
            Self: The TailwindCommand instance
        """
        logger.info('📥 Start installing Tailwind CSS...')
        try:
            if not self._check_tailwindcss():
                install_cmd = [
                    self.npm_path,
                    'install',
                    '-D',
                    *self._tailwind_package,
                ]
                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Tailwind CSS installed successfully!')

        except Exception as e:
            logger.error(f'❌ Error installing Tailwind CSS: {e}')
            raise e

        return self

    def build(self) -> Self:
        """
        Build the Tailwind CSS

        Returns:
            Self: The TailwindCommand instance
        """
        logger.info(f'🔨 Building Tailwind CSS from {self.input_css_path} to {self.output_css_path}...')
        try:
            build_cmd: list[str] = [
                self.npx_path,
                f'{self.plugin_tmp_dir}/node_modules/{self._tailwind_cli}',
                '-i',
                self.input_css_path,
                '-o',
                self.output_css_path,
                '-c',
                self.config_js_path,
            ]

            result = subprocess.run(build_cmd, capture_output=True, text=True, env=self.node_env)

            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            logger.info('✅ Build completed successfully!')
            logger.info(f'🎨 Tailwind CSS built successfully to {self.output_css_path}')

        except Exception as e:
            logger.error(f'❌ Error building Tailwind CSS: {e}')
            raise e

        return self

    def watch(self) -> Self:
        """
        Watch for changes in the input CSS file and rebuild Tailwind CSS

        Returns:
            Self: The TailwindCommand instance
        """
        logger.info(f'👀 Watching for changes in {self.input_css_path}...')
        try:
            watch_cmd = [
                self.npx_path,
                f'{self.plugin_tmp_dir}/node_modules/{self._tailwind_cli}',
                '-i',
                self.input_css_path,
                '-o',
                self.output_css_path,
                '-c',
                self.config_js_path,
                '--watch',
            ]
            subprocess.run(watch_cmd, env=self.node_env)

        except KeyboardInterrupt:
            logger.info('👋 Watch stopped.')

        except Exception as e:
            logger.error(f'❌ Error watching for changes: {e}')
            raise e

        return self

    def clean(self) -> Self:
        """
        Clean up generated files to keep directory clean

        Returns:
            Self: The TailwindCommand instance
        """
        logger.info('🧹 Cleaning up generated files...')
        try:
            files_to_remove = [
                self.config_js_path,
                f'{self.plugin_tmp_dir}/package.json',
                f'{self.plugin_tmp_dir}/package-lock.json',
                self.input_css_path,
            ]

            directories_to_remove = [f'{self.plugin_tmp_dir}/node_modules']

            # Remove files
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        if self.is_cli:
                            logger.info(f'🗑️ Removed {file_path}')
                    except Exception as e:
                        logger.warning(f'⚠️ Warning: Could not remove {file_path}: {e}')

            # Remove directories
            for dir_path in directories_to_remove:
                if os.path.exists(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                        if self.is_cli:
                            logger.info(f'🗑️ Removed {dir_path}')
                    except Exception as e:
                        logger.warning(f'⚠️ Warning: Could not remove {dir_path}: {e}')

            logger.info('✅ Cleanup completed.')

        except Exception as e:
            logger.error(f'❌ Error cleaning up: {e}')
            raise e

        return self
