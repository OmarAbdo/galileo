import re
from itertools import groupby


def encode(text: str) -> str:
    runs = ((letter, len(list(run))) for letter, run in groupby(text))
    return "".join(f"{length}{letter}" if length > 1 else letter for letter, length in runs)


def decode(text: str) -> str:
    runs = re.findall(r"(\d*)(\D)", text)
    return "".join(letter * int(length or 1) for length, letter in runs)
