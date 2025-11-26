# Test Suite Documentation

This project's test suite is written using the pytest framework and includes the following test files:

## Test File Structure

- `test_plugin.py` - Tests core plugin functionality
- `test_utils.py` - Tests utility functions
- `test_cli.py` - Tests command-line interface
- `test_dash_integration.py` - Tests end-to-end Dash application integration (requires browser automation)
- `conftest.py` - pytest configuration and fixtures
- `README.md` - English test documentation
- `README-zh_CN.md` - Chinese test documentation

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
python -m pytest tests/
```

### Run Specific Test Files

```bash
python -m pytest tests/test_plugin.py
python -m pytest tests/test_utils.py
python -m pytest tests/test_cli.py
python -m pytest tests/test_dash_integration.py
```

### Run Tests with Verbose Output

```bash
python -m pytest tests/ -v
```

## Test Types

### Unit Tests

- Tests plugin class initialization and methods
- Tests utility function functionality
- Tests CLI command parsing and execution

### Integration Tests

- Tests plugin integration with Dash applications
- Tests end-to-end workflows

## Test Coverage

To generate a test coverage report, run:

```bash
python -m pytest tests/ --cov=dash_tailwindcss_plugin --cov-report=html
```

This will generate an HTML coverage report that can be viewed in a browser.
