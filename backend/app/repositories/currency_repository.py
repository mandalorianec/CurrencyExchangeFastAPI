from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_session
from app.exceptions import CurrencyNotFoundError
from app.schemas import CurrencySchema
from app.models.currency import Currency


class CurrencyRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session

    async def get_all(self):
        currencies = await self.session.execute(select(Currency))
        result = currencies.scalars().all()
        return result

    async def get_currency_by(self, code: str):
        currency = await self.session.execute(select(Currency).filter(Currency.code == code))
        result = currency.scalars().first()
        if result is None:
            raise CurrencyNotFoundError
        return result

    async def add_currency(self, currency: CurrencySchema):
        db_object = Currency(name=currency.name, code=currency.code, sign=currency.sign)
        self.session.add(db_object)