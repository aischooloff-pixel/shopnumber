# Telegram-магазин виртуальных номеров (TigerSMS + CryptoBot)

Бот реализует магазин виртуальных номеров с:
- поставщиком номеров через **TigerSMS API**;
- пополнением через **CryptoBot API**;
- управлением через **Telegram Bot API** (aiogram).

## Важно про Vercel
`start_polling` не подходит для serverless-платформ, поэтому для Vercel используется **webhook-режим**:
- входящий endpoint: `POST /api/webhook`;
- healthcheck: `GET /`;
- установка webhook: `POST /api/setup-webhook`.

## Быстрый старт локально
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Запуск локально (polling)
```bash
PYTHONPATH=src python -m shop_bot.bot
```

## Деплой на Vercel
1. Подключите репозиторий к Vercel.
2. В Vercel Project Settings → Environment Variables добавьте:
   - `TELEGRAM_BOT_TOKEN`
   - `TIGER_API_KEY`
   - `CRYPTOBOT_API_TOKEN`
   - `PUBLIC_BASE_URL` (например, `https://shopnumber.vercel.app`)
   - `TELEGRAM_WEBHOOK_SECRET` (случайная длинная строка)
   - остальные переменные из `.env.example` при необходимости.
3. После деплоя вызовите:
   - `POST https://<ваш-домен>/api/setup-webhook`
4. Проверьте:
   - `GET https://<ваш-домен>/` должно вернуть `{"status":"ok"}`.

Если webhook не установлен, сообщения `/start` в Telegram не будут обрабатываться.

## Что уже реализовано
- Покупка номера по выбранному сервису.
- Автопредложение пополнения, если недостаточно средств.
- Проверка статуса крипто-инвойса.
- Проверка SMS-статуса активации и отмена активации.
