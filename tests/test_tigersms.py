import pytest

from shop_bot.tigersms import TigerSMSClient


class FakeTiger(TigerSMSClient):
    def __init__(self, response: str):
        super().__init__('http://example.com', 'k')
        self.response = response

    async def _request(self, **params) -> str:
        return self.response


@pytest.mark.asyncio
async def test_get_services_flat_schema() -> None:
    client = FakeTiger('{"tg": {"cost": 10, "count": 5}, "wa": {"cost": 0, "count": 2}}')
    services = await client.get_services('ru')
    assert services == [('tg', 'TG', 10.0)]


@pytest.mark.asyncio
async def test_get_services_nested_schema() -> None:
    client = FakeTiger('{"ru": {"vk": {"cost": 12, "count": 1}}}')
    services = await client.get_services('ru')
    assert services == [('vk', 'VK', 12.0)]
