import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_post_currency(client: AsyncClient):
    form_data = {"name": "Russian Ruble", "code": "RUB", "sign": "R"}
    response = await client.post("/currencies", data=form_data)
    assert response.status_code == 201
    assert response.json()["code"] == "RUB"
