from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from .config import settings
from .cryptobot import CryptoBotClient
from .keyboards import main_menu, order_menu, payment_menu, service_menu
from .storage import MemoryStore
from .tigersms import TigerSMSClient


logging.basicConfig(level=logging.INFO)

store = MemoryStore()


def create_dispatcher(tiger: TigerSMSClient, crypto: CryptoBotClient) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message) -> None:
        bal = store.get_balance(message.from_user.id)
        await message.answer(
            'Добро пожаловать в магазин виртуальных номеров.\n'
            f'Баланс: {bal:.2f} ₽\n\n'
            'Выберите действие:',
            reply_markup=main_menu(),
        )

    @dp.callback_query(F.data == 'back_main')
    async def back_main(callback: CallbackQuery) -> None:
        bal = store.get_balance(callback.from_user.id)
        await callback.message.edit_text(
            f'Главное меню\nБаланс: {bal:.2f} ₽',
            reply_markup=main_menu(),
        )
        await callback.answer()

    @dp.callback_query(F.data == 'buy')
    async def buy(callback: CallbackQuery) -> None:
        try:
            services = await tiger.get_services(settings.default_country)
            if not services:
                raise ValueError('Нет доступных сервисов')
            await callback.message.edit_text(
                'Выберите сервис для покупки номера:',
                reply_markup=service_menu(services),
            )
        except Exception as exc:
            await callback.message.answer(f'Ошибка поставщика: {exc}')
        await callback.answer()

    @dp.callback_query(F.data.startswith('service:'))
    async def buy_service(callback: CallbackQuery) -> None:
        service = callback.data.split(':', 1)[1]
        try:
            services = await tiger.get_services(settings.default_country)
            picked = next((x for x in services if x[0] == service), None)
            if not picked:
                await callback.answer('Сервис недоступен', show_alert=True)
                return

            price = picked[2]
            if not store.spend(callback.from_user.id, price):
                need_amount = round(max(1.0, price - store.get_balance(callback.from_user.id)), 2)
                invoice_id, pay_url = await crypto.create_invoice(
                    amount=need_amount,
                    asset=settings.payment_asset,
                    description=f'Topup for user {callback.from_user.id}',
                )
                store.create_pending_invoice(invoice_id, callback.from_user.id, need_amount)
                await callback.message.edit_text(
                    f'Недостаточно средств.\nДля покупки нужно: {price:.2f} ₽\n'
                    f'Пополните баланс на {need_amount:.2f} {settings.payment_asset}',
                    reply_markup=payment_menu(pay_url, invoice_id),
                )
                await callback.answer()
                return

            order_id, number = await tiger.get_number(
                service=service,
                country=settings.default_country,
                max_price=settings.default_max_price,
            )
            store.create_order(callback.from_user.id, order_id)
            await callback.message.edit_text(
                f'✅ Номер получен\n'
                f'Сервис: {service.upper()}\n'
                f'Номер: <code>{number}</code>\n'
                f'ID активации: <code>{order_id}</code>\n\n'
                'Ожидайте SMS и нажмите «Проверить SMS».',
                reply_markup=order_menu(order_id),
            )
        except Exception as exc:
            await callback.message.answer(f'Ошибка покупки: {exc}')
        await callback.answer()

    @dp.callback_query(F.data.startswith('check_invoice:'))
    async def check_invoice(callback: CallbackQuery) -> None:
        invoice_id = int(callback.data.split(':', 1)[1])
        pending = store.get_pending_invoice(invoice_id)
        if not pending or pending.user_id != callback.from_user.id:
            await callback.answer('Инвойс не найден', show_alert=True)
            return

        status = await crypto.get_invoice_status(invoice_id)
        if status == 'paid':
            paid = store.pop_pending_invoice(invoice_id)
            amount = paid.amount_rub if paid else 0.0
            new_balance = store.add_balance(callback.from_user.id, amount)
            await callback.message.edit_text(
                f'Платеж подтвержден ✅\nНачислено: {amount:.2f} ₽\nБаланс: {new_balance:.2f} ₽',
                reply_markup=main_menu(),
            )
        else:
            await callback.answer(f'Статус: {status}', show_alert=True)

    @dp.callback_query(F.data.startswith('check_sms:'))
    async def check_sms(callback: CallbackQuery) -> None:
        order_id = callback.data.split(':', 1)[1]
        if not store.has_order(callback.from_user.id, order_id):
            await callback.answer('Активация не найдена', show_alert=True)
            return
        status = await tiger.get_status(order_id)
        await callback.answer()
        await callback.message.answer(f'Статус активации: {status}')

    @dp.callback_query(F.data.startswith('cancel:'))
    async def cancel(callback: CallbackQuery) -> None:
        order_id = callback.data.split(':', 1)[1]
        if not store.has_order(callback.from_user.id, order_id):
            await callback.answer('Активация не найдена', show_alert=True)
            return
        result = await tiger.set_status(order_id, 8)
        await callback.answer('Отменено')
        await callback.message.answer(f'Результат отмены: {result}')

    @dp.callback_query(F.data == 'payments')
    async def payments(callback: CallbackQuery) -> None:
        await callback.answer('Активные платежи доступны из сценария покупки номера', show_alert=True)

    @dp.callback_query(F.data == 'orders')
    async def orders(callback: CallbackQuery) -> None:
        orders_list = store.list_orders(callback.from_user.id)
        text = 'Ваши активации:\n' + ('\n'.join(orders_list) if orders_list else 'Пока нет')
        await callback.message.answer(text)
        await callback.answer()

    @dp.callback_query(F.data == 'support')
    async def support(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(f'Поддержка: {settings.support_username}')

    return dp


def build_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.telegram_bot_token)
    tiger = TigerSMSClient(settings.tiger_base_url, settings.tiger_api_key)
    crypto = CryptoBotClient(settings.cryptobot_base_url, settings.cryptobot_api_token)
    dp = create_dispatcher(tiger=tiger, crypto=crypto)
    return bot, dp


async def main() -> None:
    bot, dp = build_bot_and_dispatcher()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
