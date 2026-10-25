import re
from collections import Counter


def word_counts(text: str) -> dict[str, int]:
    return dict(Counter(re.findall(r"[a-z]+", text.lower())))
