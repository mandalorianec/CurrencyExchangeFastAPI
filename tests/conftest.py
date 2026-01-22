import pytest
from dishka import Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, Response
from fastapi_limiter.depends import RateLimiter
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.app_factory import create_app
from app.database import Base
from app.dependencies import MyProvider
from app.repositories.currency_repository import CurrencyRepository
from app.repositories.exchangerate_repository import ExchangeRateRepository
from app.schemas import CurrencySchema, ExchangeRateSchema
from app.service.currency_service import CurrencyService
from app.service.exchange_service import ExchangeService


@pytest.fixture
def test_app() -> FastAPI:
    return create_app()


class MockMyProvider(MyProvider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)


@pytest.fixture()
async def client(test_app, container):
    client = AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test")
    yield client


@pytest.fixture
async def exchange_service(container, test_app):
    async with container() as mini_container:
        service = await mini_container.get(ExchangeService)
        yield service


@pytest.fixture
async def currency_service(container, test_app):
    async with container() as mini_container:
        service = await mini_container.get(CurrencyService)
        yield service


@pytest.fixture
async def container(test_app):
    mock_container = make_async_container(MockMyProvider())
    engine = await mock_container.get(AsyncEngine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    setup_dishka(mock_container, test_app)
    yield mock_container
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await mock_container.close()


@pytest.fixture
async def usd_currency(container):
    async with container() as mini_container:
        rep = await mini_container.get(CurrencyRepository)
        usd = CurrencySchema(name="US Dollar", code="USD", sign="$")
        await rep.add_currency(usd)
        usd = await rep.get_currency_by("USD")
        yield usd


@pytest.fixture
async def rub_currency(container):
    async with container() as mini_container:
        rep = await mini_container.get(CurrencyRepository)
        rub = CurrencySchema(name="Russian Ruble", code="RUB", sign="R")
        await rep.add_currency(rub)
        rub = await rep.get_currency_by("RUB")
        yield rub


@pytest.fixture
async def eur_currency(container):
    async with container() as mini_container:
        rep = await mini_container.get(CurrencyRepository)
        eur = CurrencySchema(name="Euro", code="EUR", sign="€")
        await rep.add_currency(eur)
        eur = await rep.get_currency_by("EUR")
        yield eur


@pytest.fixture
async def exchange_rate_usd_rub(container, usd_currency, rub_currency):
    async with container() as mini_container:
        rep = await mini_container.get(ExchangeRateRepository)
        rate = ExchangeRateSchema(baseCurrencyCode="USD", targetCurrencyCode="RUB", rate=77.75)
        await rep.add_exchangerate(rate, usd_currency.id, rub_currency.id)
        yield rate


@pytest.fixture
async def exchange_rate_usd_eur(container, usd_currency, eur_currency):
    async with container() as mini_container:
        rep = await mini_container.get(ExchangeRateRepository)
        rate = ExchangeRateSchema(baseCurrencyCode="USD", targetCurrencyCode="EUR", rate=0.85)
        await rep.add_exchangerate(rate, usd_currency.id, eur_currency.id)
        yield rate


@pytest.fixture(autouse=True)
def disable_rate_limiter(monkeypatch):
    async def mock_call(self, request: Request, response: Response):
        return

    monkeypatch.setattr(RateLimiter, "__call__", mock_call)


@pytest.fixture
def anyio_backend():
    return "asyncio"
