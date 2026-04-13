from typing import Any

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: Any | None = None):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details},
        )


def not_found(resource: str = "Resource") -> AppError:
    return AppError(status.HTTP_404_NOT_FOUND, "not_found", f"{resource} not found")


def unauthorized(message: str = "Invalid or missing credentials") -> AppError:
    return AppError(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)


def conflict(message: str) -> AppError:
    return AppError(status.HTTP_409_CONFLICT, "conflict", message)


def bad_request(message: str) -> AppError:
    return AppError(status.HTTP_400_BAD_REQUEST, "bad_request", message)
