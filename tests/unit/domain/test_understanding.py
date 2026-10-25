"""Questions about Omar's own merged code: graded by value, repeated once a week later."""

from datetime import date, timedelta

from galileo.domain.understanding.question import Asked, Question, due, is_right

TODAY = date(2026, 11, 9)


def question(key: str) -> Question:
    return Question(key, "galileo: tests/unit/test_x.py:3", f"{key}()", "1")


def test_an_answer_is_right_by_value() -> None:
    assert is_right("0.75", "0.75")
    assert is_right(" 3 ", "3.0")
    assert is_right("[1, 2]", "[1, 2]")
    assert not is_right("0.7", "0.75")


def test_an_unquoted_word_means_that_string() -> None:
    assert is_right("alpha", "'alpha'")
    assert is_right("'alpha'", "'alpha'")
    assert not is_right("beta", "'alpha'")


def test_true_isnt_one() -> None:
    assert not is_right("1", "True")
    assert is_right("True", "True")


def test_floats_compare_as_close() -> None:
    assert is_right("0.30000000000000004", "0.3")


def test_never_asked_questions_come_in_order() -> None:
    questions = [question("a"), question("b"), question("c")]
    assert due(questions, [], TODAY, count=2) == [question("a"), question("b")]


def test_a_question_comes_back_once_a_week_later_and_first() -> None:
    questions = [question("a"), question("b")]
    history = [Asked("a", TODAY - timedelta(days=7), right=False)]
    assert due(questions, history, TODAY, count=2) == [question("a"), question("b")]


def test_not_before_a_week_and_not_a_third_time() -> None:
    questions = [question("a"), question("b")]
    history = [
        Asked("a", TODAY - timedelta(days=6), right=True),
        Asked("b", TODAY - timedelta(days=20), right=True),
        Asked("b", TODAY - timedelta(days=10), right=True),
    ]
    assert due(questions, history, TODAY, count=3) == []
