import logging
from decimal import Decimal
from typing import Annotated
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from app.exceptions import ExchangeRateNotFoundError, ExchangeRateAlreadyExistsError
from app.repositories.currency_repository import CurrencyRepository
from app.repositories.exchangerate_repository import ExchangeRateRepository
from app.schemas import ConvertedExchangeRate, ExchangeRateSchema

logger = logging.getLogger(__name__)

class ExchangeRateService:
    def __init__(self,
                 exchangerate_rep: Annotated[ExchangeRateRepository, Depends(ExchangeRateRepository)],
                 currency_rep: Annotated[CurrencyRepository, Depends(CurrencyRepository)]):
        self.exchangerate_rep = exchangerate_rep
        self.currency_rep = currency_rep

    async def get_all_exchangerates(self):
        return await self.exchangerate_rep.get_all()

    async def get_exchangerate_by_codepair(self, base_code: str, target_code: str):
        exchangerate = await self.exchangerate_rep.get_exchangerate_by_codepair(base_code, target_code)
        return exchangerate

    async def update_exchangerate(self, base_code: str, target_code: str, rate: Decimal):
        try:
            exchangerate = await self.exchangerate_rep.get_exchangerate_by_codepair(base_code, target_code)
        except ExchangeRateNotFoundError:
            logger.info("Валютная пара отсутствует в базе данных")
            raise ExchangeRateNotFoundError(message="Валютная пара отсутствует в базе данных")
        exchangerate.rate = rate
        await self.exchangerate_rep.session.commit()
        return exchangerate

    async def add_exchangerate(self, exchangerate: ExchangeRateSchema, base_id: int, target_id: int):
        await self.exchangerate_rep.add_exchangerate(exchangerate, base_id, target_id)
        try:
            await self.exchangerate_rep.session.commit()
        except IntegrityError:
            logger.exception("Не удалось добавить exchangerate")
            await self.exchangerate_rep.session.rollback()
            raise ExchangeRateAlreadyExistsError
        return await self.get_exchangerate_by_codepair(
            exchangerate.base_currency_code,
            exchangerate.target_currency_code
        )

    async def get_effective_rate(self, from_: str, to: str):
        if from_ == to:
            currency = await self.currency_rep.get_currency_by(from_)
            return ConvertedExchangeRate(base_currency=currency, target_currency=currency, rate=1)
        try:
            exchange_rate = await self.exchangerate_rep.get_exchangerate_by_codepair(from_, to)
            rate = exchange_rate.rate
            base_currency = exchange_rate.base_currency
            target_currency = exchange_rate.target_currency
        except ExchangeRateNotFoundError:
            try:
                exchange_rate = await self.exchangerate_rep.get_exchangerate_by_codepair(to, from_)
                rate = 1 / exchange_rate.rate
                base_currency = exchange_rate.target_currency
                target_currency = exchange_rate.base_currency
            except ExchangeRateNotFoundError:
                usd_from = await self.exchangerate_rep.get_exchangerate_by_codepair("USD", from_)
                usd_to = await self.exchangerate_rep.get_exchangerate_by_codepair("USD", to)
                base_currency = usd_from.target_currency
                target_currency = usd_to.target_currency
                rate = usd_to.rate / usd_from.rate
        return ConvertedExchangeRate(base_currency=base_currency, target_currency=target_currency, rate=rate)