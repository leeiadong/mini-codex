import pytest

from calculator import add, multiply
from validator import validate_amount
from service import calculate_total, calculate_discount


def test_add():
    assert add(2, 3) == 5


def test_multiply():
    assert multiply(3, 4) == 12


def test_validate_positive_amount():
    assert validate_amount(100) is True


def test_validate_zero_amount():
    assert validate_amount(0) is True


def test_validate_negative_amount():
    assert validate_amount(-10) is False


def test_calculate_total():
    assert calculate_total(10, 3) == 30


def test_calculate_discount():
    assert calculate_discount(100, 20) == 80


def test_calculate_total_rejects_negative_price():
    with pytest.raises(ValueError):
        calculate_total(-10, 2)