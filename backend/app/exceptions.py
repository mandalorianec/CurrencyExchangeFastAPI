from fastapi import status


class BaseOwnException(Exception): pass


class CurrencyNotFoundError(BaseOwnException):
    def __init__(self, message="Валюта не найдена", code=status.HTTP_404_NOT_FOUND):
        self.message = message
        self.code = code


class CurrencyAlreadyExistsError(BaseOwnException):
    def __init__(self, message="Валюта с таким кодом уже существует", code=status.HTTP_409_CONFLICT):
        self.message = message
        self.code = code


class ExchangeRateNotFoundError(BaseOwnException):
    def __init__(self, message="Обменный курс для пары не найден", code=status.HTTP_404_NOT_FOUND):
        self.message = message
        self.code = code


class ExchangeRateAlreadyExistsError(BaseOwnException):
    def __init__(self, message="Валютная пара с таким кодом уже существует", code=status.HTTP_409_CONFLICT):
        self.message = message
        self.code = code
