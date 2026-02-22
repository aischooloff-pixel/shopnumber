from __future__ import annotations

import httpx


class CryptoBotClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = {'Crypto-Pay-API-Token': token}

    async def create_invoice(self, amount: float, asset: str, description: str) -> tuple[int, str]:
        payload = {
            'amount': str(round(amount, 2)),
            'asset': asset,
            'description': description,
            'allow_comments': False,
            'allow_anonymous': True,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f'{self.base_url}/createInvoice',
                headers=self.headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        if not data.get('ok'):
            raise ValueError(data)
        result = data['result']
        return int(result['invoice_id']), result['pay_url']

    async def get_invoice_status(self, invoice_id: int) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f'{self.base_url}/getInvoices',
                headers=self.headers,
                params={'invoice_ids': invoice_id},
            )
            resp.raise_for_status()
            data = resp.json()
        if not data.get('ok'):
            raise ValueError(data)
        items = data['result'].get('items', [])
        if not items:
            return 'not_found'
        return items[0].get('status', 'unknown')
