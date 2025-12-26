from httpx import AsyncClient
import pytest


@pytest.mark.anyio
async def test_get_currencies(ac: AsyncClient, override_currency_service):
    response = await ac.get("/currencies")
    assert response.status_code == 200
    assert response.json()[0]["code"] == "USD"
    assert response.json()[1]["code"] == "EUR"


@pytest.mark.anyio
async def test_post_currencies_missing_field(ac: AsyncClient):
    response = await ac.post("/currencies")
    assert response.status_code == 400


@pytest.mark.anyio
async def test_post_currency(ac: AsyncClient, override_currency_service):
    form_data = {"name": "Russian Ruble", "code": "RUB", "sign": "R"}
    response = await ac.post("/currencies", data=form_data )
    assert response.status_code == 201
    assert response.json()["code"] == "RUB"
