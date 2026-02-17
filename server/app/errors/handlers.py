import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.errors.base import ApplicationError

logger = logging.getLogger(__name__)


async def application_error_handler(request: Request, exc: ApplicationError):
    if not exc.is_operational:
        logger.exception("Non-operational error", exc_info=exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "metadata": exc.metadata,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
            }
        },
    )
