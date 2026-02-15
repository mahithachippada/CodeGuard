# TODO: Refactor this messy code later
API_KEY = "abcd1234-plaintext"   # Hardcoded secret
PASSWORD = "mypassword"          # Insecure password

def add(a,b):
    return a+b   # No docstring, spacing issue

def divide(a,b):
    return a/b   # No docstring, no zero check

class User:
    def __init__(self,name,email):
        self.name=name   # Style issue: no spaces
        self.email=email

    def login(self,password):
        if password == PASSWORD:
            print("Login successful")  # Bad practice: prints instead of secure check
        else:
            print("Login failed")

def long_line_function():
    print("This is a very very very very very very very very very very very very very very very very very very very very very very long line that should trigger a style warning")
