from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from app.schemas import ConvertedExchangeRateResponse
from app.service.exchangerate_service import ExchangeRateService


class ExchangeService:
    def __init__(self, service: Annotated[ExchangeRateService, Depends(ExchangeRateService)]):
        self.service = service

    async def convert(self, from_: str, to: str, amount: Decimal) -> ConvertedExchangeRateResponse:
        converted = await self.service.get_effective_rate(from_, to)

        response = ConvertedExchangeRateResponse(base_currency=converted.base_currency,
                                                 target_currency=converted.target_currency,
                                                 rate=converted.rate,
                                                 amount=amount,
                                                 converted_amount=converted.rate * amount
                                                 )
        return response
