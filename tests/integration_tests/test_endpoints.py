import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_currency_eur(client: AsyncClient, eur_currency) -> None:
    response = await client.get(f"/currency/{eur_currency.code}")
    assert response.status_code == 200
    assert response.json()["code"] == "EUR"


@pytest.mark.anyio
async def test_post_currency(client: AsyncClient) -> None:
    form_data = {"name": "Euro", "code": "EUR", "sign": "E"}
    response = await client.post("/currencies", data=form_data)
    assert response.status_code == 201
    assert response.json()["code"] == "EUR"


@pytest.mark.anyio
async def test_get_all_currencies(client: AsyncClient, usd_currency, eur_currency, rub_currency) -> None:
    response = await client.get("/currencies")
    assert response.status_code == 200
    assert response.json()[0]["code"] == "USD"
    assert response.json()[1]["code"] == "EUR"
    assert response.json()[2]["code"] == "RUB"


@pytest.mark.anyio
async def test_get_all_exchange_rates(client: AsyncClient, exchange_rate_usd_eur, exchange_rate_usd_rub) -> None:
    response = await client.get("/exchangeRates")
    assert response.status_code == 200
    assert response.json()[0]["baseCurrency"]["code"] == "USD"
    assert response.json()[0]["targetCurrency"]["code"] == "EUR"
    assert response.json()[1]["baseCurrency"]["code"] == "USD"
    assert response.json()[1]["targetCurrency"]["code"] == "RUB"


@pytest.mark.anyio
async def test_get_exchange_rate_usd_rub(client: AsyncClient, exchange_rate_usd_rub) -> None:
    response = await client.get("/exchangeRate/USDRUB")
    assert response.status_code == 200
    assert response.json()["baseCurrency"]["code"] == "USD"
    assert response.json()["targetCurrency"]["code"] == "RUB"


@pytest.mark.anyio
async def test_post_exchange_rate(client: AsyncClient, usd_currency, rub_currency) -> None:
    form_data = {"baseCurrencyCode": usd_currency.code, "targetCurrencyCode": rub_currency.code, "rate": 120}
    response = await client.post("/exchangeRates", data=form_data)
    assert response.status_code == 201
    assert response.json()["baseCurrency"]["code"] == "USD"
    assert response.json()["targetCurrency"]["code"] == "RUB"
    assert response.json()["rate"] == 120


@pytest.mark.anyio
async def test_patch_exchange_rate(client: AsyncClient, exchange_rate_usd_eur) -> None:
    form_data = {"rate": 10}
    response = await client.patch("exchangeRate/USDEUR", data=form_data)
    assert response.status_code == 200
    assert response.json()["rate"] == 10


@pytest.mark.anyio
async def test_get_non_existent_exchange_rate(client: AsyncClient) -> None:
    response = await client.get("/exchangeRate/ABCEDF")
    assert response.status_code == 404
    assert "message" in response.json()
    assert "Обменный курс для пары не найден" in response.json()["message"]


@pytest.mark.anyio
async def test_add_already_existent_currency(client: AsyncClient, usd_currency) -> None:
    form_data = {"name": "US Dollar", "code": "USD", "sign": "$"}
    response = await client.post("/currencies", data=form_data)
    assert response.status_code == 409
    assert "message" in response.json()
    assert "Валюта с таким кодом уже существует" in response.json()["message"]
