import operator
from collections.abc import Callable

OPERATORS: dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def apply(stack: list[float], word: str) -> None:
    if len(stack) < 2:
        raise ValueError(f"{word} needs two numbers before it")
    right, left = stack.pop(), stack.pop()
    stack.append(OPERATORS[word](left, right))


def evaluate(expression: str) -> float:
    stack: list[float] = []
    for word in expression.split():
        if word in OPERATORS:
            apply(stack, word)
        else:
            stack.append(float(word))
    if len(stack) != 1:
        raise ValueError("the expression must end with exactly one number")
    return stack[0]
