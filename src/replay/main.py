import logging

from fastapi import FastAPI

from replay.config import APP_NAME
from replay.logging import setup_logging
from replay.routes import router

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME)

app.include_router(router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}