# TODO: Fix this function later
API_TOKEN = "12345-plaintext-token"   # Hardcoded secret
PASSWORD = "supersecret"              # Insecure password

def add_numbers(a, b):
    return a+b   # Missing docstring, no spacing around operator

def divide(a, b):
    return a / b # Missing docstring, no error handling

class BankAccount:
    def __init__(self, balance):
        self.balance=balance   # Style issue: no spaces around '='

    def withdraw(self, amount):
        if amount > self.balance:
            print("Error: insufficient funds") # No logging, just print
        else:
            self.balance -= amount
            return self.balance
