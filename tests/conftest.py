#!/usr/bin/env python3
"""
Configuration file for pytest.

This file contains fixtures and configuration that will be used by all tests.
"""

import pytest
import os
import sys
import tempfile
import shutil


# Add the project root to the Python path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def test_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_working_directory():
    """Create a temporary working directory for tests."""
    original_cwd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)
