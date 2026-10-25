from collections import defaultdict
from typing import Any


def oldest_first(people: list[dict[str, Any]]) -> list[str]:
    ordered = sorted(people, key=lambda person: (-person["age"], person["name"]))
    return [person["name"] for person in ordered]


def by_initial(people: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for person in people:
        groups[person["name"][0]].append(person["name"])
    return dict(groups)
