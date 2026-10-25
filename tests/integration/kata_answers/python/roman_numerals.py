NUMERALS = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]
LETTERS = {letters: value for value, letters in NUMERALS if len(letters) == 1}


def to_roman(number: int) -> str:
    if not 1 <= number <= 3999:
        raise ValueError(f"{number} has no Roman numeral here")
    text = ""
    for value, letters in NUMERALS:
        count, number = divmod(number, value)
        text += letters * count
    return text


def from_roman(text: str) -> int:
    values = [LETTERS[letter] for letter in text]
    following = [*values[1:], 0]
    return sum(
        -value if value < after else value for value, after in zip(values, following, strict=True)
    )
