from app.errors.handlers import application_error_handler, unhandled_exception_handler
from app.errors.base import ApplicationError
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.endpoints import patient, practitioner, encounter
from app.core.database import engine, Base
from app.core.config import settings
from app.core.redis import redis_client
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🟢 Starting up the application")

    # Startup event to create tables if they don't exist (for demo purposes)
    # In production, use Alembic migrations.
    if settings.ENVIRONMENT == "development":
        logger.info("Creating database tables (development mode)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured.")

    try:
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error("Failed to connect to Redis.", exc_info=e)

    yield

    logger.info("🔴 Shutting down application...")

    await engine.dispose()
    logger.info("Database engine disposed.")


app = FastAPI(title="FastAPI Server", lifespan=lifespan)

# app.add_exception_handler(ApplicationError, application_error_handler)
# app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(patient.router, prefix="/patient", tags=["Patient"])
app.include_router(practitioner.router, prefix="/practitioner", tags=["Practitioner"])
app.include_router(encounter.router, prefix="/encounter", tags=["Encounter"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
