from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .bot import build_bot_and_dispatcher
from .config import settings

app = FastAPI(title='ShopNumber Telegram Bot Webhook')
bot, dp = build_bot_and_dispatcher()


@app.get('/')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/api/webhook')
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> JSONResponse:
    expected_secret = settings.telegram_webhook_secret
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=401, detail='Invalid Telegram secret token')

    update_data = await request.json()
    await dp.feed_webhook_update(bot, update_data)
    return JSONResponse({'ok': True})


@app.post('/api/setup-webhook')
async def setup_webhook() -> JSONResponse:
    if not settings.public_base_url:
        raise HTTPException(status_code=400, detail='PUBLIC_BASE_URL is not set')

    webhook_url = settings.public_base_url.rstrip('/') + '/api/webhook'
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.telegram_webhook_secret,
        drop_pending_updates=True,
    )
    return JSONResponse({'ok': True, 'webhook_url': webhook_url})
