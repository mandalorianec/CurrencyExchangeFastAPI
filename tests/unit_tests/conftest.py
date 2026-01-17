import pytest
from dishka import Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import Request, Response, FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_limiter.depends import RateLimiter
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.database import Base
from app.dependencies import MyProvider
from app.exception_handler import http_exception_handler, ownexception_handler, validation_exception_handler
from app.exceptions import BaseOwnException
from app.routers.currency import currency_router
from app.routers.exchangerate import exchange_rate_router
from app.service.exchange_service import ExchangeService
from app.routers.exchange import exchange_router


def create_app() -> FastAPI:
    app = FastAPI()
    # Подключаем собственные обработчики ошибок
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(BaseOwnException, ownexception_handler)

    # Подключаем свои роутеры
    app.include_router(exchange_router)
    app.include_router(exchange_rate_router)
    app.include_router(currency_router)
    return app


@pytest.fixture
def test_app() -> FastAPI:
    return create_app()


class MockMyProvider(MyProvider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)


@pytest.fixture
async def client(test_app, container):
    client = AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test")
    yield client

@pytest.fixture
async def exchange_service(container, test_app):
    setup_dishka(container, test_app)
    async with container() as mini_container:
        service = await mini_container.get(ExchangeService)
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


@pytest.fixture(autouse=True)
def disable_rate_limiter(monkeypatch):
    async def mock_call(self, request: Request, response: Response):
        return

    monkeypatch.setattr(RateLimiter, "__call__", mock_call)


@pytest.fixture
def anyio_backend():
    return "asyncio"
