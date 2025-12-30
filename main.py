import uvicorn
from app.exception_handler import validation_exception_handler, http_exception_handler, ownexception_handler
from app.exceptions import BaseOwnException
from app.lifespan import lifespan
from app.routers.exchange import exchange_router
from app.routers.exchangerate import exchange_rate_router
from app.routers.currency import currency_router
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем собственные обработчики ошибок
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(BaseOwnException, ownexception_handler)

# Подключаем свои роутеры
app.include_router(exchange_router)
app.include_router(exchange_rate_router)
app.include_router(currency_router)


@app.get("/", tags=["Перенаправление"])
async def root():
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
