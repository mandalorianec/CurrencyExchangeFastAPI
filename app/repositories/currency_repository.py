import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.exceptions import CurrencyAlreadyExistsError, CurrencyNotFoundError
from app.models.currency import Currency
from app.schemas import CurrencySchema

logger = logging.getLogger(__name__)


class CurrencyRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self._session = session

    async def get_all(self) -> list[Currency]:
        currencies = await self._session.execute(select(Currency))
        result = currencies.scalars().all()
        return list(result)

    async def get_currency_by(self, code: str) -> Currency:
        currency = await self._session.execute(
            select(Currency).filter(Currency.code == code)
        )
        result = currency.scalars().first()
        if result is None:
            raise CurrencyNotFoundError
        return result

    async def add_currency(self, currency: CurrencySchema) -> None:
        db_object = Currency(name=currency.name, code=currency.code, sign=currency.sign)
        self._session.add(db_object)
        try:
            await self._session.commit()
        except IntegrityError as e:
            logger.error("Не удалось добавить валюту из-за проблем с БД")
            await self._session.rollback()
            raise CurrencyAlreadyExistsError from e
