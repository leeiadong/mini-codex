from calculator import multiply
from validator import validate_amount


def calculate_total(price: float, quantity: int) -> float:
    if not validate_amount(price):
        raise ValueError("Invalid price")

    if quantity <= 0:
        raise ValueError("Invalid quantity")

    return multiply(price, quantity)


def calculate_discount(price: float, discount: float) -> float:
    if not validate_amount(price):
        raise ValueError("Invalid price")

    return price - discount
