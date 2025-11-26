# 测试套件说明

本项目的测试套件使用 pytest 框架编写，包含以下测试文件：

## 测试文件结构

- `test_plugin.py` - 测试插件核心功能
- `test_utils.py` - 测试工具函数
- `test_cli.py` - 测试命令行接口
- `test_dash_integration.py` - 测试插件与 Dash 应用的端到端集成（需要浏览器自动化）
- `conftest.py` - pytest 配置和 fixtures
- `README.md` - 英文测试文档
- `README-zh_CN.md` - 中文测试文档

## 运行测试

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 运行所有测试

```bash
python -m pytest tests/
```

### 运行特定测试文件

```bash
python -m pytest tests/test_plugin.py
python -m pytest tests/test_utils.py
python -m pytest tests/test_cli.py
python -m pytest tests/test_dash_integration.py
```

### 运行测试并显示详细输出

```bash
python -m pytest tests/ -v
```

## 测试类型

### 单元测试

- 测试插件类的初始化和方法
- 测试工具函数的功能
- 测试CLI命令解析和执行

### 集成测试

- 测试插件与 Dash 应用的集成
- 测试端到端的工作流程

## 测试覆盖率

要生成测试覆盖率报告，请运行：

```bash
python -m pytest tests/ --cov=dash_tailwindcss_plugin --cov-report=html
```

这将生成一个 HTML 格式的覆盖率报告，可以在浏览器中查看。