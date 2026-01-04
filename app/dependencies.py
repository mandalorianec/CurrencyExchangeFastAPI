from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
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


def get_currency_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> CurrencyRepository:
    return CurrencyRepository(session)


def get_currency_service(rep: Annotated[CurrencyRepository, Depends(get_currency_repository)]) -> CurrencyService:
    return CurrencyService(rep)


def get_exchangerate_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ExchangeRateRepository:
    return ExchangeRateRepository(session)


def get_exchangerate_service(
    exchangerate_rep: Annotated[ExchangeRateRepository, Depends(get_exchangerate_repository)],
    currency_rep: Annotated[CurrencyRepository, Depends(get_currency_repository)],
) -> ExchangeRateService:
    return ExchangeRateService(exchangerate_rep=exchangerate_rep, currency_rep=currency_rep)


def get_exchange_service(
    exchangerate_service: Annotated[ExchangeRateService, Depends(get_exchangerate_service)],
) -> ExchangeService:
    return ExchangeService(exchangerate_service)


ExchangeRateServiceDep = Annotated[ExchangeRateService, Depends(get_exchangerate_service)]
ExchangeServiceDep = Annotated[ExchangeService, Depends(get_exchange_service)]
CurrencyServiceDep = Annotated[CurrencyService, Depends(get_currency_service)]
