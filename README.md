# Проект “Обмен валют”

REST API для описания валют и обменных курсов. Позволяет просматривать и редактировать списки валют и обменных курсов, и
совершать расчёт конвертации произвольных сумм из одной валюты в другую.

## Создание БД

создайте бд в SQL Shell
CREATE DATABASE currency_exchange_db OWNER пользователь;

## Деплой

Создайте .env файл в папке backend:
```properties
POSTGRES_USER=пользователь бд postgres
POSTGRES_PASSWORD=123123
POSTGRES_DB=currency_exchange_db
HOST_DB=localhost
PORT_DB=5432

REDIS_HOST=localhost
# Макс. количество запросов в REDIS_SECONDS
REDIS_TIMES=50
REDIS_SECONDS=86400

# Макс. количество цифр после запятой
DB_SCALE=6
# Макс. количество цифр
DB_INTEGER_DIGITS=15
```

### Linux (Ubuntu)
1. Установите Docker в систему
2. Перейдите в  /CurrencyExchangeFastAPI
    ```shell
    cd CurrencyExchangeFastAPI
   git pull https://github.com/mandalorianec/CurrencyExchangeFastAPI.git
    ```
3. Создайте .env файл в папке backend:
    ```properties
    POSTGRES_USER=пользователь бд postgres
    POSTGRES_PASSWORD=123123
    POSTGRES_DB=currency_exchange_db
    HOST_DB=localhost
    PORT_DB=5432
    
    REDIS_HOST=redis
    # Макс. количество запросов в REDIS_SECONDS
    REDIS_TIMES=50
    REDIS_SECONDS=86400
    
    # Макс. количество цифр после запятой
    DB_SCALE=6
    # Макс. количество цифр
    DB_INTEGER_DIGITS=15
    ```
4. Пропишите docker compose up --build
