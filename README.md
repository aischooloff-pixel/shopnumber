# Telegram-магазин виртуальных номеров (TigerSMS + CryptoBot)

Бот реализует магазин виртуальных номеров с:
- поставщиком номеров через **TigerSMS API**;
- пополнением через **CryptoBot API**;
- управлением через **Telegram Bot API** (aiogram).

## Что сделано
- Покупка номера по выбранному сервису.
- Автопредложение пополнения, если недостаточно средств.
- Проверка статуса крипто-инвойса.
- Проверка SMS-статуса активации и отмена активации.

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env` своими токенами.

Запуск:
```bash
PYTHONPATH=src python -m shop_bot.bot
```

## Переменные окружения
- `TELEGRAM_BOT_TOKEN` — токен Telegram-бота
- `TIGER_API_KEY` — ключ TigerSMS
- `TIGER_BASE_URL` — endpoint TigerSMS handler API
- `CRYPTOBOT_API_TOKEN` — токен CryptoBot
- `CRYPTOBOT_BASE_URL` — endpoint CryptoBot API
- `PAYMENT_ASSET` — актив оплаты (например, `USDT`)
- `DEFAULT_COUNTRY` — код страны для покупки
- `DEFAULT_MAX_PRICE` — максимальная цена номера
- `SUPPORT_USERNAME` — контакт поддержки

## Медиа из Google Drive
По предоставленной ссылке обнаружены медиафайлы:
- `photo_1_2026-02-22_19-42-57.jpg` ... `photo_8_2026-02-22_19-42-57.jpg`
- `video_0.mp4`
- `video_3.mp4`

При необходимости можно добавить отправку этих медиа в `/start` через `sendMediaGroup`.
