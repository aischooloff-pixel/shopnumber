from shop_bot.storage import MemoryStore


def test_pending_invoice_lifecycle() -> None:
    store = MemoryStore()
    store.create_pending_invoice(invoice_id=1, user_id=10, amount_rub=25.5)

    pending = store.get_pending_invoice(1)
    assert pending is not None
    assert pending.user_id == 10
    assert pending.amount_rub == 25.5

    popped = store.pop_pending_invoice(1)
    assert popped is not None
    assert popped.user_id == 10
    assert store.get_pending_invoice(1) is None
