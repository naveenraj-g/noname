from .base import ApplicationError


class AuthError(ApplicationError):
    def __init__(self, message: str, *, status_code=400, code="AUTH_ERROR", metadata=None):
        super().__init__(
            message,
            status_code=status_code,
            code=code,
            metadata=metadata,
            is_operational=True,
        )


class InvalidCredentialsError(AuthError):
    def __init__(self):
        super().__init__(
            "Invalid email or password",
            status_code=401,
            code="INVALID_CREDENTIALS",
        )


class UserAlreadyExistsError(AuthError):
    def __init__(self):
        super().__init__(
            "An account with this email already exists",
            status_code=409,
            code="USER_ALREADY_EXISTS",
        )


class EmailNotVerifiedError(AuthError):
    def __init__(self):
        super().__init__(
            "Please verify your email address to continue",
            status_code=403,
            code="EMAIL_NOT_VERIFIED",
        )


class SessionExpiredError(AuthError):
    def __init__(self):
        super().__init__(
            "Your session has expired. Please sign in again.",
            status_code=401,
            code="SESSION_EXPIRED",
        )


class AccountNotFoundError(AuthError):
    def __init__(self):
        super().__init__(
            "Account not found",
            status_code=404,
            code="ACCOUNT_NOT_FOUND",
        )
