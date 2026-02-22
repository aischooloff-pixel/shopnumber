from dataclasses import dataclass


@dataclass
class UserState:
    balance: float = 0.0


class MemoryStore:
    def __init__(self) -> None:
        self.user_balances: dict[int, float] = {}
        self.user_orders: dict[int, list[str]] = {}
        self.order_owner: dict[str, int] = {}

    def add_balance(self, user_id: int, amount: float) -> float:
        current = self.user_balances.get(user_id, 0.0) + amount
        self.user_balances[user_id] = current
        return current

    def get_balance(self, user_id: int) -> float:
        return self.user_balances.get(user_id, 0.0)

    def spend(self, user_id: int, amount: float) -> bool:
        balance = self.get_balance(user_id)
        if balance < amount:
            return False
        self.user_balances[user_id] = balance - amount
        return True

    def create_order(self, user_id: int, order_id: str) -> None:
        self.user_orders.setdefault(user_id, []).append(order_id)
        self.order_owner[order_id] = user_id

    def has_order(self, user_id: int, order_id: str) -> bool:
        return self.order_owner.get(order_id) == user_id

    def list_orders(self, user_id: int) -> list[str]:
        return self.user_orders.get(user_id, [])
