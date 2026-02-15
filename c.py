"""Example module demonstrating clean code practices."""


def add_numbers(a, b):
    """
    Add two numbers together.

    Args:
        a (int or float): First number.
        b (int or float): Second number.

    Returns:
        int or float: The sum of a and b.
    """
    return a + b


def divide(a, b):
    """
    Divide one number by another.

    Args:
        a (int or float): Numerator.
        b (int or float): Denominator.

    Returns:
        float: The result of division.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


class BankAccount:
    """
    A simple bank account class.
    """

    def __init__(self, balance=0):
        """
        Initialize the account with a balance.

        Args:
            balance (int or float): Initial balance. Defaults to 0.
        """
        self.balance = balance

    def withdraw(self, amount):
        """
        Withdraw money from the account.

        Args:
            amount (int or float): Amount to withdraw.

        Returns:
            int or float: Remaining balance.

        Raises:
            ValueError: If amount exceeds balance.
        """
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        return self.balance
