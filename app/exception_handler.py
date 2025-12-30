from fastapi import status
from fastapi.responses import JSONResponse


async def validation_exception_handler(request, exc):
    for error in exc.errors():
        if error["type"] == "missing":
            return JSONResponse(
                content={
                    "message": f"Отсутствует нужное поле формы: {error['loc'][1]}"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if error["type"] == "string_too_long":
            return JSONResponse(
                content={
                    "message": f"Длина поля {error['loc'][1]} превышает"
                               f" допустимое значение: {error['ctx']['max_length']}"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if error["type"] == "string_too_short":
            return JSONResponse(
                content={
                    "message": f"Длина поля {error['loc'][1]} должна быть минимум: {error['ctx']['min_length']}"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if error["type"] == "string_pattern_mismatch":
            return JSONResponse(
                content={
                    "message": f"Поле {error['loc'][1]} должно состоять только из букв латинского алфавита!"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if error["type"] == "decimal_parsing":
            return JSONResponse(
                content={"message": "Введите корректное вещественное число"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if error["type"] == "value_error":
            return JSONResponse(
                content={"message": f"{str(error['ctx']['error'])}"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    return JSONResponse(
        content={"message": "Ошибка валидации"}, status_code=status.HTTP_400_BAD_REQUEST
    )


async def http_exception_handler(request, exc):
    content = {"message": exc.detail}
    return JSONResponse(content, status_code=exc.status_code)


async def ownexception_handler(reauest, exc):
    content = {"message": exc.message}
    return JSONResponse(content, status_code=exc.code)
