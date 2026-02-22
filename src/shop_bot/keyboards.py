from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🛍 Купить номер', callback_data='buy')],
            [InlineKeyboardButton(text='💳 Мои оплаты', callback_data='payments')],
            [InlineKeyboardButton(text='🧾 Мои активации', callback_data='orders')],
            [InlineKeyboardButton(text='🆘 Поддержка', callback_data='support')],
        ]
    )


def service_menu(services: list[tuple[str, str, float]]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{name} · {price:.2f} ₽', callback_data=f'service:{code}'
            )
        ]
        for code, name, price in services[:30]
    ]
    buttons.append([InlineKeyboardButton(text='⬅️ Назад', callback_data='back_main')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_menu(url: str, invoice_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💸 Оплатить', url=url)],
            [
                InlineKeyboardButton(
                    text='✅ Проверить оплату', callback_data=f'check_invoice:{invoice_id}'
                )
            ],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_main')],
        ]
    )


def order_menu(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄 Проверить SMS', callback_data=f'check_sms:{order_id}')],
            [InlineKeyboardButton(text='❌ Отменить', callback_data=f'cancel:{order_id}')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='back_main')],
        ]
    )
