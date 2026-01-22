import logging

import uvicorn

from app.app_factory import create_app

logger = logging.getLogger(__name__)

app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
