# Проект “Обмен валют”

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=flat&logo=nginx&logoColor=white)

REST API для описания валют и обменных курсов. Позволяет просматривать и редактировать списки валют и обменных курсов, и
совершать расчёт конвертации произвольных сумм из одной валюты в другую.

## Технологии

- Python 3.12
- FastAPI
- pydantic
- sqlalchemy
- alembic
- postgres
- redis
- fastapi-limiter
- pytest
- nginx
- docker

## Деплой на Linux(Ubuntu)

1. Установите Docker и docker compose в систему
2. Перейдите в /CurrencyExchangeFastAPI
    ```sh
   git clone https://github.com/mandalorianec/CurrencyExchangeFastAPI.git
   cd CurrencyExchangeFastAPI
    ```
3. Создайте .env файл рядом с Dockerfile:
    ```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=123123
    POSTGRES_DB=currency_exchange_db
    HOST_DB=postgres
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
4. Настройте Linux:
   ```shell
   ufw allow OpenSSH
   ufw allow 80/tcp
   ufw enable
   
   ufw allow from 172.17.0.0/16
   ```
5. Пропишите: 
   ```shell
   docker compose up --build -d
   ```
6. Приложение доступно по IP вашего VPS.
7. Документация (Swagger) доступна по http://ip/docs
