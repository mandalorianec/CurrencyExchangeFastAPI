import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, contains_eager, joinedload

from app.exceptions import ExchangeRateAlreadyExistsError, ExchangeRateNotFoundError
from app.models.currency import Currency
from app.models.exchangerate import ExchangeRate
from app.schemas import ExchangeRateSchema

logger = logging.getLogger(__name__)


class ExchangeRateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[ExchangeRate]:
        exchangerates = await self._session.execute(
            select(ExchangeRate).options(
                joinedload(ExchangeRate.base_currency), joinedload(ExchangeRate.target_currency)
            )
        )
        result = exchangerates.scalars().all()
        return list(result)

    async def update_exchangerate(self, base_code: str, target_code: str, rate: Decimal) -> None:
        try:
            exchangerate = await self.get_exchangerate_by_codepair(base_code, target_code)
            exchangerate.rate = rate
            await self._session.commit()
        except ExchangeRateNotFoundError as e:
            logger.info("Валютная пара отсутствует в базе данных")
            await self._session.rollback()
            raise ExchangeRateNotFoundError(message="Валютная пара отсутствует в базе данных") from e

    async def add_exchangerate(self, exchangerate: ExchangeRateSchema, base_id: int, target_id: int) -> None:
        rate = exchangerate.rate
        db_object = ExchangeRate(base_currency_id=base_id, target_currency_id=target_id, rate=rate)
        self._session.add(db_object)
        try:
            await self._session.commit()
        except IntegrityError as e:
            logger.exception("Не удалось добавить exchangerate. Обменный курс уже существует")
            await self._session.rollback()
            raise ExchangeRateAlreadyExistsError from e

    async def get_exchangerate_by_codepair(self, base_code: str, target_code: str) -> ExchangeRate:
        base_alias = aliased(Currency)
        target_alias = aliased(Currency)
        exchangerate = await self._session.execute(
            select(ExchangeRate)
            .join(base_alias, ExchangeRate.base_currency_id == base_alias.id)
            .join(target_alias, ExchangeRate.target_currency_id == target_alias.id)
            .options(
                contains_eager(ExchangeRate.base_currency, alias=base_alias),
                contains_eager(ExchangeRate.target_currency, alias=target_alias),
            )
            .filter(base_alias.code == base_code, target_alias.code == target_code)
        )
        result = exchangerate.scalars().first()
        if result is None:
            raise ExchangeRateNotFoundError
        return result
