from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.service.exchange_service import ExchangeService


@pytest.mark.anyio
async def test_post_currency(client: AsyncClient):
    form_data = {"name": "Russian Ruble", "code": "RUB", "sign": "R"}
    response = await client.post("/currencies", data=form_data)
    assert response.status_code == 201
    assert response.json()["code"] == "RUB"


@pytest.mark.anyio
@pytest.mark.parametrize("from_, to, amount", [("USD", "RUB", Decimal(24))])
async def test_convert(exchange_service: ExchangeService, from_: str, to: str, amount: Decimal, client: AsyncClient):
    form_data = {"name": "Russian Ruble", "code": "RUB", "sign": "R"}
    await client.post("/currencies", data=form_data)
    form_data = {"name": "US Dollar", "code": "USD", "sign": "$"}
    await client.post("/currencies", data=form_data)
    form_data = {"baseCurrencyCode": "USD", "targetCurrencyCode": "RUB", "rate": "23"}
    await client.post("/exchangeRates", data=form_data)
    response = (await exchange_service.convert(from_, to, amount)).converted_amount
    assert response == Decimal("552")


@pytest.mark.anyio
async def test_get_currency(usd_currency, client):
    response = await client.get(f"/currency/{usd_currency.code}")
    assert response.status_code == 200
    assert response.json()["code"] == usd_currency.code
