from fastapi import status


class BaseOwnException(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


class CurrencyNotFoundError(BaseOwnException):
    def __init__(self, message: str = "Валюта не найдена", code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(message, code)


class CurrencyAlreadyExistsError(BaseOwnException):
    def __init__(self, message: str = "Валюта с таким кодом уже существует", code: int = status.HTTP_409_CONFLICT):
        super().__init__(message, code)


class ExchangeRateNotFoundError(BaseOwnException):
    def __init__(self, message: str = "Обменный курс для пары не найден", code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(message, code)


class ExchangeRateAlreadyExistsError(BaseOwnException):
    def __init__(
        self, message: str = "Валютная пара с таким кодом уже существует", code: int = status.HTTP_409_CONFLICT
    ):
        super().__init__(message, code)

