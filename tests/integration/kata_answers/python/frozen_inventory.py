from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Item:
    name: str
    price: float
    quantity: int = 0


def total_value(items: list[Item]) -> float:
    return sum(item.price * item.quantity for item in items)


def restock(item: Item, amount: int) -> Item:
    return replace(item, quantity=item.quantity + amount)
