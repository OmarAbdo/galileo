def pairs(numbers: list[int], target: int) -> list[tuple[int, int]]:
    return [
        (first, second)
        for first in range(len(numbers))
        for second in range(first + 1, len(numbers))
        if numbers[first] + numbers[second] == target
    ]
