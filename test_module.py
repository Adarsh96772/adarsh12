"""Single-file script with custom division logic and Pytest unit tests."""

import pytest

def split_amount(total, parts):
    """
    Splits a total amount into equal parts.

    Raises:
        ValueError: If parts is zero or negative.
    """
    if parts <= 0:
        raise ValueError("Number of parts must be greater than zero.")
    return total / parts

# ----------------- Pytest Tests -----------------

def test_split_amount_even():
    """Test splitting a positive total evenly."""
    assert split_amount(100, 4) == 25

def test_split_amount_negative_total():
    """Test splitting a negative total."""
    assert split_amount(-50, 2) == -25

def test_split_amount_floats():
    """Test splitting floating point values."""
    assert split_amount(7.5, 2.5) == 3.0

def test_split_amount_zero_parts():
    """Test division by zero parts raises ValueError."""
    with pytest.raises(ValueError, match="greater than zero"):
        split_amount(100, 0)

def test_split_amount_negative_parts():
    """Test negative parts raises ValueError."""
    with pytest.raises(ValueError, match="greater than zero"):
        split_amount(100, -5)