import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, contains_eager, joinedload

from app.database import get_session
from app.exceptions import ExchangeRateAlreadyExistsError, ExchangeRateNotFoundError
from app.models.currency import Currency
from app.models.exchangerate import ExchangeRate
from app.schemas import ExchangeRateSchema

logger = logging.getLogger(__name__)


class ExchangeRateRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self._session = session

    async def get_all(self) -> list[ExchangeRate]:
        exchangerates = await self._session.execute(
            select(ExchangeRate).options(
                joinedload(ExchangeRate.base_currency), joinedload(ExchangeRate.target_currency)
            )
        )
        result = exchangerates.scalars().all()
        return list(result)

    async def add_exchangerate(self, exchangerate: ExchangeRateSchema, base_id: int, target_id: int) -> None:
        rate = exchangerate.rate
        db_object = ExchangeRate(base_currency_id=base_id, target_currency_id=target_id, rate=rate)
        self._session.add(db_object)
        try:
            await self._session.commit()
        except IntegrityError as e:
            logger.exception("Не удалось добавить exchangerate")
            await self._session.rollback()
            raise ExchangeRateAlreadyExistsError from e

    async def get_exchangerate_by_codepair(self, base_code: str, target_code: str) -> ExchangeRate:
        base_aliase = aliased(Currency)
        target_aliase = aliased(Currency)
        exchangerate = await self._session.execute(
            select(ExchangeRate)
            .join(base_aliase, ExchangeRate.base_currency_id == base_aliase.id)
            .join(target_aliase, ExchangeRate.target_currency_id == target_aliase.id)
            .options(
                contains_eager(ExchangeRate.base_currency, alias=base_aliase),
                contains_eager(ExchangeRate.target_currency, alias=target_aliase),
            )
            .filter(base_aliase.code == base_code, target_aliase.code == target_code)
        )
        result = exchangerate.scalars().first()
        if result is None:
            raise ExchangeRateNotFoundError
        return result
