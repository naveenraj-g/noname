from app.errors.handlers import application_error_handler, unhandled_exception_handler
from app.errors.base import ApplicationError
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import api_router
from app.core.redis import redis_client
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🟢 Starting up the application")

    try:
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error("Failed to connect to Redis.", exc_info=e)

    yield

    logger.info("🔴 Shutting down application...")


app = FastAPI(title="IAM Server", lifespan=lifespan)

# app.add_exception_handler(ApplicationError, application_error_handler)
# app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
