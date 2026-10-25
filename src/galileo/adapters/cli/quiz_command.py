"""`galileo quiz`: up to three questions about Omar's merged code. Each shows a test's setup and
asks what an expression gives; the answer is graded by value and recorded for understanding."""

from galileo.adapters.cli.context import Context
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.adapters.understanding.git_questions import GitQuestions
from galileo.adapters.understanding.history import FileHistory
from galileo.adapters.understanding.repositories import repositories
from galileo.application.understanding import QuizTools, answer, next_questions

NOTHING_DUE = (
    "No questions due. They come from tests merged on main in the last 30 days of the "
    "repositories listed in understanding.toml in your data folder.\n"
)


def quiz(context: Context) -> int:
    folder, today = context.folder, context.now.date()
    tools = QuizTools(
        GitQuestions(repositories(folder)),
        FileHistory(folder / "understanding"),
        ScoreFiles(folder),
    )
    questions = next_questions(tools, today)
    if not questions:
        context.output.write(NOTHING_DUE)
        return 0
    right = 0
    for number, question in enumerate(questions, start=1):
        heading = f"Question {number} of {len(questions)} · {question.place}"
        context.output.write(f"\n{heading}\n\n{question.context}\n\n")
        if answer(tools, question, context.ask("Your answer: "), today):
            right += 1
            context.output.write("Right.\n")
        else:
            context.output.write(f"Not quite: it's {question.expected}.\n")
    context.output.write(f"\n{right} of {len(questions)} right. Recorded for understanding.\n")
    return 0
