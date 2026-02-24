from app.errors.handlers import application_error_handler, unhandled_exception_handler
from app.errors.base import ApplicationError
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.routers import api_router
from app.core.config import settings
from app.core.redis import redis_client
from app.core.logging import setup_logging, get_logger
from app.di.container import Container
from app.auth.dependencies import get_current_principal


setup_logging()
logger = get_logger(__name__)

container = Container()
db = container.core.database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🟢 Starting up the application")

    # Startup event to create tables if they don't exist (for demo purposes)
    # In production, use Alembic migrations.
    if settings.ENVIRONMENT == "development":
        logger.info("Creating database tables (development mode)...")
        await db.connect()
        logger.info("Database tables ensured.")

    try:
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error("Failed to connect to Redis.", exc_info=e)

    yield

    logger.info("🔴 Shutting down application...")
    await db.disconnect()

    logger.info("Database engine disposed.")


app = FastAPI(title="FHIR Server", lifespan=lifespan)
app.container = container

# app.add_exception_handler(ApplicationError, application_error_handler)
# app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(
    api_router, prefix="/api/fhir/v1", dependencies=[Depends(get_current_principal)]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
