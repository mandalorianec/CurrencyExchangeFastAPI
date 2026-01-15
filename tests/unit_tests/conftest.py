import pytest
from dishka import Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import Request, Response
from fastapi_limiter.depends import RateLimiter
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.database import Base
from app.dependencies import MyProvider
from main import app


class MockMyProvider(MyProvider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)


@pytest.fixture
async def client():
    mock_container = make_async_container(MockMyProvider())
    engine = await mock_container.get(AsyncEngine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    setup_dishka(mock_container, app)
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    yield client
    await mock_container.close()


@pytest.fixture(autouse=True)
def disable_rate_limiter(monkeypatch):
    async def mock_call(self, request: Request, response: Response):
        return

    monkeypatch.setattr(RateLimiter, "__call__", mock_call)


@pytest.fixture
def anyio_backend():
    return "asyncio"
