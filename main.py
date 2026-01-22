import logging

import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka

from app.app_factory import create_app
from app.dependencies import MyProvider

logger = logging.getLogger(__name__)

app = create_app()
container = make_async_container(MyProvider())
setup_dishka(container, app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
