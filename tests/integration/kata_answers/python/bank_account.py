class InsufficientFundsError(Exception):
    pass


class Account:
    def __init__(self, owner: str) -> None:
        self.owner = owner
        self.history: list[float] = []

    @property
    def balance(self) -> float:
        return sum(self.history)

    def deposit(self, amount: float) -> None:
        self.history.append(positive(amount))

    def withdraw(self, amount: float) -> None:
        if positive(amount) > self.balance:
            raise InsufficientFundsError(f"{self.owner} has only {self.balance}")
        self.history.append(-amount)


def positive(amount: float) -> float:
    if amount <= 0:
        raise ValueError("an amount must be above 0")
    return amount
