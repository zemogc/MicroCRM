from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions keeping their detail and headers (WWW-Authenticate, Retry-After...)"""
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "path": request.url.path
        },
        headers=getattr(exc, "headers", None)
    )

def _clean_validation_message(message: str) -> str:
    # Pydantic prefixes custom validator errors with "Value error, "
    return message.removeprefix("Value error, ")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors (422)"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": _clean_validation_message(error["msg"]),
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            # Readable summary so clients can show it directly
            "detail": "; ".join(e["message"] for e in errors) or "Invalid request data",
            "errors": errors,
            "path": request.url.path
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors without exposing SQL details"""
    logger.error(f"Database error on {request.url}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "detail": "An error occurred while processing your request",
            "path": request.url.path
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred",
            "path": request.url.path
        }
    )
