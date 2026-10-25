from collections.abc import Iterator


def fizzbuzz(limit: int) -> Iterator[str]:
    for number in range(1, limit + 1):
        word = ("Fizz" if number % 3 == 0 else "") + ("Buzz" if number % 5 == 0 else "")
        yield word or str(number)
