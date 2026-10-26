# tests/unit/test_operations_extended.py

"""
Additional unit tests for app/operations.

These complement tests/unit/test_calculator.py with edge cases (large numbers,
floating-point precision, mixed signs) and checks that every operation is logged.
"""

import logging

import pytest

from app.operations import add, subtract, multiply, divide

OPERATIONS_LOGGER = "app.operations"


# ---------------------------------------------
# Edge cases
# ---------------------------------------------

@pytest.mark.parametrize(
    "func, a, b, expected",
    [
        (add, 1e15, 1e15, 2e15),
        (subtract, -1e15, 1e15, -2e15),
        (multiply, 1e8, 1e8, 1e16),
        (divide, 1e15, 1e5, 1e10),
    ],
    ids=["add_large", "subtract_large", "multiply_large", "divide_large"],
)
def test_large_numbers(func, a, b, expected):
    """Each operation handles very large magnitudes correctly."""
    assert func(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "func, a, b, expected",
    [
        (add, 0.1, 0.2, 0.3),
        (subtract, 0.3, 0.1, 0.2),
        (multiply, 0.1, 3, 0.3),
        (divide, 1, 3, 0.3333333333),
    ],
    ids=["add_float_precision", "subtract_float_precision",
         "multiply_float_precision", "divide_repeating_decimal"],
)
def test_floating_point_precision(func, a, b, expected):
    """Results are correct up to normal floating-point rounding."""
    assert func(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [(-6, -3, 2.0), (6, -3, -2.0), (-7, 2, -3.5)],
    ids=["negative_by_negative", "positive_by_negative", "negative_non_integer_result"],
)
def test_divide_sign_handling(a, b, expected):
    """Division follows the usual sign rules and returns non-integer results as floats."""
    assert divide(a, b) == expected


def test_divide_returns_float_for_exact_integer_division():
    """divide always returns a float, even when the division is exact."""
    result = divide(10, 5)
    assert isinstance(result, float)
    assert result == 2.0


@pytest.mark.parametrize("zero", [0, 0.0, -0.0], ids=["int_zero", "float_zero", "negative_float_zero"])
def test_divide_by_any_zero_raises(zero):
    """Every representation of zero is rejected as a divisor."""
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(1, zero)


# ---------------------------------------------
# Logging
# ---------------------------------------------

@pytest.mark.parametrize(
    "func, a, b, expected_message",
    [
        (add, 2, 3, "add(2, 3) = 5"),
        (subtract, 5, 3, "subtract(5, 3) = 2"),
        (multiply, 2, 3, "multiply(2, 3) = 6"),
        (divide, 6, 3, "divide(6, 3) = 2.0"),
    ],
    ids=["add", "subtract", "multiply", "divide"],
)
def test_operations_are_logged(caplog, func, a, b, expected_message):
    """Each successful operation writes a DEBUG record with its inputs and result."""
    caplog.set_level(logging.DEBUG, logger=OPERATIONS_LOGGER)

    func(a, b)

    assert expected_message in caplog.text
    assert all(record.levelno == logging.DEBUG for record in caplog.records)


def test_divide_by_zero_is_logged_as_error(caplog):
    """A division by zero is recorded at ERROR level before the exception is raised."""
    caplog.set_level(logging.DEBUG, logger=OPERATIONS_LOGGER)

    with pytest.raises(ValueError):
        divide(5, 0)

    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(error_records) == 1
    assert "divide(5, 0) failed: division by zero" in error_records[0].getMessage()
