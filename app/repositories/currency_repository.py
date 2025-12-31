from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.exceptions import CurrencyNotFoundError
from app.models.currency import Currency
from app.schemas import CurrencySchema


class CurrencyRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session

    async def get_all(self) -> list[Currency]:
        currencies = await self.session.execute(select(Currency))
        result = currencies.scalars().all()
        return list(result)

    async def get_currency_by(self, code: str) -> Currency:
        currency = await self.session.execute(
            select(Currency).filter(Currency.code == code)
        )
        result = currency.scalars().first()
        if result is None:
            raise CurrencyNotFoundError
        return result

    async def add_currency(self, currency: CurrencySchema) -> None:
        db_object = Currency(name=currency.name, code=currency.code, sign=currency.sign)
        self.session.add(db_object)
