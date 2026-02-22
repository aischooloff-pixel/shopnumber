from __future__ import annotations

import json

import httpx


class TigerSMSClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key

    async def _request(self, **params) -> str:
        query = {'api_key': self.api_key, **params}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self.base_url, params=query)
            resp.raise_for_status()
            return resp.text.strip()

    async def get_balance(self) -> float:
        text = await self._request(action='getBalance')
        if ':' in text:
            return float(text.split(':', 1)[1])
        raise ValueError(f'Unexpected TigerSMS response: {text}')

    async def get_services(self, country: str) -> list[tuple[str, str, float]]:
        text = await self._request(action='getPrices', country=country)
        data = json.loads(text)

        # API variants:
        # 1) {"tg": {"cost": 12.3, "count": 100}}
        # 2) {"ru": {"tg": {"cost": 12.3, "count": 100}}}
        raw_services = data.get(country, data) if isinstance(data, dict) else {}
        if not isinstance(raw_services, dict):
            raise ValueError(f'Unexpected TigerSMS prices schema: {text[:300]}')

        services = []
        for code, meta in raw_services.items():
            if not isinstance(meta, dict):
                continue
            cost = float(meta.get('cost', 0.0))
            count = int(meta.get('count', 0))
            if count > 0 and cost > 0:
                services.append((code, code.upper(), cost))

        services.sort(key=lambda x: x[2])
        return services

    async def get_number(self, service: str, country: str, max_price: float) -> tuple[str, str]:
        text = await self._request(
            action='getNumber',
            service=service,
            country=country,
            maxPrice=max_price,
        )
        parts = text.split(':')
        if len(parts) == 3 and parts[0] == 'ACCESS_NUMBER':
            return parts[1], parts[2]
        raise ValueError(f'TigerSMS get_number failed: {text}')

    async def get_status(self, order_id: str) -> str:
        return await self._request(action='getStatus', id=order_id)

    async def set_status(self, order_id: str, status: int) -> str:
        return await self._request(action='setStatus', id=order_id, status=status)
