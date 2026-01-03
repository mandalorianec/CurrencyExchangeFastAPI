from decimal import Decimal
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer, model_validator

from app.config import settings


def _pre_validate_code(value: str) -> str:
    value = str(value).strip().upper()
    return value


def _after_validate_code(value: str) -> str:
    if len(value) != 3:
        raise ValueError("Код валюты отсутствует в адресе")
    if not value.isalpha():
        raise ValueError("Можно использовать только буквы для задания кода валюты")

    return value


def _round_decimal(value: Decimal) -> Decimal:
    return Decimal(f"{value:.6f}")


def _after_validate_decimal(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("Число должно быть больше или равно 0")

    if value < Decimal(10) ** -settings.db_scale:
        raise ValueError("Слишком маленькое число.")

    if int(value.normalize().as_tuple().exponent) < -settings.db_scale:
        raise ValueError("Число знаков после запятой не должно превышать {settings.db_scale}")
    limit = Decimal(10) ** settings.db_integer_digits
    if value >= limit:
        raise ValueError("Слишком большое число. Максимум {settings.db_integer_digits} целых чисел")

    return value


def _pre_validate_decimal(value: Decimal) -> str:
    rate = str(value).strip().replace(",", ".")
    if rate.count(".") > 1:
        raise ValueError("Курс должен содержать не более одной точки")
    return rate


def _to_camel(field: str) -> str:
    return "".join(word.capitalize() for word in field.split("_"))


def _to_lower_camel(field: str) -> str:
    if len(field) > 0:
        up_camel_string = _to_camel(field)
        return up_camel_string[0].lower() + up_camel_string[1:]
    return field.lower()


def _is_valid_codepair(codepair: str) -> str:
    codepair = codepair.strip().upper()
    if len(codepair) != 6 or not codepair.isalpha():
        raise ValueError("Коды валют пары отсутствуют в адресе")
    return codepair


def _validate_different_codes(base_code: str, target_code: str) -> None:
    if base_code == target_code:
        raise ValueError("Нельзя добавить курс для двух одинаковых валют")


CurrencyCode = Annotated[str, BeforeValidator(_pre_validate_code), AfterValidator(_after_validate_code)]
RoundedDecimal = Annotated[
    Decimal, AfterValidator(_round_decimal), PlainSerializer(lambda x: float(x), return_type=float)
]
InputDecimal = Annotated[Decimal, BeforeValidator(_pre_validate_decimal), AfterValidator(_after_validate_decimal)]
CurrencyCodepair = Annotated[str, AfterValidator(_is_valid_codepair)]


class IdMixin(BaseModel):
    id: int = Field(examples=[1])


class CurrencySchema(BaseModel):
    name: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z ]+$", examples=["US Dollar"])
    code: CurrencyCode = Field(examples=["USD"])
    sign: str = Field(min_length=1, max_length=10, examples=["$"])

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class CurrencyResponse(CurrencySchema, IdMixin):
    model_config = ConfigDict(from_attributes=True)


class ExchangeRateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=_to_lower_camel)

    base_currency_code: CurrencyCode
    target_currency_code: CurrencyCode
    rate: InputDecimal = Field(examples=[123.4])

    @model_validator(mode="after")
    def validate_codes(self) -> Self:
        _validate_different_codes(self.base_currency_code, self.target_currency_code)
        return self


class ExchangeRateResponse(BaseModel):
    id: int
    base_currency: CurrencyResponse
    target_currency: CurrencyResponse
    rate: RoundedDecimal = Field(examples=[123.4])

    model_config = ConfigDict(alias_generator=_to_lower_camel, populate_by_name=True)


class ConvertedExchangeRate(BaseModel):
    base_currency: CurrencyResponse
    target_currency: CurrencyResponse
    rate: Decimal


class ConvertedExchangeRateResponse(ConvertedExchangeRate):
    rate: RoundedDecimal = Field(examples=[1.2])
    amount: RoundedDecimal = Field(examples=[10])
    converted_amount: RoundedDecimal = Field(examples=[12])

    model_config = ConfigDict(alias_generator=_to_lower_camel, populate_by_name=True)


class ApiErrorSchema(BaseModel):
    message: str
