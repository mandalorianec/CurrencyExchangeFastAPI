from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.repositories.currency_repository import CurrencyRepository
from app.repositories.exchangerate_repository import ExchangeRateRepository
from app.schemas import CurrencyCodepair, _validate_different_codes
from app.service.currency_service import CurrencyService
from app.service.exchange_service import ExchangeService
from app.service.exchangerate_service import ExchangeRateService


def _divide_codepair(codepair: CurrencyCodepair) -> tuple[str, str]:
    codepair = str(codepair).strip().upper()
    base_code = codepair[:3]
    target_code = codepair[3:]

    _validate_different_codes(base_code, target_code)

    return base_code, target_code


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(settings.database_url)

    @provide(scope=Scope.APP)
    async def get_async_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as new_session:
            yield new_session

    @provide(scope=Scope.REQUEST)
    def get_currency_repository(self, session: AsyncSession) -> CurrencyRepository:
        return CurrencyRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_currency_service(self, rep: CurrencyRepository) -> CurrencyService:
        return CurrencyService(rep)

    @provide(scope=Scope.REQUEST)
    def get_exchangerate_repository(self, session: AsyncSession) -> ExchangeRateRepository:
        return ExchangeRateRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_exchangerate_service(
        self, exchangerate_rep: ExchangeRateRepository, currency_rep: CurrencyRepository
    ) -> ExchangeRateService:
        return ExchangeRateService(exchangerate_rep=exchangerate_rep, currency_rep=currency_rep)

    @provide(scope=Scope.REQUEST)
    def get_exchange_service(self, exchangerate_service: ExchangeRateService) -> ExchangeService:
        return ExchangeService(exchangerate_service)
