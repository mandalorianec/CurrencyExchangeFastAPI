import logging
from typing import Annotated
from sqlalchemy.exc import IntegrityError

from fastapi import Depends

from app.exceptions import CurrencyAlreadyExistsError
from app.repositories.currency_repository import CurrencyRepository
from app.schemas import CurrencySchema

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self, rep: Annotated[CurrencyRepository, Depends(CurrencyRepository)]):
        self.rep = rep

    async def get_all_currencies(self):
        return await self.rep.get_all()

    async def get_currency_by(self, code: str):
        currency = await self.rep.get_currency_by(code)
        return currency

    async def add_currency(self, currency: CurrencySchema):
        await self.rep.add_currency(currency)
        try:
            await self.rep.session.commit()
        except IntegrityError:
            logger.error("Не удалось добавить валюту из-за проблем с БД")
            await self.rep.session.rollback()
            raise CurrencyAlreadyExistsError
        created_currency = await self.rep.get_currency_by(currency.code)
        return created_currency
