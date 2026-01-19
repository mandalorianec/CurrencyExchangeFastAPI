from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.service.exchange_service import ExchangeService


@pytest.mark.anyio
async def test_post_currency(client: AsyncClient):
    form_data = {"name": "Euro", "code": "EUR", "sign": "E"}
    response = await client.post("/currencies", data=form_data)
    assert response.status_code == 201
    assert response.json()["code"] == "EUR"


@pytest.mark.anyio
@pytest.mark.parametrize("amount", [(Decimal(24))])
async def test_convert_usd_rub(
        exchange_service: ExchangeService, amount: Decimal, client: AsyncClient, rub_currency, usd_currency,
        exchange_rate
):
    response = (await exchange_service.convert("USD", "RUB", amount)).converted_amount
    assert response == Decimal(str(exchange_rate.rate)) * amount


@pytest.mark.anyio
@pytest.mark.parametrize("amount", [(Decimal(24))])
async def test_convert_rub_usd(exchange_service: ExchangeService, amount: Decimal, client: AsyncClient, rub_currency,
                               usd_currency, exchange_rate):
    response = (await exchange_service.convert("RUB", "USD", amount)).converted_amount
    assert response == (1/Decimal(str(exchange_rate.rate)) * amount).quantize(Decimal("0.000001"))


@pytest.mark.anyio
async def test_get_currency(usd_currency, client):
    response = await client.get(f"/currency/{usd_currency.code}")
    assert response.status_code == 200
    assert response.json()["code"] == usd_currency.code
