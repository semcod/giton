"""
Tests for the sample Python module.
"""

import pytest
from src.example import add, multiply, divide


def test_add():
    """Test addition."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_multiply():
    """Test multiplication."""
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6


def test_divide():
    """Test division."""
    assert divide(6, 2) == 3.0
    assert divide(-6, 2) == -3.0


def test_divide_by_zero():
    """Test division by zero raises error."""
    with pytest.raises(ValueError):
        divide(1, 0)
