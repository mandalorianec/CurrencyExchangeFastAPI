from unittest.mock import AsyncMock
from fastapi_limiter.depends import RateLimiter
from fastapi import Response, Request
from httpx import AsyncClient, ASGITransport
from app.service.currency_service import CurrencyService
from app.schemas import CurrencyResponse
from main import app
import pytest

CURRENCIES = [
    CurrencyResponse(id=1, name="US Dollar", code="USD", sign="$"),
    CurrencyResponse(id=2, name="Euro", code="EUR", sign="E")
]


@pytest.fixture
def override_currency_service():
    mock_service = AsyncMock()

    # подменяем возвращаемые значения
    mock_service.get_all_currencies.return_value = CURRENCIES
    mock_service.add_currency.return_value = CurrencyResponse(id=3, name="Russian Ruble", code="RUB", sign="R")

    app.dependency_overrides[CurrencyService] = lambda: mock_service
    yield mock_service
    app.dependency_overrides = {}


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture(autouse=True)
def disable_rate_limiter(monkeypatch):
    async def mock_call(self, request: Request, response: Response):
        return

    monkeypatch.setattr(RateLimiter, "__call__", mock_call)


@pytest.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
