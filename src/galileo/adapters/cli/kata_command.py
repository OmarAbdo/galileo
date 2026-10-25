"""`galileo kata`: start the next kata or show the open one. `galileo kata check` runs its tests;
a pass records hands. `galileo kata stop` closes it without a record."""

from pathlib import Path

from galileo.adapters.cli.context import Context
from galileo.adapters.katas.bank import TomlBank
from galileo.adapters.katas.desk import FileDesk
from galileo.adapters.katas.languages import LANGUAGES
from galileo.adapters.katas.runner import KataRunner
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.application.katas import (
    KataTools,
    NoKataError,
    check_kata,
    find,
    start_kata,
    stop_kata,
)

LANGUAGE = "python"


def kata_tools(folder: Path, bank: TomlBank) -> KataTools:
    return KataTools(bank, FileDesk(folder / "katas"), KataRunner(), ScoreFiles(folder))


def duration(seconds: float) -> str:
    return f"{int(seconds // 60)} min {int(seconds % 60)} s"


def start(context: Context, tools: KataTools) -> int:
    language = context.action or LANGUAGE  # galileo kata go asks for a Go kata
    session = start_kata(tools, language, context.now)
    kata = find(tools.bank, session)
    minutes = int((context.now - session.started).total_seconds() // 60)
    since = f"Open since {session.started:%H:%M} ({minutes} min)."
    if minutes == 0:
        since = f"Started at {session.started:%H:%M}."
    solution = session.folder / LANGUAGES[session.language].solution
    context.output.write(
        f"{kata.title} (reference {kata.reference_seconds // 60} min)\n\n{kata.prompt}\n\n"
        f"Your file: {solution}\n{since} Run `galileo kata check` when you think it passes.\n"
    )
    return 0


def check(context: Context, tools: KataTools) -> int:
    result = check_kata(tools, context.now)
    if not result.passed:
        context.output.write(f"Not passing yet:\n{result.output}\n")
        return 1
    passed = f"Passed in {duration(result.seconds)}"
    if result.value is None:
        context.output.write(f"{passed}, but a kata open over an hour isn't counted.\n")
        return 0
    context.output.write(f"{passed}: {result.value:.2f} times the reference. Recorded for hands.\n")
    return 0


def stop(context: Context, tools: KataTools) -> int:
    stopped = stop_kata(tools.desk)
    context.output.write("Stopped. Nothing was recorded.\n" if stopped else "No kata is open.\n")
    return 0


ACTIONS = {None: start, "check": check, "stop": stop}


def run_kata(context: Context, tools: KataTools) -> int:
    try:
        return ACTIONS.get(context.action, start)(context, tools)
    except NoKataError as problem:
        context.output.write(f"{problem}\n")
        return 1


def kata(context: Context) -> int:
    return run_kata(context, kata_tools(context.folder, TomlBank()))
