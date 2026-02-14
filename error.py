# TODO: Refactor this function later


def calculate_average(marks):
    total = sum(marks)
    return total / len(marks)


def BadFunctionName(x, y):
    print(
        "This is a very long line that will definitely exceed eighty characters just to trigger the analyzer rule for testing purposes and show up in the scan results"
    )
    return x + y
