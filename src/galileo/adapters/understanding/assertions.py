"""Questions from a test file. Each `assert <expression> == <expected>` inside a test function,
where the expression calls something and the expected value is a literal (`pytest.approx` of a
literal counts), becomes a question. Omar sees the test up to that line, then the expression
followed by `== ?`."""

import ast
import hashlib
from typing import TypeGuard

from galileo.domain.understanding.question import Question


def compares_a_call(test: ast.expr) -> TypeGuard[ast.Compare]:
    return (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and any(isinstance(part, ast.Call) for part in ast.walk(test.left))
    )


def expected_text(node: ast.expr, source: str) -> str | None:
    if isinstance(node, ast.Call) and len(node.args) == 1 and "approx" in ast.unparse(node.func):
        node = node.args[0]
    try:
        ast.literal_eval(node)
    except ValueError:
        return None
    return ast.get_source_segment(source, node)


def question_at(
    node: ast.Assert, test: ast.FunctionDef, source: str, place: str
) -> Question | None:
    if not compares_a_call(node.test):
        return None
    expected = expected_text(node.test.comparators[0], source)
    expression = ast.get_source_segment(source, node.test.left)
    if expected is None or expression is None:
        return None
    setup = source.splitlines()[test.lineno - 1 : node.lineno - 1]
    context = "\n".join([*setup, f"{' ' * node.col_offset}{expression} == ?"])
    key = hashlib.sha256(f"{place}|{expression}|{expected}".encode()).hexdigest()[:16]
    return Question(key, f"{place}:{node.lineno}", expression, expected, context)


def questions_in(source: str, place: str) -> list[Question]:
    found: list[Question | None] = []
    for test in ast.walk(ast.parse(source)):
        if not isinstance(test, ast.FunctionDef) or not test.name.startswith("test"):
            continue
        asserts = [node for node in ast.walk(test) if isinstance(node, ast.Assert)]
        ordered = sorted(asserts, key=lambda node: node.lineno)
        found.extend(question_at(node, test, source, place) for node in ordered)
    return [question for question in found if question]
