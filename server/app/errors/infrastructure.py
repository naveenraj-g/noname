from .base import ApplicationError


class InfrastructureError(ApplicationError):
    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(
            message,
            status_code=500,
            code="INFRASTRUCTURE_ERROR",
            cause=cause,
            is_operational=True,
        )
