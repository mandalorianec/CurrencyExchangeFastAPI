from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas import CurrencyCodepair, _validate_different_codes
from app.service.currency_service import CurrencyService
from app.service.exchange_service import ExchangeService
from app.service.exchangerate_service import ExchangeRateService

ExchangeRateServiceDep = Annotated[ExchangeRateService, Depends(ExchangeRateService)]
ExchangeServiceDep = Annotated[ExchangeService, Depends(ExchangeService)]
CurrencyServiceDep = Annotated[CurrencyService, Depends(CurrencyService)]

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _divide_codepair(codepair: CurrencyCodepair) -> tuple[str, str]:
    codepair = str(codepair).strip().upper()
    base_code = codepair[:3]
    target_code = codepair[3:]

    _validate_different_codes(base_code, target_code)

    return base_code, target_code
