import logging

import uvicorn

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    uvicorn.run("app.app_factory:create_app", host="0.0.0.0", port=8000, factory=True, reload=True)
