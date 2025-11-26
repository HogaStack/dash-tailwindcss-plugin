# Dash TailwindCSS Plugin

一个用于将 TailwindCSS 集成到 Plotly Dash 应用程序中的插件，使用 Dash 3.x hooks。支持 Tailwind CSS v3 和 v4。

[![Tests](https://github.com/HogaStack/dash-tailwindcss-plugin/workflows/Tests/badge.svg)](https://github.com/HogaStack/dash-tailwindcss-plugin/actions)
[![Coverage](https://codecov.io/gh/HogaStack/dash-tailwindcss-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/HogaStack/dash-tailwindcss-plugin)
[![Python Version](https://img.shields.io/pypi/pyversions/dash-tailwindcss-plugin)](https://pypi.org/project/dash-tailwindcss-plugin/)
[![PyPI](https://img.shields.io/pypi/v/dash-tailwindcss-plugin)](https://pypi.org/project/dash-tailwindcss-plugin/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub](https://shields.io/badge/license-MIT-informational)](https://github.com/HogaStack/dash-tailwindcss-plugin/blob/main/LICENSE)

简体中文 | [English](./README.md)

## 功能特性

1. **在线模式**：使用 Tailwind CSS CDN 快速设置
2. **离线模式**：使用 Tailwind CLI 构建优化的 CSS
3. **自动构建**：在应用启动时自动构建 Tailwind CSS
4. **灵活配置**：可自定义输入/输出路径和配置文件
5. **自动清理**：自动删除生成的文件以保持目录整洁
6. **Node.js 管理**：自动下载和使用特定版本的 Node.js
7. **基于类的架构**：干净的面向对象设计，便于维护
8. **全面测试**：完整的测试覆盖，包括单元测试、集成测试和 Dash 特定测试
9. **自定义主题配置**：通过自定义颜色、间距等扩展 Tailwind 的默认主题
10. **可配置清理**：控制构建后是否清理中间文件
11. **Tailwind CSS v3 & v4 支持**：支持 Tailwind CSS 版本 3 和 4

## 安装

```bash
pip install dash-tailwindcss-plugin
```

或者用于开发：

```bash
pip install -e .
```

用于开发和所有依赖（包括测试依赖）：

```bash
pip install -e .[dev]
```

## 使用方法

### 在线模式 (CDN)

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 使用 CDN 模式初始化（默认为 Tailwind CSS v3）
setup_tailwindcss_plugin(mode="online")

# 或指定 Tailwind CSS 版本（v3 或 v4）
# setup_tailwindcss_plugin(mode="online", tailwind_version="4")

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Hello, TailwindCSS!", className="text-3xl font-bold text-blue-600"),
    html.P("这是使用 Tailwind CSS CDN 样式化的。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### 离线模式 (CLI)

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 使用离线模式初始化（默认）
setup_tailwindcss_plugin(
    mode="offline",
    tailwind_version="3",  # 指定 Tailwind CSS 版本（v3 或 v4）
    content_path=["**/*.py"],  # 要扫描 Tailwind 类的文件
    plugin_tmp_dir="_tailwind",  # 插件文件的临时目录
    output_css_path="_tailwind/tailwind.css",  # 输出 CSS 文件
    config_js_path="_tailwind/tailwind.config.js",  # Tailwind 配置文件
    download_node=True,  # 如果未找到则下载 Node.js
    node_version="18.17.0"  # 指定要下载的 Node.js 版本
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Hello, TailwindCSS!", className="text-3xl font-bold text-blue-600"),
    html.P("这是使用本地构建的 Tailwind CSS 样式化的。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### 自定义插件临时目录

您可以为插件文件指定自定义临时目录：

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 使用自定义插件临时目录初始化
setup_tailwindcss_plugin(
    mode="offline",
    plugin_tmp_dir="_my_tailwind",  # 自定义临时目录
    input_css_path="_my_tailwind/input.css",
    output_css_path="_my_tailwind/output.css",
    config_js_path="_my_tailwind/config.js"
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("自定义目录", className="text-3xl font-bold text-green-600"),
    html.P("这使用了自定义临时目录。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### 控制构建跳过行为

您可以控制是否在最近生成 CSS 时跳过重新构建：

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 使用自定义跳过构建参数初始化
setup_tailwindcss_plugin(
    mode="offline",
    skip_build_if_recent=True,  # 如果最近生成了 CSS 则跳过构建
    skip_build_time_threshold=10  # 如果在 10 秒内生成则认为是最近的
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("智能重建", className="text-3xl font-bold text-purple-600"),
    html.P("这使用了智能重建行为。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### 自定义主题配置

您可以通过提供自定义主题配置来扩展 Tailwind 的默认主题：

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 定义自定义主题配置
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
    },
    "borderRadius": {
        "none": "0px",
        "sm": "0.125rem",
        "DEFAULT": "0.25rem",
        "md": "0.375rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        "full": "9999px"
    }
}

# 使用自定义主题配置初始化
setup_tailwindcss_plugin(
    mode="offline",
    tailwind_theme_config=theme_config
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("自定义主题", className="text-3xl font-bold text-brand-500"),
    html.P("这使用了自定义品牌颜色。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

### 控制清理行为

默认情况下，插件在构建后会清理中间文件。您可以禁用此行为：

```python
from dash import Dash, html
from dash_tailwindcss_plugin import setup_tailwindcss_plugin

# 初始化并禁用清理
setup_tailwindcss_plugin(
    mode="offline",
    clean_after=False  # 构建后保留中间文件
)

app = Dash(__name__)
app.layout = html.Div([
    html.H1("不清理", className="text-3xl font-bold text-blue-600"),
    html.P("构建后将保留中间文件。", className="text-gray-700 mt-4")
])

if __name__ == "__main__":
    app.run(debug=True)
```

## 项目结构

```bash
dash-tailwindcss-plugin/
├── .github/
│   └── workflows/
│       └── test.yml         # GitHub Actions 测试工作流
├── dash_tailwindcss_plugin/
│   ├── __init__.py          # 导出主插件函数
│   ├── plugin.py            # 主插件实现，包含 _TailwindCSSPlugin 类
│   ├── cli.py               # 命令行界面，包含 _TailwindCLI 类
│   └── utils.py             # Node.js 管理、文件操作等实用函数
├── tests/
│   ├── README.md            # 英文测试文档
│   ├── README-zh_CN.md      # 中文测试文档
│   ├── conftest.py          # Pytest 配置夹具
│   ├── test_cli.py          # CLI 接口的单元测试
│   ├── test_dash_integration.py  # Dash 端到端集成测试
│   ├── test_plugin.py       # 插件核心功能的单元测试
│   └── test_utils.py        # 实用函数的单元测试
├── example_app.py           # 示例 Dash 应用
├── requirements-dev.txt     # 开发和测试依赖
├── pyproject.toml           # 构建配置
├── pytest.ini               # Pytest 配置
├── ruff.toml                # Ruff 配置（代码检查）
├── README.md                # 英文 README 文件
└── README-zh_CN.md          # 中文 README 文件
```

## 要求

- Python 3.8+
- Dash 3.0+
- Node.js 12+（用于离线模式，如果使用 download_node 功能则可选）

## 工作原理

### 在线模式

- 使用 `hooks.index()` 将 Tailwind CSS CDN 脚本添加到应用的 HTML 头部
- 无需构建过程
- 更大的 CSS 文件（包含所有 Tailwind 类）
- 支持 Tailwind CSS v3（默认 CDN: <https://cdn.tailwindcss.com>）和 v4（默认 CDN: <https://registry.npmmirror.com/@tailwindcss/browser/4/files/dist/index.global.js>）

### 离线模式

- 使用 `hooks.setup(priority=3)` 在应用启动时构建 Tailwind CSS
- 使用 `hooks.route(name=built_tailwindcss_link, methods=('GET',), priority=2)` 提供生成的 CSS 文件
- 使用 `hooks.index(priority=1)` 将 CSS 链接注入 HTML 头部
- 如果不存在则自动安装 Tailwind CLI
- 扫描指定文件中的 Tailwind 类以创建优化的 CSS
- 如果请求且 PATH 中未找到则自动下载 Node.js
- 构建后自动清理临时文件（除非禁用）
- **智能重建**：如果 CSS 文件在最近 5 秒内生成则跳过重建
- 支持 Tailwind CSS v3 和 v4 以及相应的 CLI 包

## 配置

插件接受以下参数：

- `mode`: "online" 或 "offline"（默认："offline"）
- `tailwind_version`: "3" 或 "4"（默认："3"）
- `content_path`: 用于扫描的文件的 Glob 模式（默认：["**/*.py"]）
- `plugin_tmp_dir`: 插件文件的临时目录（默认："_tailwind"）
- `input_css_path`: 输入 CSS 文件的路径（默认："_tailwind/tailwind_input.css"）
- `output_css_path`: 输出 CSS 文件的路径（默认："_tailwind/tailwind.css"）
- `config_js_path`: Tailwind 配置文件的路径（默认："_tailwind/tailwind.config.js"）
- `cdn_url`: 在线模式的 CDN URL（默认：<https://cdn.tailwindcss.com>）
- `download_node`: 如果未找到是否下载 Node.js（默认：False）
- `node_version`: 如果 download_node 为 True 则下载的 Node.js 版本（默认："18.17.0"）
- `tailwind_theme_config`: Tailwind CSS 的自定义主题配置字典（默认：None）
- `clean_after`: 构建后是否清理生成的文件（默认：True）
- `skip_build_if_recent`: 如果最近生成了 CSS 文件是否跳过构建（默认：True）
- `skip_build_time_threshold`: 将 CSS 文件视为最近的时间阈值（秒）（默认：5）

## 开发

1. 克隆仓库
2. 安装开发依赖：`pip install -r requirements-dev.txt`
3. 以开发模式安装：`pip install -e .`
4. 运行示例：`python example_app.py`

## 运行测试

```bash
# 安装开发依赖（包含测试依赖）
pip install -r requirements-dev.txt

# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_plugin.py
python -m pytest tests/test_utils.py
python -m pytest tests/test_cli.py
python -m pytest tests/test_dash_integration.py

# 运行带详细输出的测试
python -m pytest tests/ -v

# 运行带覆盖率报告的测试
python -m pytest tests/ --cov=dash_tailwindcss_plugin --cov-report=html
```

更多信息请参见 [tests/README-zh_CN.md](tests/README-zh_CN.md)。

## 构建包

```bash
python -m build
```

这将在 `dist/` 目录中创建源分发和 wheel 文件。

## CLI 工具

该包包含一个命令行界面：

```bash
dash-tailwindcss-plugin init              # 初始化 Tailwind 配置
dash-tailwindcss-plugin build             # 手动构建 CSS
dash-tailwindcss-plugin watch             # 监视更改
dash-tailwindcss-plugin clean             # 清理生成的文件
```

### CLI 选项

所有命令都支持以下选项：

- `--tailwind-version VERSION`: 要使用的 Tailwind CSS 版本（3 或 4）（默认："3"）
- `--content-path INPUT`: 用于扫描 Tailwind 类的文件的 Glob 模式。可以多次指定。（默认：["**/*.py"]）
- `--plugin-tmp-dir PATH`: 插件文件的临时目录（默认："./_tailwind"）
- `--input-css-path PATH`: 输入 CSS 文件的路径（默认："./_tailwind/tailwind_input.css"）
- `--output-css-path OUTPUT`: 输出 CSS 文件的路径（默认："./_tailwind/tailwind.css"）
- `--config-js-path CONFIG`: Tailwind 配置文件的路径（默认："./_tailwind/tailwind.config.js"）
- `--tailwind-theme-config JSON`: Tailwind CSS 的自定义主题配置的 JSON 字符串
- `--download-node`: 如果 PATH 中未找到则下载 Node.js
- `--node-version VERSION`: 要下载的 Node.js 版本（如果使用 --download-node）
- `--clean-after`: 构建后清理生成的文件（仅适用于 build 命令）

示例：

```bash
dash-tailwindcss-plugin build --download-node --node-version 18.17.0
```

带多个内容路径的示例：

```bash
dash-tailwindcss-plugin build --content-path "**/*.py" --content-path "**/*.js"
```

带自定义主题配置的示例：

```bash
dash-tailwindcss-plugin build --tailwind-theme-config "{\"colors\":{\"brand\":{\"500\":\"#3b82f6\"}}}"
```

带 Tailwind CSS v4 的示例：

```bash
dash-tailwindcss-plugin build --tailwind-version 4
```

带自定义插件临时目录的示例：

```bash
dash-tailwindcss-plugin build --plugin-tmp-dir "./my-tailwind" --input-css-path "./my-tailwind/input.css" --output-css-path "./my-tailwind/output.css" --config-js-path "./my-tailwind/config.js"
```

## 架构

插件遵循干净的面向对象架构：

### 主要类

1. **_TailwindCSSPlugin** ([plugin.py](./dash_tailwindcss_plugin/plugin.py)): 处理所有 Tailwind CSS 集成的主插件类
2. **_TailwindCLI** ([cli.py](./dash_tailwindcss_plugin/cli.py)): 提供命令行界面的 CLI 工具类
3. **实用函数** ([utils.py](./dash_tailwindcss_plugin/utils.py)): Node.js 管理、文件操作等辅助函数

### 入口点

- `setup_tailwindcss_plugin()`: 插件的主入口点
- `main()`: CLI 工具的入口点

这种设计确保了关注点的清晰分离，使代码库更易于维护和扩展。
